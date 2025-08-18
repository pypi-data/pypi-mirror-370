import os
import guriz
from .SQL.connection import MySQL
from rich.console import Console
from typing import Any

console = Console()

def mysql_to_python(mysql_type: str) -> str:
    mysql_type = mysql_type.lower()
    if "int" in mysql_type:
        return "int"
    if "decimal" in mysql_type or "float" in mysql_type or "double" in mysql_type:
        return "float"
    if "bool" in mysql_type or "tinyint(1)" in mysql_type:
        return "bool"
    if "date" in mysql_type or "time" in mysql_type or "year" in mysql_type:
        return "datetime"
    return "str"


def pull_models(output: str = "models.py") -> bool:
    try:
        tables = MySQL.execute_select("SHOW TABLES", fetch_type='all')
        table_names = [list(t.values())[0] for t in tables]

        relations = MySQL.execute_select(f"""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                TABLE_SCHEMA = DATABASE()
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """, fetch_type='all')

        relations_by_table = {}
        for rel in relations:
            table = rel["TABLE_NAME"]
            relations_by_table.setdefault(table, []).append(rel)

        with open(output, "w", encoding="utf-8") as f:
            f.write("from __future__ import annotations\n")
            f.write("from dataclasses import dataclass\n")
            f.write("from typing import ClassVar\n\n")

            for table in table_names:
                console.print(f"[bold blue]Gerando modelo para tabela:[/] {table}")
                columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')
                safe_table = table.replace("-", "_")
                class_name = safe_table.title().replace("_", "")
                f.write(f"@dataclass\n")
                f.write(f"class {class_name}:\n")
                f.write(f"    __tablename__ = '{table}'\n\n")

                for col in columns:
                    field_name = col["Field"]
                    const_name = field_name.upper().replace("-", "_")
                    f.write(f"    {const_name}: ClassVar[str] = \"{field_name}\"\n")

                f.write("\n")

        schema_path = os.path.join(os.path.dirname(guriz.__file__), "documentation", "schema.py")
        _generate_schema_py(schema_path, table_names)

        return True
    except Exception as e:
        console.print(f"[red]Erro ao puxar modelos:[/] {e}")
        return False


def _generate_schema_py(path: str, table_names: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("from pydantic import BaseModel, Field\n\n")

        for table in table_names:
            columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')
            safe_table = table.replace("-", "_")
            class_name = safe_table.title().replace("_", "")
            f.write(f"class {class_name}Response(BaseModel):\n")

            example = {}

            for col in columns:
                unsafe_field = col["Field"]
                field = unsafe_field.replace("-", "_")
                sql_type = col["Type"].lower()

                if "int" in sql_type:
                    ftype = "int"
                    example_value = 1
                elif "char" in sql_type or "text" in sql_type:
                    ftype = "str"
                    if "cpf" in field.lower():
                        example_value = "123.456.789-00"
                    elif "phone" in field.lower():
                        example_value = "(11) 99999-9999"
                    else:
                        example_value = f"example_{field}"
                elif "decimal" in sql_type or "float" in sql_type:
                    ftype = "float"
                    example_value = 1.23
                elif "bool" in sql_type:
                    ftype = "bool"
                    example_value = True
                else:
                    ftype = "str"
                    example_value = f"example_{field}"

                example[field] = example_value

                f.write(f"    {field}: {ftype} | None = None\n")

            f.write("\n    class Config:\n")
            f.write("        schema_extra = {\n")
            f.write("            \"example\": {\n")
            for k, v in example.items():
                if isinstance(v, str):
                    f.write(f"                \"{k}\": \"{v}\",\n")
                else:
                    f.write(f"                \"{k}\": {v},\n")
            f.write("            }\n")
            f.write("        }\n\n")
