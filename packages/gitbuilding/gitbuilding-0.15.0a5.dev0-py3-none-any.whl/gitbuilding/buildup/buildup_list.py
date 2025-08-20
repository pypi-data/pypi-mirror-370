"""
This formats the lists for buildup inculding setting classes.

It is forked from the Sane List Extension for Python-Markdown
which was released under the
[BSD License](https://opensource.org/licenses/bsd-license.php)

Original code Copyright 2011 [Waylan Limberg](http://achinghead.com)
All changes Copyright 2011-2023 The Python Markdown Project

Changes since 2023 are Copyright the GitBuilding project and licensed
under the GNU GPL.
"""

import regex as re

from markdown.extensions import Extension
from markdown.blockprocessors import OListProcessor, UListProcessor


class BuildUpOListProcessor(OListProcessor):
    """
    The markdown extension process for ordered lists
    """

    SIBLING_TAGS = ['ol']
    LAZY_OL = False

    def __init__(self, parser):
        super().__init__(parser)
        self.RE = re.compile(r'^[ ]{0,%d}\d+\.[ ]+(.*)' % (self.tab_length - 1))
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}((\d+\.))[ ]+(.*)' %
                                   (self.tab_length - 1))
        self.INDENT_RE = re.compile(r'^[ ]{%d,%d}((\d+\.)|[*+-](?:\{ *[a-zA-Z0-9-]+ *\})?)[ ]+.*' %
                                    (self.tab_length, self.tab_length * 2 - 1))


class BuildUpUListProcessor(UListProcessor):
    """
    The markdown extension process for unordered lists
    """

    SIBLING_TAGS = ['ul']

    def __init__(self, parser):
        super().__init__(parser)
        self.RE = re.compile(r'^[ ]{0,%d}[*+-](?:\{ *[a-zA-Z0-9-]+ *\})?[ ]+(.*)' %
                             (self.tab_length - 1))
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}(([*+-])(?:\{ *[a-zA-Z0-9-]+ *\})?)[ ]+(.*)' %
                                   (self.tab_length - 1))
        self.INDENT_RE = re.compile(r'^[ ]{%d,%d}((\d+\.)|[*+-](?:\{ *[a-zA-Z0-9-]+ *\})?)[ ]+.*' %
                                    (self.tab_length, self.tab_length * 2 - 1))
        self.BULLET_CLASS_RE = re.compile(r'[*+-]\{ *([a-zA-Z0-9-]+) *\}') # pylint: disable=invalid-name

    def get_items(self, block):
        """ Break a block into list items. """
        items = []
        tags = []
        for line in block.split('\n'):
            m = self.CHILD_RE.match(line)
            if m:
                tag_m = self.BULLET_CLASS_RE.match(m.group(1))
                tag = tag_m.group(1) if tag_m else None

                # Append to the list
                items.append(m.group(3))
                tags.append(tag)
            elif self.INDENT_RE.match(line):
                # This is an indented (possibly nested) item.
                if items[-1].startswith(' '*self.tab_length):
                    # Previous item was indented. Append to that item.
                    items[-1] = f'{items[-1]}\n{line}'
                else:
                    items.append(line)
                    tags.append(None)
            else:
                # This is another line of previous item. Append to that item.
                items[-1] = f'{items[-1]}\n{line}'

        for i, item in enumerate(items):
            if tags[i] is not None:
                items[i] = item + '\n{:.' + tags[i] + '}'
        return items


class BuildUpListExtension(Extension):
    """ Add Build Up lists to Markdown. """

    def extendMarkdown(self, md):
        """ Override existing List Processors. and add extra tree processor for attributes"""
        md.parser.blockprocessors.register(BuildUpOListProcessor(md.parser), 'olist', 40)
        md.parser.blockprocessors.register(BuildUpUListProcessor(md.parser), 'ulist', 30)


def makeExtension(**kwargs): # pylint: disable=invalid-name
    """
    This is required by the markdown extention API:
    https://python-markdown.github.io/extensions/api/#dot_notation
    """
    return BuildUpListExtension(**kwargs)
