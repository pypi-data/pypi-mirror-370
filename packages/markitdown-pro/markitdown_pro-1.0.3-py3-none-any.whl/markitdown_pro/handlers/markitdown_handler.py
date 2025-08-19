import asyncio
from typing import Optional

from markitdown import MarkItDown

from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from .base_handler import BaseHandler


class MarkItDownHandler(BaseHandler):
    """
    Async adapter around MarkItDown.

    - `handle(...)` is async and returns a Markdown string (or "" on failure).
    - The blocking `MarkItDown.convert(...)` call is executed via `asyncio.to_thread`
      so it doesn't block the event loop.
    """

    extensions = frozenset({".csv", ".docx", ".xlsx", ".pptx"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markitdown = MarkItDown()

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Asynchronously convert a supported file to Markdown.

        Parameters
        ----------
        file_path : str
            Path to the input file (.csv, .docx, .xlsx, .pptx).

        Returns
        -------
        str
            Markdown content, or an empty string on error / insufficient content.
        """
        logger.info(f"MarkItDownHandler: Processing '{file_path}'")
        try:
            # Run the blocking conversion off the event loop
            result = await asyncio.to_thread(self.markitdown.convert, file_path)

            # Some versions of MarkItDown return an object with `.markdown`,
            # others may return a string; normalize to a string.
            markdown = getattr(result, "markdown", result)
            if not isinstance(markdown, str):
                markdown = str(markdown)

            if not ensure_minimum_content(markdown):
                raise RuntimeError(f"MarkItDownHandler: Insufficient content for '{file_path}'")

            return markdown

        except Exception as e:
            logger.error(f"MarkItDownHandler: Error processing '{file_path}': {e}")
            return None
