"""
This module provides the default previewers for GitBuilding. Previewers
scan image-style markdown links for filtypes and links that can be automatically
previewed
"""

import re
import posixpath
import logging
from gitbuilding.buildup.preview import Previewer

_LOGGER = logging.getLogger('BuildUp')

def gitbuilding_previewers(enabled=True, no_server=False):
    """
    Return the standard previewers for Gitbuilding.
    """
    enable_3d = enabled and not no_server
    tdp = ThreeDimPreviewer(enable_3d)
    pdfp = PDFPreviewer(enabled)
    ytp = YouTubePreviewer(enabled)
    return [tdp, pdfp, ytp]

class ThreeDimPreviewer(Previewer):
    """
    Build-up previewer that will preview 3D models with GB3D
    """

    def __init__(self, enabled):
        super().__init__(enabled)
        self._name = "3D-previewer"
        self._drop_dir = "models"
        self._create_preview_page_when_enabled = True

    @property
    def creates_preview_page(self):
        """
        Property: is preview page created when enabled
        """
        return self._create_preview_page_when_enabled

    @property
    def pattern(self):
        """
        Pattern to match supported models
        """
        return re.compile(r'^.*\.(?:stl|STL|WRL|wrl|GLTF|gltf|glTF|glb|GLB)$')

    def _preview_code(self, uri, alt_text=None, hover_text=None, buildup_data=None):
        """
        Return the GB3D HTML code and a sensible response if no-script is running
        """
        # pylint: disable=unused-argument

        colour_text = ''
        if buildup_data is not None:
            if buildup_data.color:
                colour_text = f' color="{buildup_data.color}"'
        if alt_text is None:
            alt_text = "Download"

        html = (f'<noscript><a href="{uri}">{alt_text}</a></noscript>\n'
                f'<gb3d-viewer src="{uri}"{colour_text}></gb3d-viewer>')

        return html

    def preview_page_uri(self, uri):
        """
        Return the preview page uri
        """
        return posixpath.splitext(uri)[0] + ".md"

    def preview_page_content(self, uri, exsource_entry=None):
        """
        Return the markdown content of the preview page.
        """
        #Preview page is in same directory so we only need the file name
        file_name =  posixpath.basename(uri)
        model_name = posixpath.splitext(file_name)[0]

        if exsource_entry is None:
            page_md = f"# {model_name}\n\n"
            page_md += self._preview_code(file_name)
            return page_md

        return exsource_entry.as_markdown(preview_code=self._preview_code(file_name))

class PDFPreviewer(Previewer):
    """
    Build-up previewer that will preview PDF files
    """

    def __init__(self, enabled):
        super().__init__(enabled)
        self._name = "PDF-previewer"
        self._drop_dir = "documents"

    @property
    def pattern(self):
        """
        Pattern to match pdf files
        """
        return re.compile(r'^.*\.(?:pdf|PDF)$')

    def _preview_code(self, uri, alt_text=None, hover_text=None, buildup_data=None):
        """
        Return the a embeded view of the PDF
        """
        # pylint: disable=unused-argument
        if buildup_data is not None:
            _LOGGER.warning('PDF preview has unused buildup data',
                            extra={'fussy':True})

        html = (f'<embed src="{uri}" type="application/pdf" '
                'width="100%" height="600px" />')

        return html

class YouTubePreviewer(Previewer):
    """
    Build-up previewer that will embed YouTube links.
    """
    def __init__(self, enabled):
        super().__init__(enabled)
        self._name = "YouTube-previewer"

    @property
    def pattern(self):
        """
        Pattern to match a youtube link
        """
        return re.compile(r'^https?\:\/\/(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_\-]+)$')

    def youtube_code(self, uri):
        """
        Return the youtube video code for a video link.
        """
        match = self.pattern.match(uri)
        if match is None:
            return None
        return match[1]


    def _preview_code(self, uri, alt_text=None, hover_text=None, buildup_data=None):
        """
        Embeds the youtube video as an iframe
        """
        # pylint: disable=unused-argument
        if buildup_data is not None:
            _LOGGER.warning('YouTube preview has unused buildup data',
                            extra={'fussy':True})

        youtube_code = self.youtube_code(uri)
        youtube_html =  ('<iframe width="560" height="315"'
                         f' src="https://www.youtube.com/embed/{youtube_code}"'
                         ' title="YouTube video player" frameborder="0"'
                         ' allow="accelerometer; autoplay; clipboard-write;'
                         ' encrypted-media; gyroscope; picture-in-picture"'
                         ' allowfullscreen></iframe>')
        return youtube_html
