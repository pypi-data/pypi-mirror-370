"""
This sub module contains the BaseLink class and its child classes Link,
LibraryLink, and Image. Instead of constructing a Link or LibraryLink use
`create_link_object`. This will return the correct object type.
Image is used only for displaying images i.e. links that start with an !. For
a reference to an image use `create_link_object`.
"""

# Testing for this module is handled by test_buildup rather than directly running
# the functions as it provides a more realisic running of the objects.

import posixpath
import logging
from copy import copy
from dataclasses import dataclass
import regex as re
from marshmallow import Schema, fields, post_load, pre_load, ValidationError
from gitbuilding.buildup.files import FileInfo
from gitbuilding.buildup.quantity import Quantity
from gitbuilding.buildup.utilities import (clean_id,
                                           as_posix,
                                           raise_validation_error_as_warning,
                                           strip_internal_links)
from gitbuilding.buildup.url import translate_external

_LOGGER = logging.getLogger('BuildUp')

@dataclass
class LinkData:
    """
    A simple data class for the BuildUp data stored with a link
    the input data is validated by a marshmallow schema. This class
    has an extra validation step to check that data isn't defined for
    the wrong type of link.
    """
    category: str
    qty: Quantity
    total_qty: Quantity
    note: str
    step: bool
    make: bool
    output: bool
    bom: bool
    previewpage: bool
    zip: bool
    pattern: str
    hidden: bool
    noicons: bool
    titleimage: bool
    color: str
    _variables: dict

    @property
    def _non_part_link_types(self):
        return [self.step, self.output, self.bom, self.previewpage, self.zip, self.titleimage, bool(self.color)]

    @property
    def _part_link_data(self):
        return [self.category, self.qty, self.total_qty, self.note, self.make]

    @property
    def _zip_link_data(self):
        return [self.pattern]

    @property
    def part(self):
        """
        Read-only property to check if the part is a part link. This is
        true if the link data does not specify that the link is a step or
        output link.
        """

        return not any(self._non_part_link_types)

    @property
    def variables(self):
        """
        Return the variables for this link. This only has a functioning meaning for step links
        """
        return copy(self._variables)

    @property
    def valid(self):
        """
        Read-only that returns true if the data for the part is valid.
        """
        if sum(self._non_part_link_types) > 1:
            _LOGGER.warning('Multiple conflicting link types defined for same link.'
                            ' Ignoring all data for this link.')
            return False
        if self.step:
            if not _all_unset(self._part_link_data + self._zip_link_data):
                _LOGGER.warning('Unexpected properties in step link. Ignoring all data.')
                return False
        if self.output:
            if not _all_unset([self.category, self.total_qty, self.note] + self._zip_link_data):
                _LOGGER.warning('Unexpected properties in output link. Ignoring all data.')
                return False
        if self.bom:
            if not _all_unset(self._part_link_data + self._zip_link_data):
                _LOGGER.warning('Unexpected properties in BOM link. Ignoring all data.')
                return False
        if self.previewpage:
            if not _all_unset(self._part_link_data + self._zip_link_data):
                _LOGGER.warning('Unexpected properties in previewpage link. Ignoring all data.')
                return False
        if self.zip:
            if not _all_unset(self._part_link_data):
                _LOGGER.warning('Unexpected properties in zip link. Ignoring all data.')
                return False
            if self.pattern is None:
                _LOGGER.warning('No pattern given for zip link.')
                return False
        if self.noicons:
            if not self.bom:
                _LOGGER.warning('noicons should only be used for a bom link')
                return False
        if self._variables is not None:
            if not self.step:
                _LOGGER.warning('Variables have no meaning for this type of link.',
                                extra={'fussy':True})
        if self.hidden and not self.output:
            _LOGGER.warning('Only outputs can be set to hidden.',
                            extra={'fussy':True})
        return True

def _all_unset(values):
    for value in values:
        if value:
            return False
    return True


