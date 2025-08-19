from typing import Dict
from dxtrx.utils.ml.llm.domain import AssistantPrompt
from dagster import get_dagster_logger

logger = get_dagster_logger()

def format_prompt(prompt: AssistantPrompt, variables: Dict[str, str]) -> AssistantPrompt:
    try:
        formatted_messages = []
        for message in prompt.messages:
            new_message = message.model_copy()
            if message.role == "user":
                new_content = message.content.format(**variables)
                new_message = message.model_copy(update={"content": new_content})
            formatted_messages.append(new_message)
        return prompt.model_copy(update={"messages": formatted_messages})
    except KeyError as e:
        raise ValueError(f"Missing required variable in template: {e}")
    except Exception as e:
        logger.error(f"Error formatting messages: {e}")
        raise
