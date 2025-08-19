"""
Kallia - Semantic Document Processing Library

Kallia is a FastAPI-based document processing service that converts documents into
intelligent semantic chunks. The library specializes in extracting meaningful content
segments from documents while preserving context and semantic relationships.

Key Features:
- Document-to-markdown conversion for standardized processing
- Semantic chunking that respects document structure and meaning
- Support for PDF documents with extensible architecture for additional formats
- RESTful API interface with comprehensive error handling
- Configurable processing parameters (temperature, token limits, page selection)

The library is designed for applications requiring document analysis, content
extraction, knowledge base construction, and semantic search implementations.

Author: CK
GitHub: https://github.com/kallia-project/kallia
License: Apache License 2.0
Version: 0.1.4
"""

import requests
import logging
import kallia_core.models as Models
import kallia_core.constants as Constants
from fastapi import FastAPI, HTTPException
from kallia_core.memories import Memories
from kallia_core.documents import Documents
from kallia_core.chunker import Chunker
from kallia_core.logger import Logger
from kallia_core.utils import Utils

logger = logging.getLogger(__name__)
Logger.config(logger)

app = FastAPI(title=Constants.APP_NAME, version=Constants.VERSION)


@app.post("/memories", response_model=Models.MemoriesResponse)
def memories(request: Models.MemoriesRequest):
    try:
        memories = Memories.create(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return Models.MemoriesResponse(memories=memories)

    except Exception as e:
        logger.error(f"Internal Server Error {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/markdownify", response_model=Models.MarkdownifyResponse)
def markdownify(request: Models.MarkdownifyRequest):
    file_format = Utils.get_extension(request.url)
    if file_format not in Constants.SUPPORTED_FILE_FORMATS:
        logger.error("Invalid File Format")
        raise HTTPException(status_code=400, detail="Invalid File Format")

    try:
        markdown_content = Documents.to_markdown(
            source=request.url,
            page_number=request.page_number,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            include_image_captioning=request.include_image_captioning,
        )
        return Models.MarkdownifyResponse(markdown=markdown_content)

    except Exception as e:
        logger.error(f"Internal Server Error {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/chunks", response_model=Models.ChunksResponse)
def chunks(request: Models.ChunksRequest):
    try:
        semantic_chunks = Chunker.create(
            text=request.text,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return Models.ChunksResponse(chunks=semantic_chunks)

    except Exception as e:
        logger.error(f"Internal Server Error {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/documents", response_model=Models.DocumentsResponse)
def documents(request: Models.DocumentsRequest):
    file_format = Utils.get_extension(request.url)
    if file_format not in Constants.SUPPORTED_FILE_FORMATS:
        logger.error("Invalid File Format")
        raise HTTPException(status_code=400, detail="Invalid File Format")

    try:
        markdown_content = Documents.to_markdown(
            source=request.url,
            page_number=request.page_number,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            include_image_captioning=request.include_image_captioning,
        )
        semantic_chunks = Chunker.create(
            text=markdown_content,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        documents = [
            Models.Document(page_number=request.page_number, chunks=semantic_chunks)
        ]
        return Models.DocumentsResponse(documents=documents)

    except requests.exceptions.RequestException as e:
        logger.error(f"Service Unavailable {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

    except Exception as e:
        logger.error(f"Internal Server Error {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
