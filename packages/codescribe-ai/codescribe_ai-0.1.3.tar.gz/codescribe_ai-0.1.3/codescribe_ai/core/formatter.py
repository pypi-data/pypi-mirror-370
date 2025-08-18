# core/formatter.py

def collapse_long_sections(summary_dict, max_lines=300,use_html=False):
    """
    Collapses long summaries with a toggle using HTML <details>.

    Args:
        summary_dict (dict): File path to summary mapping.
        max_lines (int): Maximum visible lines before collapsing.

    Returns:
        dict: Modified summary_dict with collapsible HTML for long summaries.
    """
    collapsed = {}
    for file, summary in summary_dict.items():
        lines = summary.strip().split("\n")
        if len(lines) > max_lines:
            short_preview = "\n".join(lines[:max_lines])
            if use_html:
                detail_block = f"<details>\n<summary>Show More</summary>\n\n{summary.strip()}\n</details>"
                collapsed[file] = short_preview + "\n\n" + detail_block
            else:
                collapsed[file] = short_preview + "\n... [Content truncated]"
        else:
            collapsed[file] = summary
    return collapsed
