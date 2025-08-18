import concurrent.futures
import os
import uuid
from datetime import datetime
from typing import Any, List, Optional

import gradio as gr
import httpx
import orjson
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from swarms import Agent
from swarms.prompts.agent_conversation_aggregator import (
    AGGREGATOR_SYSTEM_PROMPT,
)
from swarms.structs.conversation import Conversation
from swarms.utils.history_output_formatter import (
    HistoryOutputType,
    history_output_formatter,
)

from advanced_research.prompts import (
    get_orchestrator_prompt,
    get_synthesis_prompt,
)

load_dotenv()


model_name = os.getenv("WORKER_MODEL_NAME", "gpt-4.1")
max_tokens = int(os.getenv("WORKER_MAX_TOKENS", 8000))
exa_search_num_results = int(os.getenv("EXA_SEARCH_NUM_RESULTS", 2))
exa_search_max_characters = int(
    os.getenv("EXA_SEARCH_MAX_CHARACTERS", 100)
)


# Schema
class AdvancedResearchAdditionalConfig(BaseModel):
    worker_model_name: str = Field(
        default=model_name,
        description="The model name to use for the worker agent.",
    )
    worker_max_tokens: int = Field(
        default=max_tokens,
        description="The maximum number of tokens to use for the worker agent.",
    )
    exa_search_num_results: int = Field(
        default=exa_search_num_results,
        description="The number of results to return from the Exa search tool.",
    )
    exa_search_max_characters: int = Field(
        default=exa_search_max_characters,
        description="The maximum number of characters to return from the Exa search tool.",
    )


schema = AdvancedResearchAdditionalConfig()


def summarization_agent(
    model_name: str | None = "claude-3-7-sonnet-20250219",
    task: str | None = None,
    max_tokens: int | None = 1000,
    img: str = None,
    **kwargs: Any,
) -> str:
    """
    Summarization agent for generating a concise summary of research findings.
    """
    agent = Agent(
        agent_name="Report-Generator-Agent",
        system_prompt=AGGREGATOR_SYSTEM_PROMPT,
        model_name=model_name,
        max_loops=1,
        max_tokens=max_tokens,
    )
    return agent.run(task=task, img=img)


def create_json_file(data: dict, file_name: str):
    # Check if file exists and load existing data
    if os.path.exists(file_name):
        try:
            with open(file_name, "rb") as f:
                existing_data = orjson.loads(f.read())
        except Exception:
            existing_data = {}
        if isinstance(existing_data, dict):
            existing_data.update(data)
            data_to_write = existing_data
        else:
            data_to_write = data
    else:
        data_to_write = data

    with open(file_name, "wb") as f:
        f.write(
            orjson.dumps(data_to_write, option=orjson.OPT_INDENT_2)
        )


