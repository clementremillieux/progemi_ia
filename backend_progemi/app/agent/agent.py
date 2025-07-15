"""Agent module"""

from typing import List, Optional

from pydantic import BaseModel

from openai import AsyncOpenAI

from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)

from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)

from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

from openai.types.chat.chat_completion_prediction_content_param import (
    ChatCompletionPredictionContentParam,
)

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage


from app.cost.cost import CostTracker

from app.performances.time_counter import time_execution

from config.logger_config import logger


class Agent:
    """Agent class for interacting with OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        system_promt: str,
        nb_retry: int = 1,
        timeout: float = 60.0,
        temprature: float = 0.0,
        name: str = "",
        cost_tracker: Optional[CostTracker] = None,
        reasoning_effort: str = "high",
        prediction: Optional[ChatCompletionPredictionContentParam] = None,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key)

        self.model_name: str = model_name

        self.system_prompt: str = system_promt

        self.nb_retry: int = nb_retry

        self.timeout: float = timeout

        self.temprature: float = temprature

        self.name = name

        self.cost_tracker: Optional[CostTracker] = cost_tracker

        self.reasoning_effort: str = reasoning_effort

        self.prediction: Optional[ChatCompletionPredictionContentParam] = prediction

    @time_execution
    async def run(
        self, response_format: type[BaseModel], chat_historic: List[BaseMessage]
    ) -> Optional[BaseModel]:
        """Run the agent with the provided chat history."""

        messages: List[
            ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionAssistantMessageParam
        ] = [
            ChatCompletionSystemMessageParam(content=self.system_prompt, role="system")
        ]

        for message in chat_historic:
            if isinstance(message, HumanMessage):
                messages += [
                    ChatCompletionUserMessageParam(
                        content=str(message.content), role="user"
                    )
                ]
            elif isinstance(message, AIMessage):
                messages += [
                    ChatCompletionAssistantMessageParam(
                        content=str(message.content), role="assistant"
                    )
                ]
            elif isinstance(message, SystemMessage):
                messages += [
                    ChatCompletionSystemMessageParam(
                        content=str(message.content), role="system"
                    )
                ]

        for _ in range(self.nb_retry):
            try:
                completion: ParsedChatCompletion = (
                    await self.client.chat.completions.parse(
                        model=self.model_name,
                        messages=messages,
                        response_format=response_format,
                        timeout=self.timeout,
                        temperature=self.temprature,
                        prediction=self.prediction,
                        # reasoning_effort=self.reasoning_effort,
                    )
                )

                reasoning = completion.choices[0].message.parsed

                self.add_cost(completion=completion)

                return reasoning

            except Exception as e:
                logger.warning(
                    "AGENT => Error while calling openai [%s] : %s",
                    self.name,
                    e,
                    exc_info=True,
                )

        logger.error(
            "AGENT => Max retry calling openai [%s] : 3",
            self.name,
        )

        return None

    def add_cost(self, completion: ParsedChatCompletion) -> None:
        """Add cost"""

        if self.cost_tracker and completion.usage:
            input_tokens: int = completion.usage.prompt_tokens

            output_tokens: int = completion.usage.completion_tokens

            model: str = completion.model

            self.cost_tracker.add_openai_query(
                nb_input_token=input_tokens,
                nb_output_token=output_tokens,
                model=model,
                function_name=self.name,
            )

    def log_agent_output(self, agent_output: BaseModel) -> None:
        """Log agent output"""

        logger.info(
            "AGENT => Agent output %s: %s",
            self.name,
            agent_output.model_dump_json(indent=2),
        )
