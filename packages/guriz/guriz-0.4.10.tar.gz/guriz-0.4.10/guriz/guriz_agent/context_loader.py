from pathlib import Path
from dotenv import dotenv_values

class ContextLoader:
    def __init__(self, root: str = "."):
        self.root = Path(root)

    def _read_file(self, path: Path, max_size_kb: int = 100) -> str:
        if not path.exists() or not path.is_file():
            return ""
        if path.stat().st_size > max_size_kb * 1024:
            return f"# Skipped large file {path.name} ({path.stat().st_size // 1024} KB)\n"
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"# Failed to read {path.name}: {e}\n"

    def _load_directory_files(self, dir_path: Path, exts=None, max_files=100) -> dict[str, str]:
        exts = exts or [".py"]
        context = {}
        if dir_path.exists() and dir_path.is_dir():
            files = list(dir_path.rglob("*"))
            py_files = [f for f in files if f.is_file() and f.suffix in exts][:max_files]
            for f in py_files:
                rel_path = str(f.relative_to(self.root))
                context[rel_path] = self._read_file(f)
        return context

    def load(self) -> dict[str, str]:
        context = {}

        for main_file in ["models.py", "main.py", "app.py"]:
            path = self.root / main_file
            if path.exists():
                context[main_file] = self._read_file(path)

        env_path = self.root / ".env"
        if env_path.exists():
            env_vars = dotenv_values(env_path)
            env_text = "\n".join(f"{k}={v}" for k, v in env_vars.items())
            context[".env"] = env_text

        for folder in ["repositories", "routes", "controllers", "services"]:
            dir_path = self.root / folder
            folder_files = self._load_directory_files(dir_path)
            context.update(folder_files)

        if not context:
            context["empty"] = "# No context found in models.py, .env or source folders."

        return context
