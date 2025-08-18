import re
from pathlib import Path

class Toolset:
    def __init__(self, mysql_client, root="."):
        self.mysql = mysql_client
        self.root = Path(root)

    def get_tools(self):
        return [
            self.list_models,
            self.list_columns_from_model,
            self.generate_get_all_route,
            self.get_env_var,
            self.show_model_code
        ]

    def list_models(self) -> list[str]:
        with self.mysql.get_cursor() as cur:
            cur.execute("SHOW TABLES;")
            return [list(row.values())[0] for row in cur.fetchall()]
        
    def list_columns_from_model(self, model_name: str) -> list[str]:
        with self.mysql.get_cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {model_name};")
            return [list(row.values())[0] for row in cur.fetchall()]
        
    def generate_get_all_route(self, model_name: str) -> str:
        route = model_name.lower() + "s"
        return f"""
@app.get("/{route}")
def get_all_{route}():
    return {model_name}Repository().all()
"""

    def get_env_var(self, name: str) -> str:
        from os import getenv
        return getenv(name, "Not found")

    def show_model_code(self, model_name: str) -> str:
        models_path = self.root / "models.py"
        if not models_path.exists():
            return "File models.py not found."

        code = models_path.read_text(encoding="utf-8")
        
        pattern = rf"class {model_name}\b.*?(?=^class |\Z)"
        match = re.search(pattern, code, flags=re.S | re.M)
        if match:
            return match.group(0).strip()
        else:
            return f"Model `{model_name}` not found in models.py"