def exa_search(
    query: str,
) -> str:
    """
    Exa Web Search Tool

    This function provides advanced, natural language web search capabilities
    using the Exa.ai API. It is designed for use by research agents and
    subagents to retrieve up-to-date, relevant information from the web,
    including documentation, technical articles, and general knowledge sources.

    Features:
    - Accepts natural language queries (e.g., "Find the latest PyTorch 2.2.0 documentation on quantization APIs")
    - Returns structured, summarized results suitable for automated research workflows
    - Supports parallel execution for multiple subagents
    - Can be used to search for:
        * Official documentation (e.g., Python, PyTorch, TensorFlow, API docs)
        * Research papers and technical blogs
        * News, regulatory updates, and more

    Args:
        query (str): The natural language search query. Can be a question, a request for documentation, or a technical prompt.

    Returns:
        str: JSON-formatted string containing the search results, including summaries and key insights.

    Example usage:
        exa_search("Show me the latest Python 3.12 documentation on dataclasses")
        exa_search("Recent research on transformer architectures for vision tasks")

    Notes:
        - This tool is ideal for agents that need to quickly gather authoritative information from the web, especially official docs.
        - The Exa API is capable of extracting and summarizing content from a wide range of sources, including documentation sites, arXiv, blogs, and more.
        - For best results when searching for documentation, include the technology/library name and the specific topic or API in your query.

    """
    api_key = os.getenv("EXA_API_KEY")

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
    }

    # Payload format for Exa API (see https://docs.exa.ai/reference/search)
    payload = {
        "query": query,
        "type": "auto",
        "numResults": schema.exa_search_num_results,
        "contents": {
            "text": True,
            "summary": {
                "schema": {
                    "type": "object",
                    "required": ["answer"],
                    "additionalProperties": False,
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": (
                                "Key insights and findings from the search result"
                            ),
                        }
                    },
                }
            },
            "context": {
                "maxCharacters": schema.exa_search_max_characters
            },
        },
    }

    try:
        logger.info(
            f"[SEARCH] Executing Exa search for: {query[:50]}..."
        )

        response = httpx.post(
            "https://api.exa.ai/search",
            json=payload,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()
        json_data = response.json()

        return orjson.dumps(
            json_data, option=orjson.OPT_INDENT_2
        ).decode("utf-8")

    except Exception as e:
        logger.error(f"Exa search failed: {e}")
        return f"Search failed: {str(e)}. Please try again."


def run_agent(i: int, query: str):
    # Can also put agent judge here
    agent = Agent(
        agent_name=f"Worker-Search-Agent-{i}",
        system_prompt=get_synthesis_prompt(),
        model_name=schema.worker_model_name,
        max_loops=1,
        max_tokens=schema.worker_max_tokens,
        tools=[exa_search],
        tool_call_summary=True,
    )
    return agent.run(task=query)


def execute_worker_search_agents(
    queries: list[str],
) -> str:
    """
    Executes multiple worker search agents in sequence, each responsible for handling a single research query.

    This function is designed to automate the process of running multiple independent search agents (one per query)
    using the Swarms Agent framework. Each agent is initialized with a custom system prompt tailored to its specific
    query, and is equipped with the Exa search tool for web research. The agents are run sequentially (not in parallel),
    and their outputs are collected and returned as a list.

    Args:
        queries (list[str]):
            A list of research queries (strings) to be processed. Each query will be handled by a separate agent.

    Returns:
        str:
            A string containing the output from all worker search agents, concatenated together.

    Workflow:
        1. For each query in the input list:
            a. Instantiate a Swarms Agent with:
                - A unique agent name based on the query.
                - A system prompt generated by `get_subagent_prompt`, customized for the query, number of results, and max characters.
                - The specified model ("claude-3-7-sonnet-20250219").
                - A single loop (max_loops=1) to ensure one-shot execution.
                - A generous token limit (max_tokens=8000) to accommodate detailed outputs.
                - The Exa search tool enabled for web research.
            b. Run the agent with the query as its task.
            c. Collect the agent's output (typically a summary or structured research findings).
        2. Return a list of all agent outputs.

    Notes:
        - This function currently runs agents sequentially. For true parallelism, consider using threading or async execution.
        - The function assumes that `get_subagent_prompt` and `exa_search` are properly defined and imported.
        - The agent's output format depends on the system prompt and the agent's implementation.
        - Useful for orchestrating multi-query research tasks in advanced research pipelines.

    Example:
        >>> queries = ["What are the latest advances in quantum computing?", "Summarize recent AI safety research."]
        >>> results = execute_worker_search_agents(queries)
        >>> print(results[0])  # Output from the first query's agent
        >>> print(results[1])  # Output from the second query's agent
    """

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_agent, i, query)
            for i, query in enumerate(queries)
        ]
        results = [
            future.result()
            for future in concurrent.futures.as_completed(futures)
        ]

    return " ".join(results)


