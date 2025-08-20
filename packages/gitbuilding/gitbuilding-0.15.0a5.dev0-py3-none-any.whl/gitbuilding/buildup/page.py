"""
This submodule deals with BuildUp pages. A Page object is created for each markdown
(buildup) file in the documentation directory.
"""

from typing import Optional
import posixpath
import logging
from copy import copy, deepcopy

import regex as re

from gitbuilding.buildup.link import FromStepLink
from gitbuilding.buildup.parts import UsedPart
from gitbuilding.buildup.partlist import PartList
from gitbuilding.buildup.buildup import BuildUpParser
from gitbuilding.buildup.files import FileInfo
from gitbuilding.buildup import utilities
from gitbuilding.buildup.qaqc import QaQcBlock, QaQcStartPage

_LOGGER = logging.getLogger('BuildUp')

def notify_logger(wrapped_func):
    """
    Notifies the logger of the page being processed
    """
    def wrapper(*args, **kwargs):
        _LOGGER.info('Changing page', extra={'set_active_page': args[0].filename})
        result = wrapped_func(*args, **kwargs)
        _LOGGER.info('Changing page', extra={'set_active_page': None})
        return result
    return wrapper

class Page:
    """
    This class represents one BuildUp page. It can be used to: track its relation to
    other pages using the step_tree; to count the parts in the page; and to export a
    pure markdown page.
    """
    AS_MARKDOWN = 0
    AS_CSV = 1

    def __init__(self, file_obj, doc):
        self._included_in = []
        self._variations = []
        self._file_obj = deepcopy(file_obj)
        self._doc = doc
        self._overloaded_path = None
        self._replace_links = None
        self._meta_info = {}

        self._part_list = PartList(self._doc.config)
        self._all_parts = None
        self._bom_pages = None
        self._title_image = None

        self._child_make_pages = []
        self._step_tree = None
        self._set_parser(self.get_raw())

        self._qaqc_start_page = None

    def __repr__(self):
        return f'<Page: {self.filepath}>'

    @property
    def summary(self):
        """
        Page summary is either the title or the first 14 characters plus "..."
        """
        if self.title != "":
            return self.title
        if len(self.raw_md) > 17:
            return self.raw_md[:14]+'...'
        return self.raw_md

    @property
    def variables(self):
        """
        Return the variables set for this page (None as not VariationPage)
        """
        return None

    @property
    def raw_md(self):
        """
        Read only property that returns the raw markdown of the page (without frontmatter)
        """
        return self._parser.raw_md

    @property
    def preprocessed_md(self):
        """
        Read only property that returns the markdown of the page after executing any
        include statements
        """
        return self._parser.preprocessed_md

    @property
    def reprocess_needed(self):
        """
        Return true if this page or any of its variations need reporcessing. This
        is because they tried to include a page that had not yet processed its includes.
        """
        for variation in self._variations:
            if variation.reprocess_needed:
                return True
        return self._parser.reprocess_needed

    @property
    def metadata(self):
        """
        Read only property that returns the metadata in from the fontmatter
        """
        return self._parser.metadata

    @property
    def part_data(self):
        """
        Read only property that returns the part data from the front matter.
        """
        return self._parser.part_data

    @property
    def details(self):
        """
        Read only property that returns the page details from the front matter.
        """
        return self._parser.details

    @property
    def tags(self):
        """
        Read only property that returns the tags for this page
        """
        # Return tags from metadata but ensure it is a list
        if not "Tags" in self.metadata:
            return []
        tags = self.metadata["Tags"]
        if isinstance(tags, list):
            return tags
        return [tags]

    @property
    def title(self):
        """
        Read only property that returns the title of the page as read
        from the fist H1 level title in page.
        """
        return copy(self._parser.get_title())

    @property
    def filepath(self):
        """
        Read only property that the full filepath of the page relative to
        the root directory of the documentation
        """
        return copy(self._file_obj.path)

    @property
    def pagedir(self):
        '''
        The directory of the input page
        '''
        return posixpath.dirname(self.filepath)

    @property
    def filename(self):
        '''
        The filename of the input page and output pages
        '''
        return posixpath.basename(self.filepath)

    @property
    def counted(self):
        '''
        Sets whether the main part list has been counted (this happens after running
        count_page)
        '''
        return self._all_parts is not None

    @property
    def part_list(self):
        """
        Returns the part list for the page this is a PartList object.
        """
        return self._part_list

    @property
    def steps(self):
        """
        Returns a list of all the steps in the page (as the url relative to the root
        of the project). This is only the steps defined in the page. Not the full tree.
        This comes directly from the parser there is no garuntee that the the url
        refers to a valid page!
        """
        return self._parser.steps

    @property
    def outputs(self):
        """
        Returns a list of all the output links. This directly by the buildUp
        parser. It is seperate from the CreatedPart objects in the partlist
        as the partlists as the FromStep links need to be resolved before
        making the part list.
        """
        return self._parser.outputs

    @property
    def images(self):
        """
        Returns a list of Image objects, one for each image
        """
        return self._parser.images

    @property
    def title_image(self):
        """
        The title image for this page if it has one. Else None is returned
        """
        return self._title_image

    @property
    def plain_links(self):
        """
        Returns a list of Link objects, one for each link that is not a build up link
        """
        return self._parser.plain_links

    @property
    def make_links(self):
        """
        Returns a list of Link objects, one for each make link
        """
        return self._parser.make_links

    @property
    def all_links(self):
        """
        Returns a list of Link objects, one for each link in the page.
        Doesn't return images. See all_links_and_images()
        """
        return self._parser.all_links

    @property
    def all_links_and_images(self):
        """
        Returns a list of Link and Image objects, one for each link/image
        in the page.
        """
        return self._parser.all_links_and_images

    @property
    def all_link_refs(self):
        """
        Returns a list of all link references in the page.
        """
        return self._parser.link_refs

    @property
    def contains_qaqc_blocks(self):
        """
        True if page contains qaqc blocks.
        """
        return bool(self._parser.qaqc_blocks)

    def get_qaqc_blocks(self, warn=True) -> QaQcBlock:
        """Return the list of QAQC blocks.
        
        This revalidates the blocks. Set warn=False to skip warning on later runs,
        instead will error which needs to be caught.
        """
        blocks = []
        for i, block in enumerate(self._parser.qaqc_blocks):
            form_id = self.id_code + f"--qaqc-sec-{i}"
            blocks.append(QaQcBlock(block, form_id, warn))
        return blocks

    def reprocess_md(self):
        """
        Reprocess the markdown and the markdown of this page and all of its
        variations
        """
        for variation in self._variations:
            variation.reprocess_md()
        self._set_parser(self.get_raw())

    def get_variation(self, variable_list):
        """Get a variation of this page with the correct variable list"""
        if variable_list is None:
            return self
        page_variables = {key:var for key,var in variable_list.items() if key.startswith(("var_", "make_"))}
        if not page_variables:
            return self
        for variation in self._variations:
            if variation.matches_variables(page_variables):
                return variation
        variation = VariationPage(self._file_obj, self._doc, self, page_variables)
        self._variations.append(variation)
        return variation

    def get_bom_page(self, as_filelist=False):
        """
        Returns the link to the bill of materials pages, or None if there is not
        a bom-link on the page. If as_filelist is True a list of FileInfo objects
        for the bill of materials is returned (if it has been created).
        If None is returned for as_filelist=True but not when as_filelist=False,
        this means that page.generate_output has not been run.
        """
        if as_filelist:
            return self._bom_pages
        return self._bom_urls() if self._has_bom_page() else None

    def _has_bom_page(self):
        bom_links = self._parser.bom_links
        bom_links_oldstyle = self._parser.bom_links_dep
        return len(bom_links) + len(bom_links_oldstyle) > 0

    def _bom_urls(self):
        urls = []
        for filetype in [self.AS_MARKDOWN, self.AS_CSV]:
            urls.append(self._bom_url(filetype))
        return urls

    def _bom_url(self, filetype=None):
        if filetype is None:
            filetype = self.AS_MARKDOWN

        if filetype == self.AS_MARKDOWN:
            return self.filepath[:-3] + "_BOM.md"
        if filetype == self.AS_CSV:
            return self.filepath[:-3] + "_BOM.csv"
        raise ValueError("Filetype for BOM URL not recognised.")

    def get_qaqc_start_page_and_json(self)->Optional[list[FileInfo]]:
        """Return a list of FileInfo objects for the QAQC start page and json.
        
        Return None if no start page.
        """
        if self._qaqc_start_page is None:
            return None
        page = FileInfo(self._qaqc_start_page.url,
                        title=self._qaqc_start_page.title,
                        dynamic_content=True,
                        content=self._qaqc_start_page.as_md(self._url_translator))
        json_file = FileInfo(self._qaqc_start_page.json_url,
                             dynamic_content=True,
                             content=self._qaqc_start_page.full_form_json)
        return [page, json_file]

    @property
    def id_code(self):
        """
        A unique ID code
        """
        # Remove .md extension and replace unsafe characters
        return re.sub(r"[^a-zA-Z1-9-]", "--", self.filepath[:-3])

    @property
    def _url_translator(self):
        if self._overloaded_path is None:
            filepath = self.filepath
        else:
            filepath = self._overloaded_path
        return self._doc.url_rules.create_translator(filepath,
                                                     replace_links=self._replace_links)

    @property
    def _part_url_translator(self):
        if self._overloaded_path is None:
            filepath = self.filepath
        else:
            filepath = self._overloaded_path
        return self._doc.url_rules.create_translator(filepath,
                                                     part_translator=True,
                                                     replace_links=self._replace_links)

    @notify_logger
    def _set_parser(self, raw_text, live_edit=False):
        self._parser = BuildUpParser(raw_text, self.filepath, self._doc, live_edit=live_edit)

    @property
    def included_in_another_page(self):
        """
        Return whether this page is included in another page
        """
        return len(self._included_in) > 0

    @property
    def included_by(self):
        """
        Return the pages that include this page
        """
        return self._included_in

    @property
    def includes(self):
        """
        Return the pages that this page includes
        """
        return self._parser.includes

    def set_as_included(self, path):
        """
        Set that this page has been included in another page with path as input
        """
        if path not in self._included_in:
            self._included_in.append(path)

    def rebuild_within(self, within_page, md, overload_path=None):
        """
        Rebuild this page within another page that incudes it
        """
        self._set_parser(md, live_edit=True)
        for variation in self._variations:
            variation.live_reparse(md)
        return within_page.rebuild(within_page.raw_md, overload_path)

    def rebuild(self, md, overload_path=None):
        """
        This is to replace the raw text and rebuild.
        This can be used to live edit a single page.
        md is the input markdown to use instead of the pages markdown
        overload_path is used to overload the path input to the
          URL_Translator. This is useful if you are displaying the
          live edited text and a different URL.
        """

        self._part_list = PartList(self._doc.config)
        self._all_parts = None
        self._step_tree = None
        self._bom_pages = None

        self._set_parser(md, live_edit=True)

        self.get_step_tree()
        self.count()

        if self._doc.page_order.number_of_paths == 0:
            pagelist = []
        elif self._doc.page_order.number_of_paths == 1:
            pagelist = self._doc.page_order.pagelists[0]
        else:
            # If multiple paths find which path this page is on, if not on any
            # use a misc one as this is only for live editing and shouldn't affect
            # things
            for trial_pagelist in self._doc.page_order.pagelists:
                pagelist = trial_pagelist
                if self in pagelist:
                    break
        result, meta = self.generate_output(pagelist, overload_path)
        return result, meta

    def __eq__(self, other):
        """
        Checks for equality using the file name. Used to find pages in lists.
        """
        return self.filepath == other

    def get_raw(self):
        """
        Returns the raw BuildUp file contents.
        """
        return self._file_obj.content

    def _resolve_from_step_links(self, pagelist):
        """
        Look for outputs in previous pages
        """
        links_and_refs = self._parser.all_links+self._parser.link_refs
        fs_links = [link for link in links_and_refs if isinstance(link, FromStepLink)]
        if len(fs_links) == 0:
            return
        if self not in pagelist:
            if not self.included_in_another_page:
                _LOGGER.warning('Cannot reference a part using FromStep on a page that is '
                                'not in the step tree.')
            return

        index = pagelist.index(self)
        prev_pages = []
        for page_entry in (pagelist[:index]):
            page_obj = self._doc.get_page_by_path(page_entry.path)
            page_obj = page_obj.get_variation(page_entry.variables)
            prev_pages.append(page_obj)
        outputs = []
        for page in prev_pages:
            outputs += page.outputs
        for from_step_link in fs_links:
            from_step_link.resolve(outputs)

    def _reset_from_step_links(self):
        fs_links = [link for link in self._parser.all_links if isinstance(link, FromStepLink)]
        for from_step_link in fs_links:
            from_step_link.reset()

    def register_make_page(self, make_page):
        """
        Register that this page is the parent page of a "make page". A make page
        is one created by a make-link. The make link will not be on this page,
        but on steps called in this page.
        """
        self._child_make_pages.append(make_page)

    @notify_logger
    def count(self):
        """
        Counts all of the part on the page and puts them into a PartList object
        """
        if self.counted:
            return

        for output in self.outputs:
            self._part_list.count_link(output)

        part_links = self._parser.reference_defined_parts + self._parser.inline_parts
        for part_link in part_links:
            self._part_list.count_link(part_link)

        for part in self._part_list.used_parts:
            if part.linklocation == '' and not part.from_step:
                _LOGGER.warning('"%s" has no link specified',
                                part.name,
                                extra={'fussy':True})

        self._all_parts = PartList(self._doc.config)

        self._all_parts.merge(self._part_list, multiply_by=self.part_list_multiplier)

        child_pages = copy(self._child_make_pages)
        for step_link in self._parser.step_links:
            step_variables = step_link.buildup_data.variables
            step_page = self._doc.get_page_by_path(step_link.link_rel_to_root,
                                                   variables=step_variables)
            if step_page is not None:
                child_pages.append(step_page.get_variation(step_variables))

        for child_page in child_pages:
            # if step page is not already counted it will be counted when accessing
            # all parts property
            self._all_parts.merge(child_page.all_parts)

    @property
    def part_list_multiplier(self):
        return None

    @property
    def all_parts(self):
        """
        Returns PartList of of all parts for the page and all steps the page references.
        If the page has not yet been counted it will run Page.count.
        """

        if not self.counted:
            self.count()
        return self._all_parts

    @property
    def is_pdf_front_page(self):
        if self._doc.config.target_format != "pdf":
            return False

        for pagelist in self._doc.page_order.pagelists:
            if self == pagelist[0]:
                return True
        return False

    def _get_title_subheading(self):
        return ""

    def _replace_title(self, processed_text):
        match = self._parser.get_title_match()
        if self == self._doc.landing_page:
            if self._doc.config.remove_landing_title:
                processed_text = processed_text.replace(match, "", 1)
        else:
            #Add title subheading if applicable
            subheading = self._get_title_subheading()
            rep_txt = match+subheading
            processed_text = processed_text.replace(match, rep_txt, 1)
        return processed_text

    def _replace_special_blockquotes(self, processed_text):
        is_html = self._doc.config.target_format != "md"
        for block, rep_block in self._parser.get_special_blockquotes(html_blocks=is_html):
            processed_text = processed_text.replace(block, rep_block)
        return processed_text

    def _replace_qaqc_blocks(self, processed_text, pagelist):
        is_html = self._doc.config.target_format != "md"

        if qaqc_blocks := self.get_qaqc_blocks():
            if not is_html:
                log_msg = ("QAQC blocks are written in HTML even though the output "
                           "format is markdown")
                _LOGGER.warning(log_msg)
            for block in qaqc_blocks:
                if pagelist:
                    build_id = self._doc.get_page_by_path(pagelist[0]).id_code
                else:
                    build_id = "--orphaned--"
                    _LOGGER.warning("QAQC blocks must be on pages on a step tree.")
                rep_block = block.as_html(build_id)
                processed_text = processed_text.replace(block.md, rep_block)
        return processed_text

    def _write_bom(self, processed_text, pagelist, replace_links):
        """
        Write the bill of the materials into text and links to the bill of materials
        page if required. Currently also builds the BOM page - split later
        """
        # Add all BOMs into the page
        boms = self._parser.inline_boms
        if len(boms) > 0:
            no_links = self._doc.config.target_format == "pdf"
            bom_text = self._all_parts.bom_md(self._doc.config.page_bom_title,
                                              self._part_url_translator,
                                              exclude_refs=self._part_list,
                                              no_links=no_links)
            if self._doc.config.target_format != "md":
                bom_text = f'<div markdown="1" class="pagebom">{bom_text}</div>'
        for bom in boms:
            processed_text = processed_text.replace(bom, bom_text)

        # Add links to bill of materials page and make page
        if self._has_bom_page():
            self._bom_pages = self.make_bom_page(pagelist, replace_links)
            bom_links = self._parser.bom_links
            bom_links_oldstyle = self._parser.bom_links_dep
            for bomlink in bom_links:
                rep_text = self._bom_link_md(bomlink.linktext)
                processed_text = processed_text.replace(bomlink.fullmatch, rep_text)
            for bomlink in bom_links_oldstyle:
                bom_url = self._url_translator.simple_translate(self._bom_pages[0].path)
                processed_text = processed_text.replace(bomlink, f"{bom_url}")
        return processed_text

    def _bom_link_md(self, linktext):
        bom_url = self._url_translator.simple_translate(self._bom_pages[0].path)
        md_link = f'[{linktext}]({bom_url})'
        if self._doc.config.target_format == "pdf":
            return md_link

        bom_url_csv = self._url_translator.simple_translate(self._bom_pages[1].path)
        html_icon_url = self._url_translator.simple_translate('static/Icons/html.png')
        csv_icon_url = self._url_translator.simple_translate('static/Icons/csv.png')
        html_icon_md = f'![HTML]({html_icon_url} "HTML Bill of Materials")'+'{: .smallicon}'
        csv_icon_md = f'![CSV]({csv_icon_url} "CSV Bill of Materials")'+'{: .smallicon}'
        return f"{md_link} ([{html_icon_md}]({bom_url}), [{csv_icon_md}]({bom_url_csv}))"

    def _write_in_page_step_headings(self, processed_text):
        """
        Writes in the headings for each in-page step. Adds ID for in-page links,
        and class for fancy CSS
        """
        for i, in_page_step in enumerate(self._parser.in_page_steps):
            kramdown_block = "{:"
            kramdown_block += f'id="{in_page_step["id"]}" '
            kramdown_block += 'class="page-step"}'
            step_heading = f"## Step {i+1}: {in_page_step['heading']} {kramdown_block}"
            if in_page_step['nosubheading']:
                subheading = ""
            else:
                subheading = self._pagestep_subheading()
            processed_text = processed_text.replace(in_page_step["fullmatch"],
                                                    step_heading+subheading)

        return processed_text

    def _pagestep_subheading(self):
        return ""

    def _replace_page_lists(self, processed_text):
        """
        Replace page lists with processed markdown
        """

        for (page_list_match, page_list_dict) in self._parser.page_lists():
            if "tag" in page_list_dict:
                page_list = self._doc.get_page_list(page_list_dict['tag'])
            else:
                page_list = self._doc.get_page_list()
            page_list_md = '\n\n'
            for page in page_list:
                link = self._url_translator.simple_translate(page.filepath)
                link_text = page.summary
                page_list_md += f'* [{link_text}]({link})\n'
            page_list_md += '\n'
            processed_text = processed_text.replace(page_list_match, page_list_md)
        return processed_text

    def _replace_step_links(self, processed_text):
        """
        Replace all step links it with processed markdown
        """
        for link in self._parser.step_links:
            #Overriding the input link text if it was just a .
            text_override = None
            if link.linktext == ".":
                page = self._doc.get_page_by_path(link.link_rel_to_root)
                if page is not None:
                    text_override = page.title
            rep_text = link.link_md(self._url_translator, text_override=text_override)
            processed_text = processed_text.replace(link.fullmatch, rep_text)
        return processed_text

    def _replace_plain_links(self, processed_text):
        """
        Replace all non buildup links it with processed markdown
        the only processing here is the url translation rules
        """
        for link in self._parser.plain_links:
            rep_text = link.link_md(self._url_translator)
            processed_text = processed_text.replace(link.fullmatch, rep_text)
        return processed_text

    def _replace_outputs(self, processed_text):
        """
        Replace all outputs with anchor points
        """
        for output in self._parser.outputs:
            rep_text = output.link_md(None)
            processed_text = processed_text.replace(output.fullmatch, rep_text)
        return processed_text

    def _replace_zip_links(self, processed_text):
        """
        Replace all zip links with processed markdown
        """
        for zip_link in self._parser.zip_links:
            rep_text = zip_link.link_md(self._url_translator)
            processed_text = processed_text.replace(zip_link.fullmatch, rep_text)
        return processed_text

    def _replace_images(self, processed_text):
        """
        Replace all images it with processed markdown
        the only processing here is the url translation rules
        """
        for image in self._parser.images:
            previewer =  self._doc.previewer_for_uri(image.image_rel_to_root)
            if previewer is None:
                if not image.is_title_image and image.buildup_data is not None:
                    _LOGGER.warning('Image has unused buildup data',
                                    extra={'fussy':True})
                if image.is_title_image:
                    if self._title_image is None:
                        self._title_image = image
                    else:
                        _LOGGER.warning('Title image is doubly defined on page')

                if image.is_title_image and self.is_pdf_front_page:
                    rep_text = ""
                else:
                    rep_text = image.image_md(self._url_translator)
            else:
                if 'previewers_used' in self._meta_info:
                    if previewer.name not in self._meta_info['previewers_used']:
                        self._meta_info['previewers_used'].append(previewer.name)
                else:
                    self._meta_info['previewers_used'] = [previewer.name]
                location = image.output_url(self._url_translator)
                rep_text = previewer.display_code(location,
                                                  image.alttext,
                                                  image.hovertext,
                                                  image.buildup_data)
            processed_text = processed_text.replace(image.fullmatch, rep_text)
        return processed_text

    def _replace_part_links(self, processed_text):
        """
        Replace all part links with processed (Kramdown) markdown
        """
        for link in self._parser.part_links:
            if self._doc.config.target_format == "pdf":
                if link.overridetext:
                    rep_text = link.overridetext
                else:
                    rep_text = link.linktext
            else:
                if link.overridetext:
                    rep_text = f'[{link.overridetext}][{link.linktext}]'
                else:
                    rep_text = f'[{link.linktext}]'
                part = self._part_list.getpart(link.linktext)
                if part is not None:
                    if part.location_undefined:
                        rep_text += '{: Class="missing"}'
            processed_text = processed_text.replace(link.fullmatch, rep_text)
        return processed_text

    def _replace_link_refs(self, processed_text):
        """
        Replace link references with BuildUp data and replace it with a
        standard markdown link reference.
        """

        for link_ref in self._parser.link_refs:
            translator = self._url_translator
            if link_ref.linktext in self._part_list:
                translator = self._part_url_translator
            processed_text = processed_text.replace(link_ref.fullmatch,
                                                    link_ref.link_ref_md(translator))
        return processed_text

    def _add_missing_link_refs(self, processed_text):
        """
        Adds link reference for any part that doesn't have one
        """
        processed_text += "\n\n"
        for part in self._part_list:
            if isinstance(part, UsedPart):
                refnames = [ref.linktext for ref in self._parser.link_refs]
                if part.name not in refnames:
                    processed_text += "\n"
                    processed_text += part.link_ref_md(self._part_url_translator)
        return processed_text

    def _add_bottom_navigation(self, processed_text, pagelist, overload_path=None):

        page_ordering = utilities.nav_order_from_pagelist(pagelist)

        path = self.filepath if overload_path is None else overload_path
        if path in page_ordering:
            # Note that <!-- GitBuilding Nav --> is searched for by
            # unmark to remove the navigation.
            processed_text += "\n\n<!-- GitBuilding Nav -->\n---\n\n"
            index = page_ordering.index(path)

            if index != 0:
                link = self._url_translator.simple_translate(page_ordering[index-1])
                processed_text += f"[Previous page]({link})"

            if index != len(page_ordering)-1:
                if index != 0:
                    processed_text += " | "
                link = self._url_translator.simple_translate(page_ordering[index+1])
                processed_text += f"[Next page]({link})"
            if index == 0:
                if self._qaqc_start_page is not None:
                    link = self._url_translator.simple_translate(self._qaqc_start_page.url)
                    processed_text += f" | [Start quality-managed build]({link})"
        return processed_text

    @notify_logger
    def generate_output(self,
                        pagelist,
                        overload_path=None,
                        replace_links=None):
        """
        Does the final stages of building the output markdown
        """
        # Note these are reset here rather than in rebuild as rebuild only relates to
        # a complete rebuild for the live editor, there everything including the page list
        # needs to be recalcualted. Generate output may be called twice in other instances
        # such as PDF generation.
        self._meta_info = {}
        self._title_image = None

        # Raise any variable warnings for this version of the page
        for warning in self._parser.preprocess_warnings:
            _LOGGER.warning(*warning)
        self._overloaded_path = overload_path
        self._replace_links = replace_links
        self._resolve_from_step_links(pagelist)

        if self._doc.config.target_format == "md":
            processed_text = self._parser.preprocessed_md_with_details
        else:
            processed_text = self._parser.preprocessed_md_with_details_placeholder

        has_qaqc = utilities.pagelist_contain_qaqc(self._doc, pagelist)
        if has_qaqc:
            self._qaqc_start_page = QaQcStartPage(pagelist, self._doc)

        processed_text = self._replace_title(processed_text)
        processed_text = self._replace_special_blockquotes(processed_text)
        processed_text = self._replace_qaqc_blocks(processed_text, pagelist)
        processed_text = self._write_bom(processed_text,
                                         pagelist,
                                         replace_links)
        processed_text = self._write_in_page_step_headings(processed_text)
        processed_text = self._replace_link_refs(processed_text)
        processed_text = self._replace_page_lists(processed_text)
        processed_text = self._replace_step_links(processed_text)
        processed_text = self._replace_part_links(processed_text)
        processed_text = self._replace_outputs(processed_text)
        processed_text = self._replace_zip_links(processed_text)
        processed_text = self._replace_plain_links(processed_text)
        processed_text = self._add_missing_link_refs(processed_text)
        #replace images last as they may be inside other links
        processed_text = self._replace_images(processed_text)
        if self.part_data is not None:
            processed_text += self.part_data.page_markdown
        if not self._doc.config.remove_bottom_nav:
            processed_text = self._add_bottom_navigation(processed_text, pagelist)

        meta = deepcopy(self._meta_info)
        if self.details is not None:
            meta['details'] = deepcopy(self.details.as_output_dict(self.filepath,
                                                                   self._url_translator))

        self._reset_from_step_links()
        self._overloaded_path = None
        self._replace_links = None
        return processed_text, meta

    @notify_logger
    def get_step_tree(self, breadcrumbs=None, variables=None):
        """
        This function traverses returns the step tree for a page. Any page that is
        finding its current step tree should pass its breadcrumbs
        """
        if breadcrumbs is None:
            breadcrumbs = []
        else:
            breadcrumbs = copy(breadcrumbs)

        if self.filepath in breadcrumbs:
            trail = ''
            for crumb in breadcrumbs:
                trail += crumb + ' -> '
            trail += self.filepath
            _LOGGER.warning("The steps in the documentation form a loop! [%s] "
                            "This can cause very weird behaviour.",
                            trail,
                            extra={'this':'that'})
            return {self.filepath: [], "variables": variables}

        if self._step_tree is None:
            breadcrumbs.append(self.filepath)
            self._parse_step_tree(breadcrumbs)

        out_tree = copy(self._step_tree)
        out_tree['variables'] = variables
        return out_tree

    def _parse_step_tree(self, breadcrumbs=None):
        """
        This function traverses the steps in the page to create a complete downward step tree
        it uses the same function of other steps until all pages downstream have completed.
        Breadcrumbs showing the path down the step tree is passed on to allow checks for loops
        in the step definition. This stops infinite loops occurring.
        """
        if breadcrumbs is None:
            breadcrumbs = [self.filepath]

        list_of_subtrees = []
        for step_link in self._parser.step_links:
            step_variables = step_link.buildup_data.variables
            step_page = self._doc.get_page_by_path(step_link.link_rel_to_root)
            if step_page is None:
                _LOGGER.warning('Missing page "%s"', step_link.link_rel_to_root)
            else:
                page_step_tree = step_page.get_step_tree(breadcrumbs,
                                                         variables=step_variables)
                list_of_subtrees.append(page_step_tree)
        # Note that page object is not hashable so the step tree key is the path.
        self._step_tree = {self.filepath: list_of_subtrees}

    def make_bom_page(self, pagelist, replace_links):
        """
        Makes separate Bill of materials page for the all parts on this page (including those
        in steps). Returns the filepath of the resulting file and the markdown in a dictionary
        """

        md_path = self._bom_url()
        csv_path = self._bom_url(self.AS_CSV)

        if self._doc.config.target_format == "pdf":
            bom_intro = ""
        else:
            bom_intro = f"Download this as a [CSV file]({posixpath.basename(csv_path)})"

        title = "Bill of Materials"
        # Fine to use self._url_translator as the BOM page will be in same
        # output directory
        no_links = self._doc.config.target_format == "pdf"
        md = self._all_parts.bom_md(f"# {title}",
                                    self._part_url_translator,
                                    intro=bom_intro,
                                    no_links=no_links)
        if not self._doc.config.remove_bottom_nav:
            md = self._add_bottom_navigation(md, pagelist, overload_path=md_path)
        csv = self._all_parts.bom_csv(self._doc)

        if replace_links is not None:
            if md_path in replace_links:
                md_path = replace_links[md_path]
            if csv_path in replace_links:
                csv_path = replace_links[csv_path]

        md_file = FileInfo(md_path, title=title, dynamic_content=True, content=md)
        csv_file = FileInfo(csv_path, title=f"{title} (csv)", dynamic_content=True, content=csv)
        return md_file, csv_file


