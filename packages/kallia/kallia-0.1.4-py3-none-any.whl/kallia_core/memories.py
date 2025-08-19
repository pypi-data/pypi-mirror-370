import json
import kallia_core.models as Models
import kallia_core.prompts as Prompts
from typing import Any, Dict, List
from kallia_core.utils import Utils
from kallia_core.messages import Messages


class Memories:
    @staticmethod
    def create(
        messages: List[Models.Message], temperature: float = 0.0, max_tokens: int = 8192
    ) -> Dict[str, Any]:
        conversation = ""
        for message in messages:
            conversation += f"<{message.role}>{message.content}</{message.role}>"
        messages = [
            {"role": "system", "content": Prompts.MEMORY_EXTRACTION_PROMPT},
            {"role": "user", "content": conversation},
        ]
        response = Messages.send(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = Utils.unwrap("information", response)
        return json.loads(content)