class LinkDataSchema(Schema):
    """
    This is the schema for the extra data that can be appended on a link
    """
    cat = fields.Str(load_default=None, allow_none=True)
    qty = fields.Str(load_default=None, allow_none=True)
    totalqty = fields.Str(load_default=None, allow_none=True)
    note = fields.Str(load_default=None, allow_none=True)
    pattern = fields.Str(load_default=None, allow_none=True)
    step = fields.Bool(load_default=False)
    make = fields.Bool(load_default=False)
    output = fields.Bool(load_default=False)
    bom = fields.Bool(load_default=False)
    previewpage = fields.Bool(load_default=False)
    zip = fields.Bool(load_default=False)
    hidden = fields.Bool(load_default=False)
    noicons = fields.Bool(load_default=False)
    titleimage = fields.Bool(load_default=False)
    color = fields.Str(load_default=None, allow_none=True)
    _variables = fields.Dict(load_default=None, allow_none=True)

    @pre_load
    def _remove_extra(self, in_data, **_):
        if not isinstance(in_data, dict):
            return in_data

        extra_args = [key for key in in_data.keys() if key not in self.fields]
        for key in extra_args:
            if key.startswith('var_'):
                if '_variables' not in in_data:
                    in_data['_variables']= {}
                in_data['_variables'][key] = in_data[key]
            else:
                _LOGGER.warning('Ignoring unknown link data key "%s"',
                                key,
                                extra={'fussy':True})
            del in_data[key]
        return in_data

    @post_load
    def _make_object(self, data, **_):
        if data['qty'] in [None, ""]:
            data['qty'] = None
        else:
            data['qty'] = Quantity(data['qty'])
        if data['totalqty'] in [None, ""]:
            data['total_qty'] = None
        else:
            data['total_qty'] = Quantity(data['totalqty'])
        if data['cat'] is None:
            data['category'] = None
        else:
            data['category'] = data['cat'].lower()
        del data['cat']
        del data['totalqty']
        link_data = LinkData(**data)
        if link_data.valid:
            return link_data
        return None

def _load_link_data(data):
    if data is None:
        return None
    try:
        return LinkDataSchema().load(data)
    except ValidationError as err:
        raise_validation_error_as_warning(err)
        return None

def _fully_normalise_link(url, page):
    """
    in the case that the page is located at 'folder/page.md' and the url is
    '../folder/path.md'. posixpath.normpath(url) does not collapse it to 'path.md'
    this will.
    """
    if url == '':
        return ''
    page_dir = posixpath.dirname(page)
    joined = posixpath.join(page_dir, url)
    joined = posixpath.normpath(joined)
    return posixpath.relpath(joined, page_dir)

def _complete_ref_style_link(linktext, link_references):
    """
    If this is a reference style link the link location is added
    from the link references
    """
    if link_references is None:
        return ""
    if linktext in link_references:
        ref_index = link_references.index(linktext)
        return link_references[ref_index].raw_linklocation
    return ""

def _is_web_link(linklocation):
    """
    Returns True if the link is a web link not a local link.
    """
    return re.match(r"^(https?:\/\/)", linklocation) is not None

def _is_from_step_link(linklocation):
    """
    Returns True if the link is a web link not a local link.
    """
    return linklocation.strip().lower() == 'fromstep'

def _library_match(linklocation):
    """
    Matches whether the link is to a part in a library:
    Returns a tuple with the library path, the output directory
    for the library and the part name. If not a library link returns
    None
    """
    # match if the part's link is in the format `abc.yaml#abc` or
    # `abc.yml#abc`
    libmatch = re.match(r"^((.+)\.ya?ml)#(.+)$", linklocation)
    if libmatch is None:
        return None
    library_path = libmatch.group(1)
    #The directory the library will write to:
    library_dir = libmatch.group(2)
    part = libmatch.group(3)
    return (library_path, library_dir, part)

