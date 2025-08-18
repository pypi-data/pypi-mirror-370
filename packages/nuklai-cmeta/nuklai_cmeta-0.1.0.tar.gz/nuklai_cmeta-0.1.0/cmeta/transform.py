from typing import Any, Dict, List
from .models import Model, Lake, Table, Column


# Compact JSON: [{"name","description","tables":[{"name","description","columns":[{"name","type","description"}]}]}]
def model_to_compact_json(model: Model) -> List[Dict[str, Any]]:
    lakes: List[Dict[str, Any]] = []
    for lake in model.lakes:
        lakes.append(
            {
                "name": lake.name,
                "description": lake.description,
                "tables": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "columns": [
                            {"name": c.name, "type": c.data_type, "description": c.description}
                            for c in t.columns
                        ],
                    }
                    for t in lake.tables
                ],
            }
        )
    return lakes


def compact_json_to_model(data: List[Dict[str, Any]]) -> Model:
    lakes: List[Lake] = []
    for lake in data:
        tables: List[Table] = []
        for t in lake.get("tables", []):
            cols = [
                Column(
                    name=c["name"],
                    data_type=c.get("type", "string"),
                    description=c.get("description"),
                )
                for c in t.get("columns", [])
            ]
            tables.append(Table(name=t["name"], description=t.get("description"), columns=cols))
        lakes.append(Lake(name=lake["name"], description=lake.get("description"), tables=tables))
    return Model(lakes=lakes)


# Extended JSON: flat rows per column, verbose keys
def model_to_extended_json(model: Model) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for lake in model.lakes:
        for table in lake.tables:
            for col in table.columns:
                rows.append(
                    {
                        "columnName": col.name,
                        "columnDescription": col.description,
                        "dataType": col.data_type,
                        "sourceDescription": lake.description,
                        "sourceName": lake.name,
                        "tableDescription": table.description,
                        "tableName": table.name,
                    }
                )
    return rows


def extended_json_to_model(rows: List[Dict[str, Any]]) -> Model:
    # Reconstruct grouped structure from flat rows
    by_lake: Dict[str, Lake] = {}
    for row in rows:
        lake_name = row["sourceName"]
        lake = by_lake.get(lake_name)
        if not lake:
            lake = Lake(name=lake_name, description=row.get("sourceDescription"), tables=[])
            by_lake[lake_name] = lake

        # table
        table_name = row["tableName"]
        table = next((t for t in lake.tables if t.name == table_name), None)
        if not table:
            table = Table(name=table_name, description=row.get("tableDescription"), columns=[])
            lake.tables.append(table)

        # column
        col = Column(
            name=row["columnName"],
            data_type=row.get("dataType", "string"),
            description=row.get("columnDescription"),
        )
        table.columns.append(col)

    return Model(lakes=list(by_lake.values()))
