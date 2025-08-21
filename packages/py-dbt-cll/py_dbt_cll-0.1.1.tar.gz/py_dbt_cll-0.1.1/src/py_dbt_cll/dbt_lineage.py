"""
dbt_lineage.py
----------------
Extracts column-level lineage from dbt SQL models using sqlglot.
Provides utilities to expand SELECT * and trace column origins for dbt manifest resources.
"""

import json

import sqlglot
import sqlglot.lineage
from sqlglot import Expression, exp
from sqlglot.errors import ParseError


def log(message: str, debug: bool, *args):
    """
    Utility function to log messages if debug mode is enabled.
    """
    if debug:
        print(message, *args)


def find_selects_in_execution_order(
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


def expand_select_star(tree, manifest, debug=False) -> exp.Expression:
    """
    Expand all SELECT * statements in the given SQLGlot expression tree.
    This function replaces SELECT * with the actual columns from the CTE or model
    and updates the expressions in the tree accordingly.
    """

    try:

        log("==" * 40, debug)
        log("Expanding select star in CTEs and main select", debug)
        log("==" * 40, debug)

        # Run it
        selects = find_selects_in_execution_order(tree)

        for node in selects:
            from_node = node.args.get("from")

            if not from_node:
                log("--" * 40, debug)
                log("No FROM node found, skipping", debug)
                log("--" * 40, debug)
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

            log("--" * 40, debug)
            log(f"Schema name: {schema_name}", debug)
            log(f"Table name: {table_name}", debug)
            log(f"Comes from subquery: {comes_from_subquery}", debug)
            log(f"From subquery: {from_subquery}", debug)
            log(
                f"Expressions: {[expr.sql(pretty=True) for expr in node.expressions]}",
                debug,
            )
            log("--" * 40, debug)

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
                        log(f"* comes from subquery: {from_subquery}", debug)
                        log("--" * 40, debug)
                        log("get referenced cte columns", debug)
                        subquery_columns_expr = from_node.this.find(
                            exp.Select
                        ).expressions

                        for col_expr in subquery_columns_expr:
                            log(f"Add column: {col_expr.alias_or_name}", debug)
                            new_expressions.append(
                                exp.Column(
                                    this=exp.Identifier(this=col_expr.alias_or_name),
                                    table=exp.Identifier(this=from_subquery),
                                )
                            )
                    elif cte:
                        log(f"* comes from CTE: {cte.alias_or_name}", debug)
                        log("--" * 40, debug)
                        log("get referenced cte columns", debug)

                        cte_columns_expr = cte.this.find(exp.Select).expressions
                        for col_expr in cte_columns_expr:
                            log(f"Add column: {col_expr.alias_or_name}", debug)
                            new_expressions.append(
                                exp.Column(
                                    this=exp.Identifier(this=col_expr.alias_or_name),
                                    table=exp.Identifier(this=cte.alias_or_name),
                                )
                            )

                    else:
                        log(f"* comes from model: {table_name}", debug)
                        log("--" * 40, debug)
                        log(f"Search manifest for table: {expr_table_ref}", debug)
                        model = [m for m in manifest if m["name"] == table_name]
                        if model:
                            log(f"Expanding star select for table {table_name}", debug)
                            for model_col in model[0].get("columns", []):
                                log(f"Add model column: {model_col}", debug)
                                new_expressions.append(
                                    exp.Column(this=exp.Identifier(this=model_col))
                                )

                            if model[0]["type"] == "source":

                                log(
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
                            log(
                                f"Model {table_name} not found in manifest, skipping star expansion",
                                debug,
                            )

                else:
                    log("is not *, keeping expression as is", debug)
                    new_expressions.append(expr)
            if new_expressions:
                log(".." * 40, debug)
                log("Updating node with new expressions", debug)
                log(
                    f"Expressions: {[e.sql(pretty=True) for e in new_expressions]}",
                    debug,
                )
                log(".." * 40, debug)
                node.set("expressions", new_expressions)
            else:
                log(".." * 40, debug)
                log("No new expressions for node, keeping as is", debug)
                log(".." * 40, debug)

        return tree

    except ParseError as e:
        print(f"Error expanding select star: {e}")
        return tree


def extract_manifest(manifest) -> list[dict]:
    """
    Extract relevant information from the dbt manifest.
    """

    ressources = []

    for resource in (manifest.get("sources", {}) | manifest.get("nodes", {})).values():

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


def extract_column_lineage(tree, column, dialect) -> list[dict] | None:
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
    sql, columns, manifest, dialect="tsql", debug=False
) -> dict[str, list[str]] | None:
    """
    Extract column lineage from the given SQL statement.
    This function parses the SQL, expands SELECT * statements, and extracts lineage for specified columns.
    """

    log("--" * 40, debug)
    log("🏓 Extracting column lineage", debug)
    log("--" * 40, debug)

    tree = sqlglot.parse_one(sql, read=dialect)

    log("✅ Parsed SQL successfully", debug)

    get_from = list(tree.find_all(exp.From))

    if not get_from:
        log("⚠️  No FROM clause found in the SQL statement.", debug)
        return None

    tree = expand_select_star(tree, manifest=manifest, debug=debug)

    log("✅ Replaced star selects successfully", debug)

    ccl = {}

    success = True

    for column_to_check in columns:
        col_linage = extract_column_lineage(tree, column_to_check, dialect)

        if not col_linage:
            success = False
            log(f"⚠️  No lineage found for column: {column_to_check}", debug)
            continue

        ccl[column_to_check] = col_linage if col_linage else []

    if success:
        log("✅ All columns had lineage extracted successfully.", debug)

    return ccl


__all__ = ["extract_cll", "extract_manifest"]
