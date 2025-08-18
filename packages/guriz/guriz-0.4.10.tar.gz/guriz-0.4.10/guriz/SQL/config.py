import os
from pathlib import Path
from dotenv import load_dotenv
from rich import print

Config = None

class ConfigSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)

            env_path = Path(".env")
            if not env_path.exists():
                print("[bold yellow].env não encontrado.[/]")
                print("ℹ️  Rode [bold cyan]guriz make:env[/] para criar um arquivo de exemplo.\n")

            load_dotenv(dotenv_path=env_path if env_path.exists() else None)
            cls._instance.load_config()

        return cls._instance

    def load_config(self):
        self._initialize()

    def _initialize(self):
        self.MYSQL_HOST = os.getenv('DB_HOST')
        self.MYSQL_PORT = int(os.getenv('DB_PORT') or 3306)
        self.MYSQL_USER = os.getenv('DB_USER')
        self.MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
        self.MYSQL_DB = os.getenv('DB_NAME')

Config = ConfigSingleton()