@dataclass
class LinkInfo:
    """
    A simple data class for the key information defined for a link.
    Ths mostly exists to aid finding coding errors which cannot be done
    using dictionaries.
    """
    fullmatch: str
    linktext: str
    linklocation: str
    alttext: str
    buildup_data: LinkData
    overridetext: str = None

    def __post_init__(self):
        self._original_linklocation = copy(self.linklocation)
        self._make_data = None

    @property
    def original_linklocation(self):
        """
        Read only property for the link location exactly as matched
        """
        return self._original_linklocation

    @property
    def make_data(self):
        """
        Return the make_data set in the header for this part
        """
        return self._make_data

    def set_make_data(self, make_data):
        if not self.buildup_data or not self.buildup_data.make:
            return

        if self.linktext.lower() in make_data:
            data = make_data[self.linktext.lower()]
            if self.linklocation:
                _LOGGER.warning('Error processing [%s] Page cannot be set by both '
                                'make data and link!', self.linktext)
                return
            self.linklocation = data['template']
            self._make_data = data

def create_link_object(link_dict, page, link_type=1, link_references=None, make_data=None):
    """
    Will create the correct link object, either Link or LibraryLink.
    link_type input should be BaseLink.LINK_REF (=0) or BaseLink.IN_LINE_FULL
    (=1 - default) depending on whether the link is a reference or and in-line
    link. If it is a reference style in-line link, the type will automatically
    adjust to BaseLink.IN_LINE_REF (=2).
    """

    link_dict['buildup_data'] = _load_link_data(link_dict['buildup_data'])
    link_info = LinkInfo(**link_dict)

    if make_data:
        link_info.set_make_data(make_data)

    if _is_web_link(link_info.linklocation):
        weblink = True
    else:
        weblink = False
        link_info.linklocation = as_posix(link_info.linklocation, warn=True)

    if link_info.buildup_data is None:
        output = False
        bom = False
        previewpage = False
    else:
        output = link_info.buildup_data.output
        bom = link_info.buildup_data.bom
        previewpage = link_info.buildup_data.previewpage

    if link_type == BaseLink.LINK_REF:
        if link_info.buildup_data is not None and link_info.buildup_data.qty is not None:
            _LOGGER.warning('Specifying the quantity of a part used in a link reference'
                            'is not permitted. Quantity should be specified in the text.')
            link_info.buildup_data.qty = None
    else:
        if link_info.linklocation == "":
            link_type = BaseLink.IN_LINE_REF
            link_info.linklocation = _complete_ref_style_link(link_info.linktext,
                                                              link_references)

    if not (output or bom or previewpage):
        if weblink:
            return Link(link_info, page, link_type)
        if _is_from_step_link(link_info.linklocation):
            return FromStepLink(link_info, page, link_type)
        lib_match = _library_match(link_info.linklocation)
        if lib_match is not None:
            return LibraryLink(link_info, page, link_type, lib_match)
    return Link(link_info, page, link_type)

