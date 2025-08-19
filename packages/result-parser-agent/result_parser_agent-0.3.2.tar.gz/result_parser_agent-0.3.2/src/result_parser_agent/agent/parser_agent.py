from typing import Annotated, Any, TypedDict

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from loguru import logger

from ..config.settings import settings
from ..models.schema import StructuredResults
from ..prompts.agent_prompts import get_initial_message
from ..tools.langchain_tools import create_tools


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "The messages in the conversation"]
    remaining_steps: Annotated[int, "Number of remaining steps"]
    todos: Annotated[list[str], "List of tasks to complete"]
    files: Annotated[dict[str, Any], "Discovered files and their info"]
    parsing_progress: Annotated[dict[str, Any], "Progress tracking for each file"]
    extracted_data: Annotated[dict[str, Any], "Extracted metrics data"]
    raw_context: Annotated[dict[str, str], "Filepath to raw context mapping"]
    errors: Annotated[list[str], "List of errors encountered"]
    config: Annotated[Any, "Configuration object"]
    context: Annotated[dict[str, Any], "Context information"]


class ResultsParserAgent:
    def __init__(self):
        self.config = settings
        self.model = self._create_llm_model()
        self.agent = self._create_agent()
        self.structured_llm = self.model.with_structured_output(StructuredResults)

    def _create_llm_model(self) -> LanguageModelLike:
        provider = self.config.LLM_PROVIDER

        if provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=self.config.LLM_MODEL,
                api_key=self.config.GROQ_API_KEY.get_secret_value(),
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.config.LLM_MODEL,
                api_key=self.config.OPENAI_API_KEY.get_secret_value(),
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=self.config.LLM_MODEL,
                api_key=self.config.ANTHROPIC_API_KEY.get_secret_value(),
            )
        elif provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(model=self.config.LLM_MODEL)
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=self.config.LLM_MODEL,
                api_key=self.config.GOOGLE_API_KEY.get_secret_value(),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_agent(self) -> Any:

        tools = create_tools(None)
        return create_react_agent(self.model, tools, debug=self.config.AGENT_DEBUG)

    async def parse_results(
        self, input_path: str, metrics: list[str] = None
    ) -> StructuredResults:
        try:
            logger.info(f"🚀 Starting autonomous parsing of: {input_path}")
            logger.info(f"📊 Requested metrics: {metrics}")

            target_metrics = metrics

            # Log the initial configuration
            logger.info("🔧 Agent configuration:")
            logger.info(f"   - Provider: {self.config.LLM_PROVIDER}")
            logger.info(f"   - Model: {self.config.LLM_MODEL}")
            logger.info(f"   - Debug mode: {self.config.AGENT_DEBUG}")
            logger.info(f"   - Max retries: {self.config.AGENT_MAX_RETRIES}")
            logger.info(f"   - Timeout: {self.config.AGENT_TIMEOUT}s")

            initial_messages = [
                HumanMessage(content=get_initial_message(input_path, target_metrics))
            ]

            if self.config.AGENT_DEBUG:
                logger.info("🔍 Debug mode enabled - showing intermediate steps")
                logger.info(f"📁 Processing input path: {input_path}")
                logger.info(f"📊 Target metrics: {metrics}")
                logger.info(
                    f"🛠️  Available tools: {[tool.name for tool in self.agent.tools]}"
                )

            if self.config.AGENT_DEBUG:
                logger.info("🔍 Initial messages created.")
                logger.debug(
                    f"System prompt length: {len(initial_messages[0].content)}"
                )

            logger.info("🤖 Invoking agent with initial prompt...")
            runnable_config = RunnableConfig(recursion_limit=50)
            result = await self.agent.ainvoke(
                {"messages": initial_messages}, config=runnable_config
            )

            if self.config.AGENT_DEBUG:
                logger.info("🔍 Agent execution completed.")
                logger.info(f"📝 Final response: {result['output']}")

            final_agent_message = result["messages"][-1]

            if self.config.AGENT_DEBUG:
                logger.info("🔍 Processing final agent message")
                logger.info(f"📝 Message content: {final_agent_message.content}")

            if not hasattr(final_agent_message, "content"):
                logger.error("❌ Final agent message has no content")
                raise ValueError("Final agent message has no content.")

            logger.info("🔧 Converting agent response to structured format...")
            structured_result = await self.structured_llm.ainvoke(
                final_agent_message.content
            )

            if self.config.AGENT_DEBUG:
                logger.info("✅ Structured result successfully parsed.")
                logger.debug(f"Structured result: {structured_result}")

            return structured_result

        except Exception as e:
            logger.error(f"❌ Error in parse_results: {e}")
            if self.config.AGENT_DEBUG:
                import traceback

                logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")

            # Return empty results with error context
            logger.warning("🔄 Returning empty results due to error")
            return StructuredResults(iterations=[])
