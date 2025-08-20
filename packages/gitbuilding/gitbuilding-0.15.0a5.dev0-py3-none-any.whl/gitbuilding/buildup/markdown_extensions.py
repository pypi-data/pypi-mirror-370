"""
Lists markdown extensions used.
"""
def base_extensions(pdf=False, unmark=False):
    extensions = ["markdown.extensions.tables",
                  "markdown.extensions.attr_list",
                  "markdown.extensions.fenced_code",
                  "gitbuilding.buildup.buildup_list:BuildUpListExtension",
                  "markdown.extensions.md_in_html"]
    if not pdf and not unmark:
        extensions.append("markdown.extensions.toc")
    return tuple(extensions)