class BaseLink():
    """
    A base class for a link. Can is used to do a number of things from completing
    reference style links. Translating links to be relative to different pages
    and generating the output FileInfo objects. Do not use it directly. Use a the
    child class:
    * Image
    or the function
    the function `create_link_object`. This  will assign the correct type between `Link`,
    and `LibraryLink`.
    """
    LINK_REF = 0
    IN_LINE_FULL = 1
    IN_LINE_REF = 2

    def __init__(self, link_info, page, link_type):
        self._weblink = False
        self._page = page
        self._link_type = link_type
        self._link_info = link_info

        #Output links can't have a location, this may change.
        self._check_location()

        #If it is a an inline part link or output it must have a quantity!
        if link_type != self.LINK_REF and (self.is_part or self.is_output):
            if self.buildup_data.qty is None:
                linktype = 'part' if self.is_part else 'output'
                _LOGGER.warning('The %s link for %s has no qty specified.',
                                linktype,
                                self._link_info.linktext)

    def _check_location(self):
        """
        Checks the location is set correctly for the type of BuildUp data specified.
        For example "output" and "bom" links cannot have a location specified.
        """
        #Output links can't have a location, this may change.
        if not (self.is_output or self.is_bom):
            return

        if self._link_info.linklocation != '':
            if self.is_output:
                _LOGGER.warning('A target should not be specified when defining an'
                                ' output, it will automatically link to this page.')
            else:
                _LOGGER.warning('A target should not be specified when creating a'
                                ' link to a BOM page. The target will be generated'
                                ' automatically')

    def __eq__(self, obj):
        return obj == self._link_info.linktext

    @property
    def is_inline_ref(self):
        """
        Return true if link is an inline reference (i.e. is just the square bracket portion)
        """
        return self._link_type == self.IN_LINE_REF

    @property
    def weblink(self):
        """
        Return true if link is web link
        """
        return self._weblink

    @property
    def is_image(self):
        """
        Return true if link is image
        """
        return False

    @property
    def is_buildup(self):
        """
        Return true if link is a buildup link. Note that a link to a
        preview page is considered a plain link as there is no extra
        metadata
        """
        if self.to_preview_page:
            return False
        return self.buildup_data is not None

    @property
    def page(self):
        """
        The name of the page the link is defined on
        """
        return self._page

    @property
    def fullmatch(self):
        """
        The full regex match for the link in the original BuildUp
        """
        return self._link_info.fullmatch

    @property
    def overridetext(self):
        """
        The text that overrides the main text.
        """
        return self._link_info.overridetext

    @property
    def linktext(self):
        """
        The text inside the square brackets for the link in BuildUp
        """
        return self._link_info.linktext

    @property
    def raw_linklocation(self):
        """The raw input link location. Reference style links have
        location completed"""
        return self._link_info.linklocation

    @property
    def original_linklocation(self):
        """The raw input link location without reference style links 
        completed"""
        return self._link_info.original_linklocation

    @property
    def link_rel_to_page_no_preview(self):
        """
        Returns the link address relative to the BuildUp page. Never returns
        the link to a preview page
        """
        return _fully_normalise_link(self.raw_linklocation, self._page)

    @property
    def link_rel_to_page(self):
        """
        Link address relative to the BuildUp page
        """
        location = self.link_rel_to_page_no_preview
        if location == "":
            return ""
        if self.to_preview_page:
            return posixpath.splitext(location)[0]+".md"
        return location

    @property
    def link_rel_to_root_no_preview(self):
        """
        Location of the link relative to the root BuildUp directory. Never returns
        the link to a preview page
        """
        location = self.link_rel_to_page_no_preview
        if location == "":
            return ""
        page_dir = posixpath.dirname(self._page)
        root_link = posixpath.join(page_dir, location)
        root_link = posixpath.normpath(root_link)
        return root_link

    @property
    def link_rel_to_root(self):
        """
        Link address relative to the BuildUp page
        """
        location = self.link_rel_to_root_no_preview
        if location == "":
            return ""
        if self.to_preview_page:
            return posixpath.splitext(location)[0]+".md"
        return location

    def link_needed_on_page(self, page):
        """Return what would be need to be specified on a given page to link to
        the same location"""
        page_dir = posixpath.dirname(page)
        if self.weblink:
            return self.raw_linklocation
        if not page_dir:
            return self.link_rel_to_root_no_preview
        if self.link_rel_to_root_no_preview:
            return posixpath.relpath(self.link_rel_to_root_no_preview, page_dir)
        return ""

    @property
    def location_undefined(self):
        """
        Returns a boolean value stating whether the link is undefined
        """
        return self.link_rel_to_page == ""

    @property
    def alttext(self):
        """
        Returns the alt-text of the link
        """
        return self._link_info.alttext

    @property
    def buildup_data(self):
        """
        Returns the LinkData objects for the link metadata
        """
        return self._link_info.buildup_data

    @property
    def make_data(self):
        """
        Returns the dictionary for any make_data for this link. Applies
        only to make links using make_data rather than a page
        """
        return self._link_info.make_data

    @property
    def is_plain(self):
        """
        Read only boolean. Returns true for links with no BuildUp meta data
        """
        return self.buildup_data is None

    @property
    def is_part(self):
        """
        Read only boolean. Returns true for links with BuildUp that describe
        part/tool usage.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.part

    @property
    def is_step(self):
        """
        Read only boolean. Returns true for links with BuildUp that describe
        another step in the documentation.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.step

    @property
    def is_make(self):
        """
        Read only boolean. Returns true for links with BuildUp that describe
        describe the use of a part that should be made in an earlier step.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.make

    @property
    def is_output(self):
        """
        Read only boolean. Returns true for links with BuildUp that describe
        an part created on this page.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.output

    @property
    def is_bom(self):
        """
        Read only boolean. Returns true for links to bill of materials pages.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.bom

    @property
    def is_zip(self):
        """
        Read only boolean. Returns true for links to automatically created zips.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.zip

    @property
    def zip_pattern(self):
        """
        The glob pattern used to determine which files to zip
        """
        if self.is_zip:
            return self.buildup_data.pattern
        return None

    @property
    def to_preview_page(self):
        """
        Read only boolean. Returns true for links to preview pages.
        """
        if self.is_plain or self.is_image:
            return False
        return self.buildup_data.previewpage

    @property
    def content_generated(self):
        """Returns true if the content is generated in build up and otherwise
        return false"""
        #Note the link_rel_to_page has converted library links into .md links
        rel_link = strip_internal_links(self.link_rel_to_page_no_preview)
        if rel_link.endswith('.md'):
            return True
        if self.raw_linklocation.startswith('{{'):
            return True
        if self.is_zip:
            return True
        return False

    def as_output_file(self, external_dirs, files_to_zip=None):
        """ Returns the link as an FileInfo object.
        If the link is to a buildup file `None` is returned as this is generated
        elsewhere.
        `files_to_zip` input should only be used for zip links
        """
        if self.is_zip:
            return FileInfo(self.link_rel_to_root_no_preview,
                            dynamic_content=True,
                            files_to_zip=files_to_zip)
        if files_to_zip is not None:
            raise ValueError('files_to_zip should only be set for zip links')
        if self.content_generated or self.location_undefined:
            return None
        path = self.link_rel_to_root_no_preview
        if not path.startswith(".."):
            return FileInfo(path)
        on_disk = path
        path = translate_external(on_disk, external_dirs)
        return FileInfo(path, location_on_disk=on_disk)

    def link_ref_md(self, url_translator):
        """
        Returns a plain markdown link reference for the link.
        Input is a URLTranslator object
        """
        location = self.output_url(url_translator)
        return f'[{self.linktext}]:{location} "{self.alttext}"'

    def link_md(self, url_translator=None, text_override=None):
        """
        Returns a plain markdown link for the link object, i.e. the part
        in the text not the reference.
        If this is a link reference object None is returned.
        Input is a URLTranslator object
        Optionally the link text can be overridden, this doesn't work for
        a reference style link as it would break it.
        """

        # This may be confusing. overridetext is from a preceding [] in the original
        # markdown. text_override input GitBuilding is forcing an override for a differenet
        # reason
        override_md = f"[{self.overridetext}]" if self.overridetext else ""

        if self.is_output:
            anchor_name = clean_id(self.linktext)
            text = self.overridetext if self.overridetext else self.linktext
            text = '' if self.buildup_data.hidden else text
            return f'<a name="output__{anchor_name}"></a>{text}'
        if self._link_type == self.LINK_REF:
            return None
        if self._link_type == self.IN_LINE_REF:
            return f'{override_md}[{self.linktext}]'

        # A full inline link
        if url_translator is None:
            location = self.raw_linklocation
        else:
            location = self.output_url(url_translator)
        if text_override is None:
            text = self.linktext
        else:
            override_md = ""
            text = text_override

        target_format = url_translator.target_format if url_translator is not None else None
        kramdown = ""
        if target_format == "html":
            if self._weblink:
                kramdown = '{:target="_blank"}'
        elif target_format == "pdf":
            if location.startswith("#"):
                kramdown = '{: class="internal-link"}'
            # This needs improving. Weblinks should become footnotes
            # links to files or blank links should either warn or
            # do something usefil

        return f'{override_md}[{text}]({location} "{self.alttext}"){kramdown}'

    def output_url(self, url_translator):
        """
        Uses url_translator a URLTranslator object
        to generate a link to the correct place.
        """
        return url_translator.translate(self)


