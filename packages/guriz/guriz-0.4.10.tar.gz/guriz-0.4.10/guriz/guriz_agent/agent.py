from agno.agent import Agent
from agno.models.ollama import Ollama
from ..guriz_agent.context_loader import ContextLoader
from ..guriz_agent.toolset import Toolset

class GurizAgent:
    def __init__(self, mysql_client):
        self.context_loader = ContextLoader()
        self.toolset = Toolset(mysql_client)

        context_dict = self.context_loader.load()

        self.llm = Agent(
            model=Ollama(id="llama3-groq-tool-use"),
            context=context_dict,
            tools=self.toolset.get_tools(),
            memory=True,
        )
        self.dev_mode = False

    def chat(self, message: str) -> str:
        message_lower = message.lower()

        if message_lower == "dev mode on":
            self.dev_mode = True
            return "Developer mode enabled. Debug info will be shown."
        elif message_lower == "dev mode off":
            self.dev_mode = False
            return "Developer mode disabled."

        if "json" in message_lower:
            return self.llm.print_response(message, format="json", dev_mode=self.dev_mode)

        if any(keyword in message_lower for keyword in ["list", "show", "get all", "what are"]):
            return self.llm.print_response(message, format="list", dev_mode=self.dev_mode)

        return self.llm.print_response(message, dev_mode=self.dev_mode)
