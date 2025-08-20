'''
Function to remove markdown formatting.
from https://stackoverflow.com/a/54923798
'''
from io import StringIO
from markdown import Markdown
from .markdown_extensions import base_extensions


def unmark_element(element, stream=None):
    '''
    Stream processor to patch Markdown with. Removes all markdown formatting.
    '''
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain", extensions=base_extensions(unmark=True))
__md.stripTopLevelTags = False

def unmark(text, remove_bottom_nav=True):
    '''
    Returns a copy of text with markdown formatting removed.
    '''
    if remove_bottom_nav:
        nav_ident = "<!-- GitBuilding Nav -->"
        if nav_ident in text:
            nav_pos = text.index(nav_ident)
            text = text[:nav_pos]
    return __md.convert(text)
