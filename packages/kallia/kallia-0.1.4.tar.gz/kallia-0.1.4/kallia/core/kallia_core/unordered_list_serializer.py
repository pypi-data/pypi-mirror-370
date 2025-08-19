import kallia_core.prompts as Prompts
from typing import Any
from docling_core.transforms.serializer.base import (
    BaseDocSerializer,
    SerializationResult,
)
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer
from docling_core.types.doc.document import TableItem, DoclingDocument
from typing_extensions import override
from kallia_core.messages import Messages
from kallia_core.utils import Utils


class UnorderedListSerializer(MarkdownTableSerializer):
    def __init__(self, temperature: float, max_tokens: int) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens

    @override
    def serialize(
        self,
        *,
        item: TableItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        **kwargs: Any,
    ) -> SerializationResult:
        image_url = Utils.to_data_url(item.get_image(doc))
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": Prompts.TABLE_EXTRACTION_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]
        response = Messages.send(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        extracted_data = Utils.unwrap("information", response)
        content = f"<table>{extracted_data}</table>"
        return create_ser_result(text=content, span_source=item)
