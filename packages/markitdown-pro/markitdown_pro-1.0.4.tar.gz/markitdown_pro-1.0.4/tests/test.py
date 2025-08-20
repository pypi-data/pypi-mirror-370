import logging
from pathlib import Path

import pytest
from dotenv import load_dotenv

from markitdown_pro.conversion_pipeline import ConversionPipeline

from .fixtures import EXCLUDE_EXTENSIONS, data_path
from .utils import list_files

log = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.resolve()
ENV_PATH = SCRIPT_DIR / ".test.env"

if not ENV_PATH.exists():
    raise FileNotFoundError(
        f"The .test.env file is missing in {SCRIPT_DIR!s}. "
        "Please create it with the required environment variables."
    )

load_dotenv(dotenv_path=str(ENV_PATH))

TEST_FILES_PATH = data_path()
ALL_FILES = list_files(TEST_FILES_PATH, exclude_ext=EXCLUDE_EXTENSIONS, recursive=True)
log.info(f"Found {len(ALL_FILES)} test files in {TEST_FILES_PATH}.")


def _pretty_id(p: Path) -> str:
    base = data_path()
    try:
        return str(p.relative_to(base))
    except ValueError:
        return p.name


@pytest.mark.asyncio
@pytest.mark.parametrize("file_path", ALL_FILES, ids=[_pretty_id(p) for p in ALL_FILES])
async def test_files(file_path: Path, pipeline: ConversionPipeline):
    log.info(f"Testing file: {file_path}")

    markdown_text = await pipeline.convert_document_to_md(str(file_path))
    assert markdown_text is not None, f"Conversion returned None for {file_path.name}"
    assert isinstance(markdown_text, str), f"Output type is not str for {file_path.name}"
