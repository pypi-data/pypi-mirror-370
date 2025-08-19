import kallia_core.prompts as Prompts
from typing import Any
from docling_core.transforms.serializer.base import (
    BaseDocSerializer,
    SerializationResult,
)
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import MarkdownPictureSerializer
from docling_core.types.doc.document import PictureItem, DoclingDocument
from typing_extensions import override
from kallia_core.messages import Messages
from kallia_core.utils import Utils


class ImageCaptionSerializer(MarkdownPictureSerializer):
    def __init__(
        self, temperature: float, max_tokens: int, include_image_captioning: bool
    ) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.include_image_captioning = include_image_captioning

    @override
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        **kwargs: Any,
    ) -> SerializationResult:
        if not self.include_image_captioning:
            return create_ser_result(text="<image></image>", span_source=item)

        image_url = Utils.to_data_url(item.get_image(doc))
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": Prompts.IMAGE_CAPTIONING_PROMPT},
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
        content = f"<image>{extracted_data}</image>"
        return create_ser_result(text=content, span_source=item)
