"""
This submodule contains the main BuildUp Documentation class.
"""

from copy import copy, deepcopy
import fnmatch
import logging
import posixpath
import json
from dataclasses import is_dataclass
from gitbuilding.buildup.page import Page
from gitbuilding.buildup.partlist import GlobalPartList
from gitbuilding.buildup.libraries import Libraries
from gitbuilding.buildup.files import FileInfo
from gitbuilding.buildup.url import URLRules, translate_external
from gitbuilding.buildup.link import LibraryLink
from gitbuilding.buildup.config import ConfigSchema
from gitbuilding.buildup.pageorder import PageOrder
from gitbuilding.buildup import utilities
from gitbuilding.buildup.unmark import unmark
from gitbuilding.buildup.exsource import GBExSource

_LOGGER = logging.getLogger('BuildUp')

class Documentation:
    """
    This class represents the documentation in a BuildUp project. All other objects
    representing Pages, Libraries, Parts, Partlists, Links, etc are held within this
    the Documentation object. The most simple use of the Documentation object is to
    initialise it with a configuration and then run `buildall` with a list of input
    files.
    """

    def __init__(self, configuration, working_dir, url_rules=None, previewers=None):
        self._filelist = None
        self._working_dir = working_dir
        self._external_files = None
        self._exsource = None
        self._landing_page = None
        self._pages = []
        self._libs = Libraries([])
        self._output_files = []
        self._page_order = None
        self._global_partlist = None
        if is_dataclass(configuration):
            self._input_config = configuration
        elif isinstance(configuration, dict):
            self._input_config = ConfigSchema().load(configuration)
        else:
            raise TypeError("configuration should be a dataclass or dictionary")
        self._config = deepcopy(self._input_config)

        if url_rules is None:
            self._url_rules = URLRules()
        else:
            if not isinstance(url_rules, URLRules):
                raise TypeError('url_rules must a URLRules object')
            self._url_rules = url_rules
        self._url_rules.set_external_dirs(self._config.external_dirs)

        if previewers is None:
            self._previewers = []
        else:
            self._previewers = previewers

    @property
    def working_dir(self):
        """
        Read only property that returns the working dir as a absolute path in the
        operating systems's format
        """
        return self._working_dir

    @property
    def filelist(self):
        """
        Read only property that returns the input files
        """
        return self._filelist

    @property
    def config(self):
        """
        Read only property that returns the config object
        """
        return self._config

    @property
    def landing_page(self):
        """
        Somewhat confusing read only property. This option is the
        Page object of the landing page. `config.landing_page` is
        the path to the landing page. This may be changed in future
        versions!
        """
        return self._landing_page

    @property
    def pages(self):
        """
        Read only property that returns the list of pages (list of
        Page objects) in the documentation. The list is returned so any
        modifications to the returned list will affect the Documentation.
        """
        return self._pages

    @property
    def page_order(self):
        """
        Returns the PageOrder object describing the paths through the documentation
        """
        return self._page_order

    @property
    def global_partlist(self):
        """
        Returns the global partlist. This partlist has all parts used in any path through the
        documentation. The quantities listed are meaninless.
        """
        return self._global_partlist

    @property
    def libs(self):
        """
        Read only property that returns the list of libraries (list of
        Library objects) in the documentation. The list is returned so any
        modifications to the returned list will affect the Documentation.
        """
        return self._libs

    @property
    def output_files(self):
        '''
        List of all output files as FileInfo objects
        '''
        return self._output_files

    @property
    def previewers(self):
        """
        Return a lists of the previewers for this documentation object.
        (For example the STL previewer or the PDF previewer)
        """
        return self._previewers

    @property
    def url_rules(self):
        '''
        Returns the URLRules object to set how output urls are formatted
        '''

        return self._url_rules

    def get_file(self, path):
        '''If a file with at this path in the output exists a
        FileInfo object is returned

        If the file is not in the output None is returned'''
        if path in self._output_files:
            return self.output_files[self.output_files.index(path)]
        return None

    def previewer_for_uri(self, uri):
        """
        Returns the previewer for this file or link. Returns None if cannot
        preview
        """
        for previewer in self.previewers:
            if previewer.can_preview(uri):
                return previewer
        return None

    def get_page_by_path(self, filepath, variables=None):
        """
        Returns the page object matching the file path, or None if missing
        """
        if filepath in self._pages:
            page = self._pages[self._pages.index(filepath)]
            if variables:
                page = page.get_variation(variables)
            return page
        return None

    def get_page_objects(self, path_list, warn=False):
        """
        Returns a list of valid page objects for an input list of paths. Any missing
        paths are silently ignored. Therefore an invalid input list results in an
        empty output list. Set `warn=True` to log a warning for each missing page
        """
        obj_list = []
        for path in path_list:
            if path in self._pages:
                obj_list.append(self.get_page_by_path(path))
            elif warn:
                _LOGGER.warning('Missing page "%s"', path)
        return obj_list

    def get_page_list(self, tag=None):
        """
        Return a list of all the pages. Optionally only the pages matching a given tag
        """
        if tag is None:
            return copy(self._pages)
        return [page for page in self._pages if tag in page.tags]

    def _create_all_pages(self, filelist):
        """
        Creates a Page object for each markdown page in the input filelist.
        """

        self._pages = []
        for file_obj in filelist:
            if file_obj.dynamic_content and file_obj.path.endswith('.md'):
                self._pages.append(Page(file_obj, self))
        n=0
        while sum([1 for page in self._pages if page.reprocess_needed])>0:
            n+=1
            if n > len(self._pages):
                rec_pages = [page.filepath for page in self._pages if page.reprocess_needed]
                _LOGGER.warning('Recursive include between %s', ', '.join(rec_pages))
                break
            for page in self._pages:
                if page.reprocess_needed:
                    page.reprocess_md()

    def _check_landing_page(self):
        """
        Checks if the landing page exists. Also looks for index.md as this
        is the standard landing page once we change to html
        """

        if "index.md" in self._pages:
            if self._config.landing_page is None:
                self._config.landing_page = "index.md"
            elif self._config.landing_page != "index.md":
                _LOGGER.warning("Landing page is set to %s but also `index.md` exists. "
                                "This may cause unreliable behaviour",
                                self._config.landing_page)

        if self._config.landing_page in self._pages:
            self._landing_page = self._pages[self._pages.index(self._config.landing_page)]

    def _make_navigation(self):
        """
        If the navigation is not set in the configuration a Navigation
        is automatically created
        """
        if self._config.navigation != []:
            self._check_and_complete_subnav()

        elif self.page_order.number_of_paths == 0:
            url_translator = self.url_rules.create_translator('index.md')
            pages = [page for page in self._pages if page != self._landing_page]
            for page in pages:
                link = url_translator.simple_translate(page.filepath)
                self._config.navigation.append({'title': page.summary, 'link': link})
        else:
            for n in range(self.page_order.number_of_paths):
                pagelist = self.page_order.pagelists[n]
                replace_links = self.page_order.link_replacement_dictionaries[n]
                url_translator = self.url_rules.create_translator('index.md',
                                                                  replace_links=replace_links)
                nav = self._make_navigation_from_page_order(pagelist, url_translator)
                self._config.navigation += nav

    def _check_and_complete_subnav(self):
        #A standard translatior to translate urls into output format
        url_translator = self.url_rules.create_translator('index.md')
        for [n, nav_item] in enumerate(self._config.navigation):
            link = nav_item["link"]
            if link in self._page_order.duplicates:
                _LOGGER.warning("Creating navigation link for duplicated page.")
                continue
            if self._config.autocompletesubnav:
                has_subnav = "subnavigation" in nav_item
                on_pagelist = link in self.page_order.masterlist
                if (not has_subnav) and on_pagelist:
                    this_sub_nav, replace_links = self.page_order.get_pagelist_for_page(link)
                    # A translatior that replaces pages to the correct version for the active path
                    # of the documentation
                    this_translator = self.url_rules.create_translator('index.md',
                                                                       replace_links=replace_links)
                    nav = self._make_navigation_from_page_order(this_sub_nav, this_translator)
                    nav[0]["title"] = nav_item["title"]
                    self._config.navigation[n] = nav[0]
                    continue
            self._translate_nav_item(nav_item, url_translator)


    def _translate_nav_item(self, nav_item, url_translator):
        nav_item["link"] = url_translator.simple_translate(nav_item["link"])
        if "subnavigation" in nav_item:
            for sub_nav_item in nav_item["subnavigation"]:
                self._translate_nav_item(sub_nav_item, url_translator)

    def _make_navigation_from_page_order(self, pagelist, url_translator):

        def append_nav_item(nav, nav_item, nav_depth):
            if nav_depth == 0:
                nav.append(nav_item)
            elif nav_depth == 1:
                parent_item = nav[-1]
                if "subnavigation" not in parent_item:
                    parent_item["subnavigation"] = []
                parent_item["subnavigation"].append(nav_item)

        nav = []

        #Remove the landing_page if it is the start of the pagelist.
        if self._landing_page == pagelist[0]:
            index_page = pagelist.pop(0)
            if index_page.md_bom_page is not None:
                bom_link = url_translator.simple_translate(index_page.md_bom_page)
                bom_nav_item = {'title': "Bill of Materials", 'link': bom_link}
                append_nav_item(nav, bom_nav_item, 0)
        for page_entry in pagelist:
            page = self.get_page_by_path(page_entry.path)
            link = url_translator.simple_translate(page.filepath)
            nav_item = {'title': page.summary, 'link': link}
            nav_depth = page_entry.depth-pagelist[0].depth
            append_nav_item(nav, nav_item, nav_depth)
            if page_entry.md_bom_page is not None:
                bom_link = url_translator.simple_translate(page_entry.md_bom_page)
                bom_nav_item = {'title': "Bill of Materials", 'link': bom_link}
                append_nav_item(nav, bom_nav_item, nav_depth+1)
        return nav

    def _generate_output_files(self):
        """
        Returns a list of all files that need to be output
        for plain markdown output.
        """
        all_output_files = []

        for page in self._pages:
            #Skip any pages on a step tree, they will be generated later.
            if page in self._page_order.masterlist:
                continue
            #Skip any pages included in another page
            if page.included_in_another_page:
                continue
            self._append_outputs_for_page(all_output_files, page, [])

        for n in range(self._page_order.number_of_paths):
            replace_links = self._page_order.link_replacement_dictionaries[n]
            pagelist = self._page_order.pagelists[n]
            for page_entry in pagelist:
                basedepth = 1 if self._landing_page == pagelist[0].path else 0
                crumbs = page_entry.get_breadcrumbs()
                crumbs = crumbs[basedepth:]
                page_name = page_entry.path
                if page_name in replace_links:
                    out_path = replace_links[page_name]
                else:
                    out_path = page_name
                duplicate_of = None if page_name == out_path else page_name
                page = self.get_page_by_path(page_name, variables=page_entry.variables)
                if page.included_in_another_page:
                    _LOGGER.warning('The page %s is included in another page and will not be '
                                    'output, it should not be used as a step in another page!',
                                    page_name)
                    continue

                self._append_outputs_for_page(all_output_files,
                                              page,
                                              pagelist,
                                              overloaded_path=out_path,
                                              replace_links=replace_links,
                                              duplicate_of=duplicate_of,
                                              breadcrumbs=crumbs)
        self._append_page_for_duplicates(all_output_files)

        return all_output_files

    def _append_page_for_duplicates(self, all_output_files):
        for duplicated_page in self._page_order.duplicates:
            page = self.get_page_by_path(duplicated_page)
            links = []
            # Duplicates is a dictionary.
            # Each page that is duplicated is a key who's value is the list of the root of
            # each documentation path that contains the page
            for duplicate_entry in self._page_order.duplicates[duplicated_page]:
                rootpath = duplicate_entry.root
                #For each copy find the output path, and the title of the root page.
                root_page = self.get_page_by_path(rootpath)
                list_no = self._page_order.get_list_number(rootpath)
                replace_links = self._page_order.link_replacement_dictionaries[list_no]
                url_translator = self.url_rules.create_translator(duplicate_entry.path,
                                                                  replace_links=replace_links)
                translated_target = url_translator.simple_translate(duplicate_entry.path)
                links.append((root_page.title, translated_target))
            content = ("# There are multiple versions of this page.\n\nPlease select one "
                       "of these projects:\n\n")
            for link in links:
                content += f"* [{link[0]}]({link[1]})\n"
            content += "\n"
            file_obj = FileInfo(page.filepath,
                                dynamic_content=True,
                                content=content,
                                duplicate_disambiguation=True)
            all_output_files.append(file_obj)

    def _append_outputs_for_page(self,
                                 all_output_files,
                                 page,
                                 pagelist,
                                 overloaded_path=None,
                                 replace_links=None,
                                 duplicate_of=None,
                                 breadcrumbs=None,
                                 pdf=False):

        page_content, meta = page.generate_output(pagelist,
                                                  overload_path=overloaded_path,
                                                  replace_links=replace_links)
        outpath = overloaded_path if overloaded_path is not None else page.filepath
        file_obj = FileInfo(outpath,
                            title=page.title,
                            dynamic_content=True,
                            content=page_content,
                            meta_info=meta,
                            duplicate_of=duplicate_of,
                            includes=page.includes,
                            variables=page.variables,
                            breadcrumbs=breadcrumbs)
        all_output_files.append(file_obj)
        if page.get_bom_page(as_filelist=True) is not None:
            bom_pages = page.get_bom_page(as_filelist=True)
            bom_crumb = [outpath] if breadcrumbs is None else breadcrumbs
            for bom_page in bom_pages:
                bom_page.breadcrumbs = bom_crumb + [bom_page.path]
            all_output_files += bom_pages
        if pagelist and page == pagelist[0]:
            qaqc_start_page_and_json = page.get_qaqc_start_page_and_json()
            if qaqc_start_page_and_json is not None:
                all_output_files += qaqc_start_page_and_json
        for link in page.all_links_and_images:
            linked_file = None
            if link.content_generated:
                if isinstance(link, LibraryLink):
                    if pdf:
                        #Note library contents are not output in pdf
                        continue
                    linked_file = self._libs.part_page(*link.library_location)
                elif link.is_zip:
                    link_urls = [link.link_rel_to_root_no_preview for link in page.all_links]
                    link_urls = [link_url for link_url in link_urls if link_url is not None]
                    matching = fnmatch.filter(link_urls, link.zip_pattern)
                    #deduplicate files to zip
                    matching = list(set(matching))
                    linked_file = link.as_output_file(self.config.external_dirs,
                                                      files_to_zip=matching)
                else:
                    link_path = utilities.strip_internal_links(link.link_rel_to_root)
                    if link_path not in self._filelist + self._page_order.filenames_of_duplicates:
                        _LOGGER.warning("Linked markdown page does not exist: %s", link_path)
                    else:
                        linkpage = self.get_page_by_path(link_path)
                        if linkpage is not None and linkpage.included_in_another_page:
                            _LOGGER.warning("%s is embedded in another page, it is not in the "
                                            "final output to be linked to",
                                            link_path)
            else:
                linked_file = link.as_output_file(self.config.external_dirs)
            if linked_file is not None:
                if linked_file not in all_output_files:
                    if not(linked_file.dynamic_content or linked_file in self._filelist+self._external_files):
                        if linked_file.location_on_disk.startswith('..') and linked_file.path.startswith('orphaned_files'):
                            pass
                        elif linked_file.path in self._filelist:
                            _LOGGER.warning("Unknown issue with linked file %s, is this a "
                                            "malformed library link?",
                                            linked_file.path)
                        else:
                            _LOGGER.warning("Linked file does not exist: %s", linked_file.path)
                    # append even if missing to avoid duplicate warnings
                    all_output_files.append(linked_file)
                else:
                    if link.is_zip:
                        current_zip = all_output_files[all_output_files.index(linked_file)]
                        if not linked_file.files_to_zip == current_zip.files_to_zip:
                            _LOGGER.warning('Two zips of the same name are generated with '
                                            'different contents')

    def _append_preview_pages(self, all_output_files):
        for output_file in all_output_files:
            output_path = output_file.path
            if self.previewer_for_uri(output_path) is not None:
                previewer = self.previewer_for_uri(output_path)
                title = posixpath.splitext(posixpath.basename(output_path))[0]
                if previewer.create_preview_page:
                    prev_path = previewer.preview_page_uri(output_path)
                    exsource_entry = self._exsource.export_for(output_file)
                    md = previewer.preview_page_content(output_path,
                                                        exsource_entry=exsource_entry)
                    file_obj = FileInfo(prev_path,
                                        title=title,
                                        dynamic_content=True,
                                        content=md,
                                        meta_info={'previewers_used': previewer.name})
                    all_output_files.append(file_obj)
                    self._append_exsource_links(exsource_entry, all_output_files)

    def _append_exsource_links(self, exsource_entry, all_output_files):
        if exsource_entry:
            linked_files = (exsource_entry.output_files +
                            exsource_entry.source_files +
                            exsource_entry.dependencies)
            for linked_file in linked_files:
                disk_path = linked_file.filepath
                doc_path = translate_external(disk_path, self._config.external_dirs)
                file_obj = FileInfo(doc_path, location_on_disk=disk_path)
                if file_obj not in all_output_files:
                    all_output_files.append(file_obj)

    def _update_config_title(self):
        if self._config.title is None:
            if self._config.landing_page is None:
                self._config.title = "Untitled project"
            else:
                self._config.title = self._landing_page.title

    def _set_page_order(self):
        # build step_tree for all pages
        trees = []
        for page in self._pages:
            trees.append(page.get_step_tree())

        self._page_order = PageOrder(trees, self)

    def buildall(self, filelist, external_files):
        """
        Builds the output documentation as a list of FileInfo objects based on the input
        documentation directory defined by `filelist` (also a list of FileInfo objects)
        """
        # By deepcopying the input config this refreshes the config state
        # if this is not the first time the documentation has run the config will
        # contain information generated from the buildup files, such as navigation or
        # project title

        self._filelist = filelist
        self._external_files = external_files
        self._config = deepcopy(self._input_config)
        self._exsource = GBExSource(self._config, self._filelist+self._external_files)
        self._libs = Libraries(filelist)
        self._create_all_pages(filelist)
        self._check_landing_page()
        self._update_config_title()

        # NOTE: If changing the key page functions below be sure to also change
        # the Page.rebuild

        self._set_page_order()

        # count parts on pages and sub pages
        self._global_partlist = GlobalPartList(self._config)
        for page in self._pages:
            page.count()
            self._global_partlist.merge(page.part_list)

        self._make_navigation()
        self._output_files = self._generate_output_files()
        self._append_preview_pages(self._output_files)
        self._append_forced_outputs(self._output_files)

        if self._config.include_search:
            self._build_search_index()

        return self._output_files

    def _append_forced_outputs(self, outputs):
        for filename in self._config.force_output:
            if utilities.contains_wildcards(filename):
                matches = utilities.match_files(filename, self._filelist)
                outputs += matches
            elif filename not in outputs:
                try:
                    #append this file to the output list
                    matched_file = self._filelist[self._filelist.index(filename)]
                    outputs.append(copy(matched_file))
                except ValueError:
                    _LOGGER.warning('"%s" is on the forced output list but the file'
                                    'cannot be found', filename)

    def output_for_pdf_by_pathlist(self, list_number):
        """
        Returns a list of all files that need to be output if only the documentation
        for a specific pagelist is being generated. This function runs based on the
        outputs created the last time build_all was run.
        """

        pagelist = self._page_order.pagelists[list_number]
        output_files = []
        for page_entry in pagelist:
            page = self.get_page_by_path(page_entry.path, variables=page_entry.variables)
            self._append_outputs_for_page(output_files, page, pagelist, pdf=True)

        for extra_page in self._config.extra_pages_for_pdf:
            page = self.get_page_by_path(extra_page)
            if page is None:
                _LOGGER.warning('Extra page "%s" for pdf is missing', extra_page)
            else:
                self._append_outputs_for_page(output_files, page, pagelist, pdf=True)


        return output_files

    def _build_search_index(self):
        '''
        Builds a search_index.json from output file list and registers it to be
        output.
        '''
        search_index = []
        for outfile in self._output_files:
            if outfile.dynamic_content:
                path, ext = posixpath.splitext(outfile.path)
                if outfile.path == self._landing_page:
                    path = "index"
                is_md = ext.lower() == ".md"
                is_license = path.lower() == "license"
                if  is_md and not is_license and not outfile.duplicate_disambiguation:
                    search_index.append({"path": path,
                                         "title": outfile.title,
                                         "content": unmark(outfile.content),
                                         "breadcrumbs": outfile.breadcrumbs})

        self._output_files.append(FileInfo(path="search_index.json",
                                  dynamic_content=True,
                                  content=json.dumps(search_index)))
