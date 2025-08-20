import logging
from pathlib import Path

import mammoth

from tinybear._paths import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR

logging.basicConfig(level=logging.INFO)

DEFAULT_STYLE_MAP = """
b => strong
i => em
p[style-name='Title'] => h1
p[style-name='Heading1'] => h1
p[style-name='Heading 1'] => h1
p[style-name='Heading2'] => h2
p[style-name='Heading 2'] => h2
p[style-name='Heading3'] => h3
p[style-name='Heading 3'] => h3
p[style-name='Heading4'] => h4
p[style-name='Heading 4'] => h4
"""


def convert_file_from_doc(
    path_to_file: Path,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    style_map: str = DEFAULT_STYLE_MAP,
    print_html: bool = True,
) -> Path:
    """Read from DOC(x) file, write to HTML file, return its path."""

    html = read_from_doc(path_to_file=path_to_file, style_map=style_map)

    if print_html:
        logging.info(html)

    output_path = output_dir / f"{path_to_file.stem}.html"

    with output_path.open(mode="w", encoding="utf-8") as output_file:
        output_file.write(html)

    return output_path


def convert_all_docs(
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    print_html: bool = True,
) -> None:
    """Converts all .DOC(x) files in a directory."""
    if not output_dir.exists():
        output_dir.mkdir()

    for pattern in ("*.doc", "*.docx"):
        for file in input_dir.glob(pattern):
            logging.info(f"Converting {file.name}")
            convert_file_from_doc(path_to_file=file, output_dir=output_dir, print_html=print_html)


def read_from_doc(
    path_to_file: Path,
    style_map: str = DEFAULT_STYLE_MAP,
) -> str:
    """Read binary content from doc file and produce string HTML."""
    with path_to_file.open(mode="rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, style_map=style_map)
        return result.value


if __name__ == "__main__":
    convert_all_docs()  # pragma: no cover
