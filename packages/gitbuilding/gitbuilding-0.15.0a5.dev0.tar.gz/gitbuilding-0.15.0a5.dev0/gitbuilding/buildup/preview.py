"""
Define html previews for file types. This will set the HTML to display
a particular file type or web-link. If this is set you can display a the
file or link either by using markdown image syntax.
"""

class Previewer():
    """
    Base class for previewers this should be sub-classed
    for use.
    """

    def __init__(self, enabled):
        self._name = "Unknown_previewer"
        self._enabled = enabled
        self._drop_dir = "misc"
        self._create_preview_page_when_enabled = False

    @property
    def pattern(self):
        """
        This is not implemented for the base class. For sub-classes this should return
        a compiled regex for URIs that should be previewed
        """
        return NotImplemented

    def can_preview(self, uri):
        """
        Return whether this uri can be previewed
        """
        # pylint: disable=no-member
        if self.pattern is NotImplemented:
            raise NotImplementedError("Previewer is a base class that should be subclassed"
                                      " rather than used as is")
        return self.pattern.match(uri) is not None

    def display_code(self, uri, alt_text, hover_text, buildup_data):
        """
        Returns
        """
        if self._enabled:
            return self._preview_code(uri, alt_text, hover_text, buildup_data)
        return self._static_markdown(uri, alt_text, hover_text, buildup_data)

    def _preview_code(self, uri, alt_text, hover_text, buildup_data=None):
        """
        This is not impemented for the base class. For sub-classes this should return
        a the HTML to preview the input URI
        """
        # pylint: disable=unused-argument
        return NotImplemented

    def _static_markdown(self, uri, alt_text, hover_text, buildup_data=None):
        """
        This returns the markdown to replace the image syntax with if the previewing is
        not enabled. This will just be a link to the URI
        """
        # pylint: disable=unused-argument
        return f'[{alt_text}]({uri} "{hover_text}")'

    @property
    def name(self):
        """
        Name of the previewer
        """
        return self._name

    @property
    def dir_for_dropped_files(self):
        """
        Directory where dropped files of this type are saved
        """
        return self._drop_dir

    @property
    def create_preview_page(self):
        """
        Return whether preview pages should be created for this type of file/link
        """
        return self._create_preview_page_when_enabled and self._enabled

    def preview_page_uri(self, uri):
        """
        Return the preview page uri
        """
        return uri+"preview.md"

    def preview_page_content(self, uri):
        """
        Return the markdown content of the preview page.
        """
        return f"No preview set for {uri}"
