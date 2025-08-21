### py-dbt-cll

Python packages that extracts column lineage information from dbt models based on their metadata in the manifest file. It does not require any connection to the database and it only uses sqlGlot to extract the column level lineage information from a SQL query. Before the query is passed into sqlGlot, the query is modified with additional information from the manifest file, so that the column lineage can be accurately determined.

### Installation

You can install the package using pip:

```bash
pip install py-dbt-cll
```

### Usage

Import the module.

```bash
from py_dbt_cll.dbt_lineage import DbtCLL
```

Load your manifest file

```py
with open("tests/manifest.json", "r", encoding="utf-8") as file:
    manifest_data = json.load(file)
ccl = DbtCLL(manifest_data)

sql = """
    select *
    from (
        select *
        from ...
    ) as final
"""
columns = ["academic_year_id", "date_id"]
lineage = ccl.extract_cll(sql, columns, debug=False)
```
