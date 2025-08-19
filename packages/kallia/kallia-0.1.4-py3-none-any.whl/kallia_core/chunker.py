import json
import kallia_core.models as Models
import kallia_core.prompts as Prompts
from typing import List
from kallia_core.utils import Utils
from kallia_core.messages import Messages


class Chunker:
    @staticmethod
    def create(
        text: str, temperature: float = 0.0, max_tokens: int = 8192
    ) -> List[Models.Chunk]:
        messages = [
            {"role": "system", "content": Prompts.SEMANTIC_CHUNKING_PROMPT},
            {"role": "user", "content": text},
        ]
        response = Messages.send(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = Utils.unwrap("information", response)
        return json.loads(content)