class Link(BaseLink):
    '''
    A link to another file in the Documentation directory. See also LibraryLink.
    This class should always be created with `create_link_object` which will
    create the correct link type. The child class Image can be created directly
    with its constructor.
    '''

    def __init__(self, link_info, page, link_type):
        super().__init__(link_info, page, link_type)

        #Note that weblink is not subclassed so that Image doesn't need two classes
        self._weblink = _is_web_link(link_info.linklocation)
        if self._weblink:
            if self.is_step:
                _LOGGER.warning('A step link must link to a buildup page')
                self._link_info.buildup_data.step = False
        else:
            if self._link_type == self.LINK_REF:
                if self._link_info.linklocation.lower() == "missing":
                    self._link_info.linklocation = ''
                    return

            if posixpath.isabs(self._link_info.linklocation):
                _LOGGER.warning('Absolute path "%s" removed, only relative paths are supported.',
                                self._link_info.linklocation)
                self._link_info.linklocation = ""
            if self.is_step and self._link_info.linklocation == '':
                _LOGGER.warning('A step link must link to a buildup page')
                self._link_info.buildup_data.step = False
            self._link_info.linklocation = self._link_info.linklocation

    @property
    def internal_link(self):
        """
        Return true if is an internal link to this page. i.e. url starts with #
        """
        return self.link_rel_to_page.startswith('#')

    @property
    def link_rel_to_root(self):
        """
        Location of the link relative to the root BuildUp directory
        """
        if self._weblink:
            return self.raw_linklocation
        if self.internal_link:
            return self._page+self.link_rel_to_page
        return super().link_rel_to_root

    @property
    def link_rel_to_page(self):
        """
        Location of the link relative to the page
        """
        if self._weblink:
            return self.raw_linklocation
        return super().link_rel_to_page

    def as_output_file(self, external_dirs, files_to_zip=None):
        """ Returns the link as an FileInfo object.
        If the link is to a buildup file `None` is returned as this is generated
        elsewhere.
        """
        if self._weblink or self.internal_link:
            return None
        return super().as_output_file(external_dirs, files_to_zip)

    def output_url(self, url_translator):
        """
        Uses url_translator a URLTranslator object
        to generate a link to the correct place.
        """
        if self._weblink:
            return self.raw_linklocation
        return super().output_url(url_translator)

    @property
    def content_generated(self):
        """Returns true if the content is generated in build up and otherwise
        return false"""
        if self._weblink:
            return False
        return super().content_generated

