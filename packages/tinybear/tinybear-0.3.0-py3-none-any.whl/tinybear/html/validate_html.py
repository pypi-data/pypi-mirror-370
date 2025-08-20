import re
from collections.abc import Iterable

from bs4 import BeautifulSoup, Tag

from tinybear.exceptions import ParsingError

TAG_PATTERN = re.compile(r"<(/?\w+)[^>]*>")
UNESCAPED_LTE_PATTERN = re.compile(r"<(?![a-zA-Z/])")


def validate_html(
    html: str,
    allowed_tags: Iterable[str] = (
        "a",
        "b",
        "body",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "head",
        "html",
        "i",
        "li",
        "ol",
        "p",
        "strong",
        "sub",
        "sup",
        "title",
        "u",
        "ul",
    ),
    is_text_at_root_level_allowed: bool = False,
) -> None:
    """
    Validate that the HTML string is well-formed and only contains allowed tags.

    Args:
        html: The HTML string to validate
        allowed_tags: Iterable of allowed HTML tag names (e.g., ['p', 'a', 'strong']).
            Defaults to a basic (quite restrictive) set of tags.
        is_text_at_root_level_allowed: If True, allow text nodes at the root level.
            If False (default), all text must be wrapped in block elements.

    Raises:
        ParsingError: If the HTML is not well-formed or contains disallowed tags
    """
    if not html:
        return  # Empty string is valid

    _check_for_unescaped_ampersand(html)
    _check_for_unescaped_less_than(html)

    soup = BeautifulSoup(html, "html5lib")

    _check_all_tags_are_allowed(soup=soup, allowed_tags=allowed_tags)
    _check_list_structure(soup)
    _check_paragraphs(soup)

    _check_for_unclosed_tags(html)

    if not is_text_at_root_level_allowed:
        _check_for_root_level_text(soup)


def _check_all_tags_are_allowed(soup: BeautifulSoup, allowed_tags: Iterable[str]) -> None:
    """Validate that only allowed tags are present in the HTML."""
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            raise ParsingError(
                f"Tag '{tag.name}' is not allowed. "
                f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
            )


def _check_entity_with_ampersand(html: str, position: int) -> int:
    """Validate that an HTML entity is properly formatted.
    Return the position of the semicolon that closes the entity.
    """
    semicolon_pos = html.find(";", position + 1)
    if semicolon_pos == -1:
        raise ParsingError(f"Text contains unescaped &: {html[position:position + 50]}...")

    entity = html[position + 1 : semicolon_pos]
    if not (entity.startswith("#") and entity[1:].isdigit()) and entity not in [
        "amp",
        "lt",
        "gt",
        "quot",
        "apos",
    ]:
        raise ParsingError(
            f"Invalid HTML entity: &{entity}; in: {html[position:position + 50]}..."
        )

    return semicolon_pos


def _check_for_root_level_text(soup: BeautifulSoup) -> None:
    """Validate that there's no text at the root level or after block elements.

    This function checks for text nodes that are not properly wrapped in block elements.
    It allows text in certain inline elements but requires other text to be in block elements.
    """
    # First check direct children of the root for any text nodes
    body = soup.find("body")  # even if there's no <body> tag, html5lib will wrap content in one
    for child in body.children:
        if isinstance(child, str) and child.strip():
            raise ParsingError("Text must be wrapped in a block element")


def _check_for_unescaped_ampersand(html: str) -> None:
    """Check that there are no unescaped ampersands."""
    position = 0

    while position < len(html):
        if html[position] == "&":
            semicolon_pos = _check_entity_with_ampersand(html, position)
            position = semicolon_pos + 1
        else:
            position += 1


def _check_for_unescaped_less_than(html: str) -> None:
    """Check for a solitary '<' in the text content (not followed by a letter or an "/")."""
    if UNESCAPED_LTE_PATTERN.search(html):
        raise ParsingError("Unescaped '<' found in text content. Use '&lt;' instead.")


def _check_for_unclosed_tags(html: str) -> None:
    # Extract all tags from the string
    tags = TAG_PATTERN.findall(html)
    # Count opening and closing tags
    tag_counts: dict[str, int] = {}
    for tag in tags:
        if tag.startswith("/"):
            tag_name = tag[1:]
            tag_counts[tag_name] = tag_counts.get(tag_name, 0) - 1
        else:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    # Tags with non-zero count are unbalanced
    unclosed = [tag for tag, count in tag_counts.items() if count != 0]

    if unclosed:
        raise ParsingError(f"Unclosed tags found:{', '.join(unclosed)}")


def _check_list_structure(soup: BeautifulSoup) -> None:
    """Validate the structure of lists and list items."""
    # Check list structure
    for list_tag in soup(["ul", "ol"]):
        for child in list_tag.children:
            if isinstance(child, Tag) and child.name != "li":
                raise ParsingError(
                    f"<{list_tag.name}> can only contain <li> elements, "
                    f"found <{child.name}>: {child}"
                )

    # Check that <li> elements are direct children of <ul> or <ol>
    for li in soup("li"):
        parent = li.parent
        if parent.name not in ["ul", "ol"]:
            raise ParsingError(
                f"<li> must be a direct child of <ul> or <ol>, "
                f"found inside <{parent.name}>: {li}"
            )


def _check_paragraphs(soup: BeautifulSoup) -> None:
    """Validate paragraph structure and content."""
    paragraphs = soup("p")

    # Check for empty or nested paragraphs
    # Due to how parser works, nested paragraphs will end up being transformed into
    # sequence of paragraphs with empty paragraph at the end.
    for p in paragraphs:
        if not p.get_text(strip=True):
            raise ParsingError("Empty or nested <p> tags are not allowed")