def create_director_agent(
    agent_name: str = "Director-Agent",
    model_name: str = "claude-3-7-sonnet-20250219",
    task: str | None = None,
    max_tokens: int = 8000,
    img: Optional[str] = None,
    max_loops: int = 1,
):
    """
    Create a director agent for the advanced research system.

    Args:
        agent_name (str): Name of the director agent. Default is "Director-Agent".
        model_name (str): Model to use for the agent. Default is "claude-3-7-sonnet-20250219".
        task (str | None): The research task or instruction for the agent to execute.
        max_tokens (int): Maximum number of tokens for the agent's output. Default is 8000.
        img (Optional[str]): Optional image input for the agent.
        **kwargs: Additional keyword arguments.

    Returns:
        str: The output from the director agent after running the specified task.
    """
    director_agent = Agent(
        agent_name=agent_name,
        system_prompt=get_orchestrator_prompt(),
        model_name=model_name,
        max_loops=max_loops,
        max_tokens=max_tokens,
        tools=[execute_worker_search_agents],
        tool_call_summary=True,
    )

    return director_agent.run(task=task, img=img)


def generate_id():
    return f"AdvancedResearch-{uuid.uuid4()}-time-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class AdvancedResearch:
    """
    AdvancedResearch is a high-level orchestrator for multi-agent research workflows.
    It manages the research process by coordinating director and worker agents, maintaining
    conversation history, and supporting export and output formatting.

    Attributes:
        id (str): Unique identifier for the research session.
        name (str): Name of the research system or session.
        description (str): Description of the research system or session.
        worker_model_name (str): Model name used for worker agents.
        director_agent_name (str): Name of the director agent.
        director_model_name (str): Model name used for the director agent.
        director_max_tokens (int): Maximum tokens for the director agent's output.
        output_type (HistoryOutputType): Output format for conversation history.
        max_loops (int): Number of research loops to run.
        export_on (bool): Whether to export conversation history to a JSON file.
        director_max_loops (int): Maximum loops for the director agent.
        conversation (Conversation): Conversation object to store the research dialogue.
    """

    def __init__(
        self,
        id: str = generate_id(),
        name: str = "Advanced Research",
        description: str = "Advanced Research",
        worker_model_name: str = "claude-3-7-sonnet-20250219",
        director_agent_name: str = "Director-Agent",
        director_model_name: str = "claude-3-7-sonnet-20250219",
        director_max_tokens: int = 8000,
        output_type: HistoryOutputType = "final",
        max_loops: int = 1,
        export_on: bool = False,
        director_max_loops: int = 1,
        chat_interface: bool = False,
    ):
        """
        Initialize the AdvancedResearch system.

        Args:
            id (str): Unique identifier for the research session.
            name (str): Name of the research system or session.
            description (str): Description of the research system or session.
            worker_model_name (str): Model name for worker agents.
            director_agent_name (str): Name of the director agent.
            director_model_name (str): Model name for the director agent.
            director_max_tokens (int): Maximum tokens for the director agent's output.
            output_type (HistoryOutputType): Output format for conversation history.
            max_loops (int): Number of research loops to run.
            export_on (bool): Whether to export conversation history to a JSON file.
            director_max_loops (int): Maximum loops for the director agent.
            chat_interface (bool): Whether to launch a Gradio chat interface instead of running directly.
        """
        self.id = id
        self.name = name
        self.description = description
        self.worker_model_name = worker_model_name
        self.director_agent_name = director_agent_name
        self.director_model_name = director_model_name
        self.director_max_tokens = director_max_tokens
        self.output_type = output_type
        self.max_loops = max_loops
        self.export_on = export_on
        self.director_max_loops = director_max_loops
        self.chat_interface = chat_interface

        self.conversation = Conversation(
            name=f"conversation-{self.id}"
        )

    def step(self, task: Optional[str], img: Optional[str] = None):
        """
        Execute a single research step by running the director agent on the given task.

        Args:
            task (Optional[str]): The research task to execute.
            img (Optional[str]): Optional image input.

        Returns:
            str: The output from the director agent.
        """
        # Run the director agent
        output = create_director_agent(
            agent_name=self.director_agent_name,
            model_name=self.director_model_name,
            task=task,
            max_tokens=self.director_max_tokens,
            img=img,
        )

        self.conversation.add(self.director_agent_name, output)

        return output

    def run(
        self, task: str = None, img: Optional[str] = None, **kwargs
    ):
        """
        Run the advanced research system. If chat_interface=True, launches a Gradio chat interface.
        Otherwise, runs the research system for the specified number of loops,
        maintaining conversation history across all iterations.

        Args:
            task (str, optional): The research task to execute. Not required when chat_interface=True.
            img (Optional[str]): Optional image input.
            **kwargs: Additional arguments to pass to launch_chat_interface() when using chat interface.

        Returns:
            str or list: Formatted conversation history containing all loop iterations,
                         or exports the conversation to a JSON file if export_on is True.
                         Returns None when launching chat interface.
        """
        if self.chat_interface:
            # Launch the Gradio chat interface
            self.launch_chat_interface(**kwargs)
            return None

        if task is None:
            raise ValueError(
                "task argument is required when chat_interface=False"
            )

        self.conversation.add("human", task)

        self.step(task, img)

        if self.export_on:
            create_json_file(
                data=self.conversation.return_messages_as_dictionary(),
                file_name=f"{self.id}.json",
            )
        else:
            # Return the complete conversation history from all loops
            return history_output_formatter(
                conversation=self.conversation, type=self.output_type
            )

    def batched_run(self, tasks: List[str]):
        """
        Run the research system on a batch of tasks.

        Args:
            tasks (List[str]): List of research tasks to execute.
        """
        [self.run(task) for task in tasks]

    def chat_response(
        self, message: str, history: List[List[str]]
    ) -> str:
        """
        Process a chat message and return the research response for Gradio interface.

        Args:
            message (str): The user's research question/task.
            history (List[List[str]]): Chat history from Gradio.

        Returns:
            str: The final research response from the director agent.
        """
        try:
            # Reset conversation for each new chat to avoid context buildup
            self.conversation = Conversation(
                name=f"conversation-{self.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

            # Add the user message to conversation
            self.conversation.add("human", message)

            # Run the research step
            output = self.step(message)

            return output

        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return f"I apologize, but I encountered an error while processing your research request: {str(e)}"

    def create_gradio_interface(self):
        """
        Create and return a Gradio chat interface for the research system.

        Returns:
            gr.Interface: The configured Gradio interface.
        """
        if gr is None:
            raise ImportError(
                "Gradio is not installed. Please install it with: pip install gradio"
            )

        # Create the chat interface
        interface = gr.ChatInterface(
            fn=self.chat_response,
            title=self.name,
            description=self.description,
            examples=[
                "What are the latest advances in quantum computing?",
                "Research the most effective treatments for diabetes",
                "What are the current trends in artificial intelligence?",
                "Find information about renewable energy technologies",
                "What are the latest developments in space exploration?",
            ],
            chatbot=gr.Chatbot(
                height=600,
                placeholder="Ask me any research question and I'll provide comprehensive findings using advanced AI agents.",
            ),
            textbox=gr.Textbox(
                placeholder="Enter your research question here...",
                container=False,
                scale=7,
            ),
        )

        return interface

    def launch_chat_interface(
        self,
        share: bool = False,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        **kwargs,
    ):
        """
        Launch the Gradio chat interface.

        Args:
            share (bool): Whether to create a public link. Default is False.
            server_name (str): Server host. Default is "127.0.0.1".
            server_port (int): Server port. Default is 7860.
            **kwargs: Additional arguments to pass to gradio.launch().
        """
        if gr is None:
            raise ImportError(
                "Gradio is not installed. Please install it with: pip install gradio"
            )

        interface = self.create_gradio_interface()

        logger.info(f"Launching {self.name} chat interface...")
        logger.info(
            f"Access the interface at: http://{server_name}:{server_port}"
        )

        interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            **kwargs,
        )

    def get_output_methods(self):
        """
        Get the available output formatting methods.

        Returns:
            list: List of available HistoryOutputType values.
        """
        return list(HistoryOutputType)