class FromStepLink(BaseLink):
    """
    A child class of BaseLink for links to parts produced in previous documentation steps
    """
    def __init__(self, link_info, page, link_type):
        super().__init__(link_info, page, link_type)
        self._resolved = False
        if self.is_step:
            _LOGGER.warning('When linking to "FromStep" the link cannot be a step link')
            self._link_info.buildup_data.step = False

    def reset(self):
        """
        Resets the link to an unresoved state
        """
        self._resolved = False

    def resolve(self, outputs):
        """
        This function resolves the URL for a part defined in a previous step.
        Input is all of the outputs defined in prvious steps. Nothing is returned
        from this method. If the corresponing part is located FromStepLink.resolved
        will be set to True, if not a warning will be logged.
        """
        output_names = [link.linktext.lower() for link in outputs]
        if self.linktext.lower() in output_names:
            index = output_names.index(self.linktext.lower())
            page_dir = posixpath.dirname(self.page)
            self._link_info.linklocation = posixpath.relpath(outputs[index].page, page_dir)
            self._resolved = True
        else:
            _LOGGER.warning('The step that defines [%s] cannot be found', self.linktext)

    @property
    def resolved(self):
        """
        Boolean property. Returns true if the step that defines the output has been
        resolved.
        """
        return self._resolved

    @property
    def link_rel_to_page(self):
        """
        Return the link relative to the page if it is resolved
        """
        if not self.resolved:
            return ""
        return super().link_rel_to_page

    def link_needed_on_page(self, page):
        """
        For a FromStepLink this always returns "fromstep"
        """
        return "fromstep"


