import typer
import ast
import sys
import os
import importlib.util
from typing import List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from pathlib import Path
from .core import pull_models
from .guriz_agent.agent import GurizAgent
from guriz.documentation.registry import DOCUMENTED_ROUTES
from guriz.documentation.serve_docs import serve_docs
from guriz.documentation.documentate import import_controllers_from

sys.path.insert(0, os.path.abspath('.'))
app = typer.Typer()
console = Console()

@app.command("pull")
def pull(output: str = "models.py"):
    """
    Puxa tabelas do banco e gera tipagens.
    """
    console.print("[cyan]Iniciando DB pull...[/cyan]")
    success = pull_models(output)
    if success:
        console.print(f"[green]Modelos salvos em: {output}[/green]")
    else:
        console.print("[red]Erro ao gerar modelos.[/red]")

@app.command("make:project")
def make_project():
    """
    Cria uma estrutura base de projeto FastAPI.
    """
    folders = [
        "app/controllers",
        "app/services",
        "app/repositories",
        "app/jobs",
        "app/core",
        "app/dependencies"
    ]

    files = {
        "app/__init__.py": "",
        "app/router.py": (
            "from fastapi import APIRouter\n\n\n"
            "class APIRoutes:\n"
            "    def __init__(self):\n"
            "        self.router = APIRouter()\n"
            "        self.register_routes()\n\n"
            "    def register_routes(self):\n"
            "        @self.router.get('/')\n"
            "        def health():\n"
            "            return {'status': 'ok'}\n"
        ),
        "main.py": (
            "from fastapi import FastAPI\n"
            "from app.router import APIRoutes\n\n\n"
            "# Defina seu prefixo de rota aqui (ex: '/api')\n"
            "ROUTE_PREFIX = ''\n\n"
            "app = FastAPI()\n\n"
            "# Registrar rotas com prefixo (exceto health)\n"
            "routes = APIRoutes()\n"
            "app.include_router(routes.router, prefix=ROUTE_PREFIX)\n\n"
            "if __name__ == '__main__':\n"
            "    import uvicorn\n"
            "    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)\n"
        ),
        "settings.py": "# Configurações do projeto\n",
        "requirements.txt": "fastapi\nuvicorn[standard]\nrich\n",
        "Dockerfile": (
            "FROM python:3.11\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN pip install -r requirements.txt\n"
            "CMD [\"python\", \"main.py\"]\n"
        ),
        "README.md": "# Projeto FastAPI\n",
    }

    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Pasta criada:[/] {folder}")

    for file_path, content in files.items():
        file = Path(file_path)
        if not file.exists():
            file.write_text(content)
            console.print(f"[blue]✓ Arquivo criado:[/] {file_path}")
        else:
            console.print(f"[yellow]⚠ Arquivo já existe, ignorado:[/] {file_path}")

