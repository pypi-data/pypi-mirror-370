"""
dbt_lineage.py
----------------
Extracts column-level lineage from dbt SQL models using sqlglot.
Provides utilities to expand SELECT * and trace column origins for dbt manifest resources.
"""

import sqlglot
import sqlglot.lineage
from sqlglot import Expression, exp
from sqlglot.errors import ParseError


class DbtCLL:
    """
    Column-level lineage extraction for dbt models.
    """

    def __init__(self, manifest):
        if manifest is None:
            raise ValueError("Please provide a valid dbt manifest.")

        self.manifest = self._extract_manifest(manifest)

    def _log(self, message: str, debug: bool, *args):
        """
        Utility function to log messages if debug mode is enabled.
        """
        if debug:
            print(message, *args)

    def _extract_manifest(self, manifest) -> list[dict]:
        """
        Extract relevant information from the dbt manifest.
        """

        ressources = []

        for resource in (
            manifest.get("sources", {}) | manifest.get("nodes", {})
        ).values():

            resource_type = (
                "nodes"
                if resource.get("resource_type") == "model"
                or resource.get("resource_type") == "snapshot"
                else "source" if resource.get("resource_type") == "source" else None
            )

            if not resource_type:
                continue

            ressources.append(
                {
                    "name": (
                        resource.get("identifier", resource["name"])
                        if resource_type == "source"
                        else resource["name"]
                    ),
                    "schema": resource["schema"],
                    "columns": list(resource.get("columns", {}).keys()),
                    "type": resource_type,
                    "sql": resource.get("compiled_code", None),
                }
            )

        return ressources

    def _find_selects_in_execution_order(
        self,
        tree: exp.Expression,
    ) -> list[exp.Select]:
        """
        Given a parsed SQLGlot expression tree, return all SELECT statements
        in execution order: deepest subqueries first, outermost SELECT last.
        """
        visited = set()
        ordered_selects = []

        def visit(node: Expression):
            if isinstance(node, exp.Expression):
                # First visit all children (post-order)
                for child in node.args.values():
                    if isinstance(child, list):
                        for item in child:
                            visit(item)
                    elif isinstance(child, exp.Expression):
                        visit(child)

            if isinstance(node, exp.Select):
                node_id = id(node)
                if node_id not in visited:
                    visited.add(node_id)
                    ordered_selects.append(node)

        visit(tree)
        return ordered_selects

    def _expand_select_star(self, tree, debug=False) -> exp.Expression:
        """
        Expand all SELECT * statements in the given SQLGlot expression tree.
        This function replaces SELECT * with the actual columns from the CTE or model
        and updates the expressions in the tree accordingly.
        """

        try:

            self._log("==" * 40, debug)
            self._log("Expanding select star in CTEs and main select", debug)
            self._log("==" * 40, debug)

            # Run it
            selects = self._find_selects_in_execution_order(tree)

            for node in selects:
                from_node = node.args.get("from")

                if not from_node:
                    self._log("--" * 40, debug)
                    self._log("No FROM node found, skipping", debug)
                    self._log("--" * 40, debug)
                    continue

                schema_name = (
                    from_node.args["this"].db
                    if hasattr(from_node.args["this"], "db")
                    else None
                )
                comes_from_subquery = isinstance(from_node.args["this"], exp.Subquery)
                table_name = (
                    from_node.this.name if hasattr(from_node.this, "name") else None
                )
                from_subquery = (
                    from_node.args["this"].alias if comes_from_subquery else None
                )

                self._log("--" * 40, debug)
                self._log(f"Schema name: {schema_name}", debug)
                self._log(f"Table name: {table_name}", debug)
                self._log(f"Comes from subquery: {comes_from_subquery}", debug)
                self._log(f"From subquery: {from_subquery}", debug)
                self._log(
                    f"Expressions: {[expr.sql(pretty=True) for expr in node.expressions]}",
                    debug,
                )
                self._log("--" * 40, debug)

                new_expressions = []
                for expr in node.expressions:
                    if expr.is_star:

                        expr_table_ref = (
                            expr.args.get("table").alias_or_name
                            if expr.args.get("table")
                            else table_name
                        )
                        cte = [
                            c
                            for c in tree.find_all(exp.CTE)
                            if c.alias_or_name == expr_table_ref
                        ]
                        cte = cte[0] if cte else None

                        if comes_from_subquery:
                            self._log(f"* comes from subquery: {from_subquery}", debug)
                            self._log("--" * 40, debug)
                            self._log("get referenced cte columns", debug)
                            subquery_columns_expr = from_node.this.find(
                                exp.Select
                            ).expressions

                            for col_expr in subquery_columns_expr:
                                self._log(
                                    f"Add column: {col_expr.alias_or_name}", debug
                                )
                                new_expressions.append(
                                    exp.Column(
                                        this=exp.Identifier(
                                            this=col_expr.alias_or_name
                                        ),
                                        table=exp.Identifier(this=from_subquery),
                                    )
                                )
                        elif cte:
                            self._log(f"* comes from CTE: {cte.alias_or_name}", debug)
                            self._log("--" * 40, debug)
                            self._log("get referenced cte columns", debug)

                            cte_columns_expr = cte.this.find(exp.Select).expressions
                            for col_expr in cte_columns_expr:
                                self._log(
                                    f"Add column: {col_expr.alias_or_name}", debug
                                )
                                new_expressions.append(
                                    exp.Column(
                                        this=exp.Identifier(
                                            this=col_expr.alias_or_name
                                        ),
                                        table=exp.Identifier(this=cte.alias_or_name),
                                    )
                                )

                        else:
                            self._log(f"* comes from model: {table_name}", debug)
                            self._log("--" * 40, debug)
                            self._log(
                                f"Search manifest for table: {expr_table_ref}", debug
                            )
                            model = [
                                m for m in self.manifest if m["name"] == table_name
                            ]
                            if model:
                                self._log(
                                    f"Expanding star select for table {table_name}",
                                    debug,
                                )
                                for model_col in model[0].get("columns", []):
                                    self._log(f"Add model column: {model_col}", debug)
                                    new_expressions.append(
                                        exp.Column(this=exp.Identifier(this=model_col))
                                    )

                                if model[0]["type"] == "source":

                                    self._log(
                                        f"Found source table {table_name}, adding dbt columns",
                                        debug,
                                    )
                                    dbt_cols = [
                                        "dbt_updated_at",
                                        "dbt_valid_from",
                                        "dbt_valid_to",
                                        "dbt_scd_id",
                                    ]
                                    for dbt_col in dbt_cols:
                                        new_expressions.append(
                                            exp.Alias(
                                                this=exp.Null(),
                                                alias=exp.Identifier(this=dbt_col),
                                            )
                                        )
                            else:
                                self._log(
                                    f"Model {table_name} not found in manifest, skipping star expansion",
                                    debug,
                                )

                    else:
                        self._log("is not *, keeping expression as is", debug)
                        new_expressions.append(expr)
                if new_expressions:
                    self._log(".." * 40, debug)
                    self._log("Updating node with new expressions", debug)
                    self._log(
                        f"Expressions: {[e.sql(pretty=True) for e in new_expressions]}",
                        debug,
                    )
                    self._log(".." * 40, debug)
                    node.set("expressions", new_expressions)
                else:
                    self._log(".." * 40, debug)
                    self._log("No new expressions for node, keeping as is", debug)
                    self._log(".." * 40, debug)

            return tree

        except ParseError as e:
            print(f"Error expanding select star: {e}")
            return tree

    def _extract_column_lineage(self, tree, column, dialect) -> list[dict] | None:
        """
        Extract column lineage information from the SQLGlot expression tree.
        """
        try:
            test = sqlglot.lineage.lineage(
                column=column, sql=tree.sql(dialect=dialect), dialect=dialect
            )
        except Exception as err:
            print(f"Error in sqlglot.lineage: {err}")
            return None

        nodes = []

        for n in test.walk():
            nodes.append(
                {
                    "name": n.name,
                    "schema": (
                        n.expression.args.get("db")
                        if hasattr(n.expression, "args")
                        else None
                    ),
                    "expression": n.expression,
                    "source": n.source,
                    "downstream": [d.name for d in n.downstream],
                }
            )

        model_lineage = [n for n in nodes if not n["downstream"] and n["schema"]]

        lineage = []

        for lineage_node in model_lineage:
            target_model = lineage_node["name"].split(".")[0]
            target_col = lineage_node["name"].split(".")[1]
            lineage_target = f"{lineage_node['schema']}.{target_model}.{target_col}"

            lineage.append(lineage_target)

        return lineage

    def extract_cll(
        self, sql, columns, dialect="tsql", debug=False
    ) -> dict[str, list[str]] | None:
        """
        Extract column lineage from the given SQL statement.
        This function parses the SQL, expands SELECT * statements, and extracts lineage for specified columns.
        """

        self._log("--" * 40, debug)
        self._log("🏓 Extracting column lineage", debug)
        self._log("--" * 40, debug)

        if self.manifest is None:
            raise ValueError("Manifest is not provided or is empty.")

        tree = sqlglot.parse_one(sql, read=dialect)

        self._log("✅ Parsed SQL successfully", debug)

        get_from = list(tree.find_all(exp.From))

        if not get_from:
            self._log("⚠️  No FROM clause found in the SQL statement.", debug)
            return None

        tree = self._expand_select_star(tree, debug=debug)

        self._log("✅ Replaced star selects successfully", debug)

        ccl = {}

        success = True

        for column_to_check in columns:
            col_linage = self._extract_column_lineage(tree, column_to_check, dialect)

            if not col_linage:
                success = False
                self._log(f"⚠️  No lineage found for column: {column_to_check}", debug)
                continue

            ccl[column_to_check] = col_linage if col_linage else []

        if success:
            self._log("✅ All columns had lineage extracted successfully.", debug)

        return ccl


__all__ = ["DbtCLL"]