class LibraryLink(BaseLink):
    """
    A child class of BaseLink for links to parts in Libraries. It translates
    the from the link in the library to the final markdown page. Then other
    translations happen as standard.
    """

    def __init__(self, link_info, page, link_type, lib_match):
        super().__init__(link_info, page, link_type)
        if self.is_step:
            _LOGGER.warning('A step link must link to a buildup page')
            self._link_info.buildup_data.step = False
        libname = _fully_normalise_link(lib_match[1], page)
        #The id/key in the part library
        self._part_id = lib_match[2]
        self._output_rel_to_page = posixpath.join(libname, self._part_id+'.md')
        page_dir = posixpath.dirname(page)
        root_link = posixpath.join(page_dir, lib_match[0])
        #This is the libray relative to the root
        self._library_file = posixpath.normpath(root_link)


    @property
    def link_rel_to_page_no_preview(self):
        """
        Location of the output part page relative to the BuildUp page
        """
        return self._output_rel_to_page

    def link_needed_on_page(self, page):
        """
        Return the link needed to link to this library item on a given page
        """
        page_dir = posixpath.dirname(page)
        library = posixpath.relpath(self._library_file, page_dir)
        return library+"#"+self._part_id

    @property
    def library_location(self):
        """
        Returns a tuple of the library file (relative to the root dir) and the
        part name.
        """
        return (self._library_file, self._part_id)

    @property
    def content_generated(self):
        """
        Always returns true as LibraryLinks always generate content
        """
        return True

class Image(Link):
    """
    A child class of Link to deal with the subtle differences of Links
    and Images in markdown.
    """

    def __init__(self, image_dict, page, link_references=None):

        image_dict['buildup_data'] = _load_link_data(image_dict['buildup_data'])
        image_dict["linktext"] = ''
        image_dict["linklocation"] = image_dict["imagelocation"]
        self._hovertext = image_dict["hovertext"]
        del image_dict["imagelocation"]
        del image_dict["hovertext"]
        link_info = LinkInfo(**image_dict)
        if link_info.linklocation == "":
            link_type = BaseLink.IN_LINE_REF
            link_info.linklocation = _complete_ref_style_link(link_info.linktext,
                                                              link_references)
        else:
            link_type = BaseLink.IN_LINE_FULL

        #Image is not created by create_link_object() so need to check url is posix
        if not _is_web_link(link_info.linklocation):
            link_info.linklocation = as_posix(link_info.linklocation, warn=True)

        super().__init__(link_info,
                         page=page,
                         link_type=link_type)

    @property
    def is_title_image(self):
        """
        Return whether this is the title image for the PDF.
        """
        if self.buildup_data is None:
            return False
        return self.buildup_data.titleimage

    @property
    def is_image(self):
        """
        Return whether this is an image
        """
        return True

    @property
    def image_rel_to_page(self):
        """
        Location of the image file relative to the BuildUp page
        """
        return self.link_rel_to_page

    @property
    def image_rel_to_root(self):
        """
        Location of the image file relative to the root BuildUp directory
        """
        return self.link_rel_to_root

    @property
    def hovertext(self):
        """
        Returns the hover text of the link
        """
        return self._hovertext

    def _library_match(self):
        """
        This overrides the Link version of this functions and just
        returns false as an image cannot be a library.
        """
        return None

    def image_md(self, url_translator):
        """
        Returns a the plain markdown for the image
        """
        location = self.output_url(url_translator)
        return f'![{self.alttext}]({location} "{self.hovertext}")'

    def link_md(self, url_translator=None, _=None):
        """
        This should not be used for an image.
        """
        raise NotImplementedError("For links use image_md")