@app.command("make:repository")
def make_repository():
    """
    Gera repositórios base (CRUD) para as models do projeto.
    """
    models_path = Path("models.py")
    if not models_path.exists():
        console.print("[red]models.py não encontrado. Use `guriz pull` antes.[/red]")
        raise typer.Exit()

    with open(models_path, "r") as f:
        tree = ast.parse(f.read())

    model_names: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            model_names.append(node.name)

    if not model_names:
        console.print("[yellow]Nenhuma model encontrada em models.py[/yellow]")
        return

    console.print("[bold cyan]Models disponíveis:[/bold cyan]")
    for i, name in enumerate(model_names, 1):
        console.print(f"{i}. {name}")

    selected = Prompt.ask(
        "[bold green]Digite os números das models (separados por vírgula)[/bold green]",
        default="1"
    )
    indexes = [int(i.strip()) for i in selected.split(",") if i.strip().isdigit()]
    selected_models = [model_names[i - 1] for i in indexes if 0 < i <= len(model_names)]

    Path("app/repositories").mkdir(parents=True, exist_ok=True)

    for model in selected_models:
        file_name = f"app/repositories/{model.lower()}_repository.py"
        if Path(file_name).exists():
            overwrite = Confirm.ask(f"[yellow]Arquivo {file_name} já existe. Sobrescrever?[/yellow]", default=False)
            if not overwrite:
                continue

        with open(file_name, "w") as f:
            f.write(
    f"""from models import {model}
from guriz.repository import Repository
from typing import Any

class {model}Repository(Repository):
    def __init__(self):
        super().__init__({model}.__tablename__)

    def get_by_id(self, id_: int) -> {model} | None:
        return self.where({model}.ID, id_).get()

    def create(self, data: dict) -> int:
        return super().create(data)

    def update(self, id_: int, data: dict) -> bool:
        return super().update(id_, data=data)

    def delete(self, id: int | None = None) -> Any:
        if id is None:
            raise ValueError("id is required")
        return super().delete(id)

    def list_all(self) -> list[{model}]:
        return self.all()
"""
)
    console.print(f"[green]✓ Repository criado:[/] {file_name}")


# @app.command("run:ia")
# def run_ia():
#     """
#     Inicia o agente LLM para auxiliar no desenvolvimento com Guriz.
#     """
#     agent = GurizAgent(MySQL)
#     print("🤖 Guriz Agent iniciado! Digite 'exit' para sair.\n")

#     while True:
#         user_input = input("Você 🧠: ").strip()
#         if user_input.lower() in ("exit", "quit", "sair"):
#             break

#         response = agent.chat(user_input)
#         print("\nGuriz 🤖:\n", response, "\n")

@app.command("show:docs")
def show_docs(terminal: bool = typer.Option(False, "--terminal", help="Mostra no terminal ao invés do navegador")):
    schema_path = os.path.join(os.path.dirname(__file__), "documentation", "schema.py")
    spec = _load_schema_classes(schema_path)

    if terminal:
        table = Table(title="Documentação das Rotas")
        table.add_column("Model", style="cyan")

        for model_name, model_class in spec.items():
            config = getattr(model_class, "Config", None)
            if config is None:
                continue
            example = {}
            if hasattr(config, "json_schema_extra"):
                example = getattr(config, "json_schema_extra", {}).get("example", {})
            elif hasattr(config, "schema_extra"):
                example = getattr(config, "schema_extra", {}).get("example", {})
            table.add_row(f"{model_name}\n{example}")
        
        console.print(table)
    else:
        import guriz.documentation.serve_docs as serve_docs
        serve_docs.serve_docs()
        

def _load_schema_classes(path: str):
    spec_loader = importlib.util.spec_from_file_location("schema", path)
    if spec_loader is None or spec_loader.loader is None:
        raise ImportError(f"Cannot load module from path: {path}")

    schema_mod = importlib.util.module_from_spec(spec_loader)
    sys.modules["schema"] = schema_mod
    spec_loader.loader.exec_module(schema_mod)

    spec = {}
    for attr in dir(schema_mod):
        obj = getattr(schema_mod, attr)
        if hasattr(obj, "schema") and callable(getattr(obj, "schema")):
            spec[attr] = obj
    return spec
        
@app.command("make:env")
def make_env():
    """
    Cria um arquivo .env com variáveis de conexão ao banco.
    """
    ENV_PATH = Path(".env")
    ENV_VARS = {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "database_name"
    }
    
    if ENV_PATH.exists():
        console.print("[yellow].env já existe.[/]")
        if not Confirm.ask("Deseja sobrescrever?", default=False):
            console.print("[bold green]Abortado.[/]")
            return

    with open(ENV_PATH, "w") as f:
        for key, value in ENV_VARS.items():
            f.write(f"{key}={value}\n")

    console.print("[bold green].env criado com sucesso![/]")


def main():
    app()

if __name__ == "__main__":
    main()
