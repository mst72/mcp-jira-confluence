"""
Formatters for converting plain text to Atlassian Document Format (ADF)
and Confluence Storage Format.
"""

import re
from typing import Dict, Any, List


def plain_text_to_adf(text: str) -> Dict[str, Any]:
    """
    Convert plain text to Atlassian Document Format (ADF).

    Supports basic formatting:
    - Paragraphs (separated by double newlines)
    - Bold: **text** or __text__
    - Italic: *text* or _text_
    - Code: `code`
    - Bullet lists: lines starting with * or -
    - Numbered lists: lines starting with 1., 2., etc.

    Args:
        text: Plain text with optional markdown-like formatting

    Returns:
        ADF JSON structure
    """
    if not text or not text.strip():
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": []
                }
            ]
        }

    content = []
    lines = text.split('\n')
    current_paragraph = []
    current_list = []
    list_type = None  # 'bullet' or 'ordered'

    def flush_paragraph():
        nonlocal current_paragraph, content
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            if para_text.strip():
                content.append(_create_paragraph(para_text))
            current_paragraph = []

    def flush_list():
        nonlocal current_list, list_type, content
        if current_list and list_type:
            content.append({
                "type": "bulletList" if list_type == "bullet" else "orderedList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [_create_paragraph(item)]
                    }
                    for item in current_list
                ]
            })
            current_list = []
            list_type = None

    for line in lines:
        stripped = line.strip()

        # Empty line - paragraph break
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        # Bullet list item
        if stripped.startswith('* ') or stripped.startswith('- '):
            flush_paragraph()
            if list_type != "bullet":
                flush_list()
                list_type = "bullet"
            current_list.append(stripped[2:])
            continue

        # Numbered list item
        numbered_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if numbered_match:
            flush_paragraph()
            if list_type != "ordered":
                flush_list()
                list_type = "ordered"
            current_list.append(numbered_match.group(1))
            continue

        # Regular line - add to current paragraph
        flush_list()
        current_paragraph.append(stripped)

    # Flush remaining content
    flush_paragraph()
    flush_list()

    # If no content was created, add empty paragraph
    if not content:
        content = [{"type": "paragraph", "content": []}]

    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def _create_paragraph(text: str) -> Dict[str, Any]:
    """
    Create a paragraph node with inline formatting support.

    Args:
        text: Text with markdown-like inline formatting

    Returns:
        Paragraph ADF node
    """
    inline_content = _parse_inline_formatting(text)

    return {
        "type": "paragraph",
        "content": inline_content if inline_content else [{"type": "text", "text": ""}]
    }


def _parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """
    Parse inline formatting (bold, italic, code) from text.

    Args:
        text: Text with markdown-like formatting

    Returns:
        List of text nodes with marks
    """
    content = []
    remaining = text

    # Simple pattern matching for basic formatting
    # This is a simplified version - a full parser would be more robust
    pattern = r'(\*\*|__|`|\*|_)'
    parts = re.split(pattern, remaining)

    i = 0
    while i < len(parts):
        part = parts[i]

        if not part:
            i += 1
            continue

        # Regular text
        if part not in ('**', '__', '*', '_', '`'):
            if part.strip():
                content.append({"type": "text", "text": part})
            i += 1
            continue

        # Found a delimiter - look for closing delimiter
        delimiter = part
        if i + 2 < len(parts):
            text_content = parts[i + 1]
            closing = parts[i + 2] if i + 2 < len(parts) else None

            if closing == delimiter and text_content:
                # Apply formatting
                marks = []
                if delimiter in ('**', '__'):
                    marks = [{"type": "strong"}]
                elif delimiter in ('*', '_'):
                    marks = [{"type": "em"}]
                elif delimiter == '`':
                    marks = [{"type": "code"}]

                content.append({
                    "type": "text",
                    "text": text_content,
                    "marks": marks
                })
                i += 3
                continue

        # No matching closing delimiter - treat as literal
        content.append({"type": "text", "text": delimiter})
        i += 1

    return content


def plain_text_to_storage(text: str) -> str:
    """
    Convert plain text to Confluence Storage Format (HTML-like).

    Supports basic formatting:
    - Paragraphs (separated by double newlines)
    - Headings: # H1, ## H2, ### H3
    - Bold: **text** or __text__
    - Italic: *text* or _text_
    - Code: `code`
    - Code blocks: ```code```
    - Bullet lists: lines starting with * or -
    - Numbered lists: lines starting with 1., 2., etc.

    Args:
        text: Plain text with optional markdown-like formatting

    Returns:
        Confluence Storage Format HTML string
    """
    if not text or not text.strip():
        return "<p></p>"

    html_parts = []
    lines = text.split('\n')
    current_paragraph = []
    current_list = []
    list_type = None  # 'ul' or 'ol'
    in_code_block = False
    code_block_lines = []

    def flush_paragraph():
        nonlocal current_paragraph, html_parts
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            if para_text.strip():
                formatted_text = _format_inline_html(para_text)
                html_parts.append(f"<p>{formatted_text}</p>")
            current_paragraph = []

    def flush_list():
        nonlocal current_list, list_type, html_parts
        if current_list and list_type:
            tag = list_type
            list_items = ''.join(f"<li>{_format_inline_html(item)}</li>" for item in current_list)
            html_parts.append(f"<{tag}>{list_items}</{tag}>")
            current_list = []
            list_type = None

    for line in lines:
        stripped = line.strip()

        # Code block delimiter
        if stripped.startswith('```'):
            if in_code_block:
                # End code block
                code_content = '\n'.join(code_block_lines)
                html_parts.append(
                    f'<ac:structured-macro ac:name="code">'
                    f'<ac:plain-text-body><![CDATA[{code_content}]]></ac:plain-text-body>'
                    f'</ac:structured-macro>'
                )
                code_block_lines = []
                in_code_block = False
            else:
                # Start code block
                flush_paragraph()
                flush_list()
                in_code_block = True
            continue

        # Inside code block
        if in_code_block:
            code_block_lines.append(line)
            continue

        # Empty line
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        # Heading
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2)
            html_parts.append(f"<h{level}>{_format_inline_html(heading_text)}</h{level}>")
            continue

        # Bullet list item
        if stripped.startswith('* ') or stripped.startswith('- '):
            flush_paragraph()
            if list_type != "ul":
                flush_list()
                list_type = "ul"
            current_list.append(stripped[2:])
            continue

        # Numbered list item
        numbered_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if numbered_match:
            flush_paragraph()
            if list_type != "ol":
                flush_list()
                list_type = "ol"
            current_list.append(numbered_match.group(1))
            continue

        # Regular line
        flush_list()
        current_paragraph.append(stripped)

    # Flush remaining content
    flush_paragraph()
    flush_list()

    if not html_parts:
        return "<p></p>"

    return ''.join(html_parts)


def _format_inline_html(text: str) -> str:
    """
    Apply inline HTML formatting to text.

    Args:
        text: Text with markdown-like formatting

    Returns:
        HTML formatted text
    """
    # Escape HTML special characters
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic: *text* or _text_ (but not in middle of word)
    text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)

    # Inline code: `code`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    return text
