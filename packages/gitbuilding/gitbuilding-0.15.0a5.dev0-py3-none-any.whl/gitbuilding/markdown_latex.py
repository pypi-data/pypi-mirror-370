'''
This extension was coppied from the markdown latex package and then modified to work
with latex2mathml.

This file has been re-licenced GPL
All makrdown-latex content is:
# Copyright (c) 2019-2021 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
'''


import re
import typing as typ
import hashlib
import logging

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from latex2mathml.converter import convert as latex2mathml

logger = logging.getLogger(__name__)

FENCE_RE       = re.compile(r"^(\s*)(`{3,}|~{3,})")
BLOCK_START_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math")
BLOCK_CLEAN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math(.*)(\2)$", flags=re.DOTALL)
INLINE_DELIM_RE = re.compile(r"`{1,2}")

def _clean_block_text(block_text: str) -> str:
    block_match = BLOCK_CLEAN_RE.match(block_text)
    if block_match:
        return block_match.group(3)
    return block_text


def make_marker_id(text: str) -> str:
    """
    Return a hash to mark the position fo the tex block
    """
    data = text.encode("utf-8")
    return hashlib.md5(data).hexdigest()


def tex2html(tex: str) -> str:
    '''
    Convert latex into mathml html
    '''
    result = latex2mathml(tex)
    return result


def _md_block2html(block_text: str) -> str:
    block_text = _clean_block_text(block_text)
    header, rest = block_text.split("\n", 1)
    if "{" in header and "}" in header:
        block_text = rest

    return tex2html(block_text)


def _clean_inline_text(inline_text: str) -> str:
    if inline_text.startswith("$``"):
        inline_text = inline_text[len("$``") :]
    if inline_text.startswith("$`"):
        inline_text = inline_text[len("$`") :]
    if inline_text.endswith("``$"):
        inline_text = inline_text[: -len("``$")]
    if inline_text.endswith("`$"):
        inline_text = inline_text[: -len("`$")]
    return inline_text


def _md_inline2html(inline_text: str) -> str:
    inline_text = _clean_inline_text(inline_text)
    return tex2html(inline_text)


class InlineCodeItem(typ.NamedTuple):
    """
    Simple named tuple for iterating over inline latex
    """

    inline_text: str
    start      : int
    end        : int


def iter_inline_latex(line: str) -> typ.Iterable[InlineCodeItem]:
    """
    Iterate over inline Latex
    """
    pos = 0
    while True:
        inline_match_start = INLINE_DELIM_RE.search(line, pos)
        if inline_match_start is None:
            break

        pos   = inline_match_start.end()
        start = inline_match_start.start()
        delim = inline_match_start.group()

        try:
            end = line.index(delim, start + len(delim)) + (len(delim) - 1)
        except ValueError:
            continue

        pos = end

        if line[start - 1] != "$":
            continue
        if line[end + 1] != "$":
            continue

        inline_text = line[start - 1 : end + 2]
        pos         = end + len(delim)

        yield InlineCodeItem(inline_text, start - 1, end + 2)


def makeExtension(**kwargs): # pylint: disable=invalid-name
    """
    This is required by the markdown extention API:
    https://python-markdown.github.io/extensions/api/#dot_notation
    """
    return LatexExtension(**kwargs)

class LatexExtension(Extension):
    """
    The base extension class for the latex extension
    """
    def __init__(self, **kwargs) -> None:
        self.math_html: typ.Dict[str, str] = {}
        super().__init__(**kwargs)

    def reset(self) -> None:
        self.math_html.clear()

    def extendMarkdown(self, md) -> None:
        """
        Register the preporcess or and post processor for the extensions
        """
        preproc = LatexPreprocessor(md, self)
        md.preprocessors.register(preproc, name='latex_fenced_code_block', priority=50)

        postproc = LatexPostprocessor(md, self)
        md.postprocessors.register(postproc, name='latex_fenced_code_block', priority=0)
        md.registerExtension(self)


