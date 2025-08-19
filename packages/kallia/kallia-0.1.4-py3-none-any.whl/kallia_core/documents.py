from kallia_core.image_caption_serializer import ImageCaptionSerializer
from kallia_core.unordered_list_serializer import UnorderedListSerializer
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat


class Documents:
    @staticmethod
    def to_markdown(
        source: str,
        page_number: int = 1,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        include_image_captioning=False,
    ) -> str:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = True

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        page_range = (page_number, page_number)
        converted_doc = converter.convert(source, page_range=page_range).document
        markdown_serializer = MarkdownDocSerializer(
            doc=converted_doc,
            picture_serializer=ImageCaptionSerializer(
                temperature, max_tokens, include_image_captioning
            ),
            table_serializer=UnorderedListSerializer(temperature, max_tokens),
        )
        return markdown_serializer.serialize().text