class VariationPage(Page):
    """
    A page object for a variation on a page that is modified by variables.
    """

    def __init__(self, file_obj, doc, parent, page_vars):
        self._parent = parent
        self._page_vars = page_vars
        super().__init__(file_obj, doc)

    @property
    def variables(self):
        """
        Return the variables set for this page
        """
        return self._page_vars

    @notify_logger
    def _set_parser(self, raw_text, live_edit=False):
        self._parser = BuildUpParser(raw_text,
                                     self.filepath,
                                     self._doc,
                                     variables=self._page_vars,
                                     live_edit=live_edit)

    def matches_variables(self, variable_list):
        """Return true if variable list matches page variables for this variation."""
        return variable_list==self._page_vars

    def get_variation(self, variable_list):
        """Get a variation of this page with the correct variable list"""
        return self._parent.get_variation(variable_list)

    @property
    def part_list_multiplier(self):
        if 'make_qty' in self._page_vars:
            return self._page_vars['make_qty']
        return None

    @property
    def _make_qty(self):
        qty = self.part_list_multiplier
        if qty is None:
            return 0
        else:
            return qty.value

    @property
    def _make_output_name(self):
        return self._page_vars.get('make_linktext', 'output')

    def _get_title_subheading(self):
        if self._make_qty>1:
            return (f"\n***In this page you will be making {self._make_qty} "
                    f"{self._make_output_name}***\n")
        return ""

    def _pagestep_subheading(self):
        if self._make_qty>1:
            return (f"\n***For each of the {self._make_qty} {self._make_output_name} "
                    "you will need to:***\n")
        return ""

    @property
    def included_in_another_page(self):
        """
        Return whether this page is included in another page
        """
        return self._parent.included_in_another_page

    def set_as_included(self, path):
        """
        Set that this page has been included in another page. This should stop excess warnings
        """
        self._parent.set_as_included(path)

    def live_reparse(self, md):
        """
        Update parser for this variation of the page during live edit
        """
        self._set_parser(md, live_edit=True)