class LatexPreprocessor(Preprocessor):
    """
    Preprocessor for the latex extension. The preprocessor doesn't create the mathml yet
    as it this might bet affected by later changes. Instead it replaces it with marker tags
    """

    def __init__(self, md, ext: LatexExtension) -> None:
        super().__init__(md)
        self.ext: LatexExtension = ext

    def _make_tag_for_block(self, block_lines: typ.List[str]) -> str:
        indent_len  = len(block_lines[0]) - len(block_lines[0].lstrip())
        indent_text = block_lines[0][:indent_len]

        block_text = "\n".join(line[indent_len:] for line in block_lines).rstrip()
        marker_id  = make_marker_id("block" + block_text)
        marker_tag = f"tmp_block_md_latex_{marker_id}"

        math_html = _md_block2html(block_text)
        self.ext.math_html[marker_tag] = f"<p>{math_html}</p>"
        return indent_text + marker_tag

    def _make_tag_for_inline(self, inline_text: str) -> str:
        marker_id  = make_marker_id("inline" + inline_text)
        marker_tag = f"tmp_inline_md_latex_{marker_id}"

        math_html = _md_inline2html(inline_text)
        self.ext.math_html[marker_tag] = math_html
        return marker_tag

    def _iter_out_lines(self, lines: typ.List[str]) -> typ.Iterable[str]:
        is_in_math_fence     = False
        is_in_fence          = False
        expected_close_fence = "```"

        block_lines: typ.List[str] = []

        for line in lines:
            if is_in_fence:
                yield line
                is_ending_fence = line.rstrip() == expected_close_fence
                if is_ending_fence:
                    is_in_fence = False
            elif is_in_math_fence:
                block_lines.append(line)
                is_ending_fence = line.rstrip() == expected_close_fence
                if is_ending_fence:
                    is_in_math_fence = False
                    marker_tag       = self._make_tag_for_block(block_lines)
                    del block_lines[:]
                    yield marker_tag
            else:
                math_fence_match = BLOCK_START_RE.match(line)
                fence_match      = FENCE_RE.match(line)
                if math_fence_match:
                    is_in_math_fence     = True
                    prefix               = math_fence_match.group(1)
                    expected_close_fence = prefix + math_fence_match.group(2)
                    block_lines.append(line)
                elif fence_match:
                    is_in_fence          = True
                    prefix               = fence_match.group(1)
                    expected_close_fence = prefix + fence_match.group(2)
                    yield line
                else:
                    inline_codes = list(iter_inline_latex(line))
                    for code in reversed(inline_codes):
                        # iterate in reverse, so that start and end indexes
                        # remain valid after replacements
                        marker_tag = self._make_tag_for_inline(code.inline_text)
                        line       = line[: code.start] + marker_tag + line[code.end :]

                    yield line

        # unclosed block
        if block_lines:
            for line in block_lines:
                yield line

    def run(self, lines: typ.List[str]) -> typ.List[str]:
        return list(self._iter_out_lines(lines))



class LatexPostprocessor(Postprocessor):
    """
    This post processor is needed because other processors might affect
    the output if it is directly yelided earlier on as the mathml markup could be
    parsed as markdown
    """
    def __init__(self, md, ext: LatexExtension) -> None:
        super().__init__(md)
        self.ext: LatexExtension = ext

    def run(self, text: str) -> str:
        if any(marker in text for marker in self.ext.math_html):

            for marker, html in self.ext.math_html.items():
                is_block  = marker.startswith("tmp_block_md_latex_")
                is_inline = marker.startswith("tmp_inline_md_latex_")
                assert is_block or is_inline

                if marker in text:
                    if is_block:
                        wrapped_marker = "<p>" + marker + "</p>"
                    else:
                        wrapped_marker = marker

                    while marker in text:
                        if wrapped_marker in text:
                            text = text.replace(wrapped_marker, html)
                        else:
                            text = text.replace(marker, html)
                else:
                    logger.warning("LatexPostprocessor couldn't find: %s", marker)

        return text
