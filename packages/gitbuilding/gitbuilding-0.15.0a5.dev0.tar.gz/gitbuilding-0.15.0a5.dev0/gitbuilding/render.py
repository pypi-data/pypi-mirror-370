"""
This contains GBRenderer, the class responsible for rendering processed markdown into HTML
It also contains the URLRules GitBuilding uses for HTML and some other helper functions.
"""


import posixpath
import datetime
from copy import copy, deepcopy
import logging
#from defusedxml import ElementTree
import regex as re
from markdown import markdown
from jinja2 import Environment, FileSystemLoader
# Must use pylint disable incorrect pylint error see:
# https://github.com/pylint-dev/pylint/issues/491
from pygments.formatters import HtmlFormatter #pylint: disable=no-name-in-module
from gitbuilding.buildup import URLRules
from gitbuilding import utilities
from gitbuilding.buildup.buildup import IMAGE_REGEX
from gitbuilding.buildup.markdown_extensions import base_extensions
from gitbuilding.native_file_operations import (GBPATH,
                                                exists_on_disk,
                                                get_matches_from_dir,
                                                read_local_file)

_LOGGER = logging.getLogger('BuildUp.GitBuilding')


class CodeBlockFormatter(HtmlFormatter):
    """
    A special formatter so we can handle certain code blocks ourselves
    """
    def __init__(self, lang_str='', **options):
        super().__init__(**options)
        # lang_str has the value {lang_prefix}{lang}
        # specified by the CodeHilite's options
        self.lang_str = lang_str

    def format_unencoded(self, source, outfile):
        """
        Catch the unencoded source and check the language.
        """

        if self.lang_str != "language-license":
            super().format_unencoded(source, outfile)
            return
        fullsource = "".join([token[1] for token in source])
        outfile.write('<pre>'+fullsource+'</pre>')

def _md_to_html_no_par(md):
    """
    convert markdown to html but remove all paragraph tags
    """
    html = markdown(md, extensions=["markdown.extensions.attr_list"])
    html = html.replace(r'<p>', '')
    html = html.replace(r'</p>', '')
    return html

class URLRulesHTML(URLRules):
    """
    The BuildUp URLRules used in GitBuilding for both the server and the static HTML.
    This is a child-class of buildup.URLRules with functions to strip off '.md' file
    extensions, rerouted stl links (for parts only) to markdown pages, and to replace
    empty links with "missing".
    """
    def __init__(self, rel_to_root=False, no_server=False):

        super().__init__(rel_to_root=rel_to_root)
        self._target_format = "html"
        def fix_missing(url, anchor, page):
            if url == "" and  anchor == "":
                url = posixpath.relpath("missing", posixpath.dirname(page))
                return url, anchor
            return url, anchor

        def stl_to_page(url, anchor, _):
            if url.endswith('.stl'):
                return url[:-4]+'.html', anchor
            return url, anchor

        def md_to_page(url, anchor, _):
            if url.endswith('.md'):
                return url[:-3]+'.html', anchor
            return url, anchor

        self.add_modifier(fix_missing)
        self.add_modifier(md_to_page)
        if not no_server:
            self.add_part_modifier(stl_to_page)

class URLRulesPDF(URLRules):
    """
    The BuildUp URLRules used in GitBuilding PDF generation (via single pageHTML).
    This is a child-class of buildup.URLRules with functions to strip off '.md' file
    """
    def __init__(self, rel_to_root=True):

        super().__init__(rel_to_root=rel_to_root)
        self._target_format = "pdf"

        def md_to_inside_page(url, anchor, _):
            if url.endswith('.md'):
                url = url[:-3]
                url = url.replace('/', '__')
                if anchor != '':
                    anchor = url + '---' + anchor
                else:
                    anchor = url
                url = ''
            return url, anchor

        self.add_modifier(md_to_inside_page)


def _is_active_nav_item(nav_item, link):
    """
    Checks if the item in the navigation dictionary or any of the
     terms in the sub-navigation are the active page
    """
    if nav_item["link"] == link:
        return True
    if "subnavigation" in nav_item:
        for sub_nav_item in nav_item["subnavigation"]:
            if _is_active_nav_item(sub_nav_item, link):
                return True
    return False

def format_warnings(warnings, show_page=False):
    """
    Returns warnings for the live renderer to display
    """
    output = ""
    for warning in warnings:
        if warning["fussy"]:
            cssclass = "fussywarning"
            warntype = "FussyWarning"
        else:
            cssclass = "warning"
            warntype = "Warning"

        if show_page:
            if isinstance(warning["active_page"], str) and warning["active_page"].endswith('.md'):
                page = warning["active_page"][:-2] + "html"
                active_txt = f'<a href="/{page}">{page}</a> -- '
            else:
                active_txt = ""
        else:
            active_txt = ""

        output += f'<p class="{cssclass}">{active_txt}{warntype}: {warning["message"]}</p>\n'
    return output



class GBRenderer:
    """
    This class is the renderer for GitBuilding HTML
    """
    FULLPAGE = 0
    IFRAME = 1
    PDFPAGE = 2

    def __init__(self, working_dir, config, url_rules, root="/", static=True, no_server=False):
        """
        `static` sets whether it is generating a static site or a page for the live editor
        `no_server` is only used for static sites, sets whether the site is designed to work
                without a server running
        """
        self._working_dir = working_dir
        self.config = config
        self._static = static
        self._no_server = no_server
        self._root = root
        self.custom_stylesheets = []
        self.custom_favicons = {'ico': [], 'png': []}
        self._warning_count = [0,0]

        # Variables that can be accessed by jinja templates
        self.populate_vars()
        self.scan_assets()
        self._url_rules = url_rules

        custom_path = "./_templates"
        template_path = GBPATH + "/templates"
        static_path = GBPATH + "/static"
        loader = FileSystemLoader([custom_path, template_path, static_path])
        self.env = Environment(loader=loader, trim_blocks=True)

    def set_warning_count(self, warnings):
        """
        Set the global warning count to be displayed on all pages
        """
        warning_count = [0,0]
        for warning in warnings:
            if warning["fussy"]:
                warning_count[1] += 1
            else:
                warning_count[0] += 1
        self._warning_count = warning_count

    def populate_vars(self):
        """
        This function populates a partial list of variables that can be used in
        templates. Some variables (with urls) are dynamically calculated later.
        To include dynamically calculated variables, make sure to use the
        _get_variables function.
        """

        self._variables = {"title": self.config.title,
                           "year": datetime.datetime.now().year,
                           "root": self._root}

        self._variables["authors"] = utilities.author_list(self.config)
        self._variables["email"] = self.config.email
        self._variables["affiliation"] = self.config.affiliation
        self._variables["primary_color"] = self.config.primary_color
        self._variables["secondary_color"] = self.config.secondary_color
        self._variables["hover_color"] = self.config.hover_color
        self._variables["remove_images_border"] = self.config.remove_images_border
        self._variables["remove_images_background"] = self.config.remove_images_background
        #Note licence is calculated dynamically

        for key in self.config.variables.keys():
            self._variables[key] = self.config.variables[key]

    def _get_variables(self, link=None):
        """
        link is used to change the url roots to relatative. Set link=None to use WebsiteRoot from
        the configuration file.
        """
        variables = copy(self._variables)
        if link is not None:
            relative_root = posixpath.relpath('.', posixpath.dirname(link)) + "/"
            variables['root'] = relative_root
        else:
            variables['root'] = "./"
        if self._no_server:
            url_translator = self._url_rules.create_translator(link)
            variables['landing'] = url_translator.simple_translate('index.md')
        else:
            variables['landing'] = variables['root']

        variables['license'] = self._get_license(link)
        variables['include_search'] = self.config.include_search and not self._no_server
        return variables

    def _get_license(self, link):
        '''Returns the licence name or licence link. The variable link is the
        url of the page this text will go on. This allows relative links to be calculated
        '''
        if self.config.license is None:
            return None

        #Not linking to license in pdf
        if self.config.license_file is None or self.config.target_format == "pdf":
            return self.config.license

        url_translator = self._url_rules.create_translator(link)
        licence_url = url_translator.simple_translate(self.config.license_file)
        return f'<a href="{licence_url}">{self.config.license}</a>'

    def scan_assets(self):
        """
        This scans the assets folder of the project to look for custom CSS and favicons
        """
        if exists_on_disk("assets", self._working_dir):
            css_files = get_matches_from_dir("assets",
                                             self._working_dir,
                                             r"^.+\.css$",
                                             relative=True)
            self.custom_stylesheets += css_files
            ico_favicons = get_matches_from_dir("assets",
                                                self._working_dir,
                                                r"^favicon\.ico$",
                                                relative=True)
            self.custom_favicons['ico'] += ico_favicons
            png_regex = r"favicon-([0-9]+)x[0-9]+\.png$"
            png_favicons = get_matches_from_dir("assets",
                                                self._working_dir,
                                                r"^"+png_regex,
                                                relative=True)
            for png_favicon in png_favicons:
                pixels = re.match(r".*"+png_regex, png_favicon).group(1)
                self.custom_favicons['png'].append((png_favicon, pixels))

    def nav_links(self, link=None):
        """
        This function returns the side navigation
        """

        navigation = deepcopy(self.config.navigation)
        for nav_item in navigation:
            if _is_active_nav_item(nav_item, link):
                nav_item['class'] = 'active'
                if "subnavigation" in nav_item:
                    for sub_nav_item in nav_item["subnavigation"]:
                        if _is_active_nav_item(sub_nav_item, link):
                            sub_nav_item['class'] = 'active'
                        else:
                            sub_nav_item['class'] = 'not-active'
            else:
                nav_item['class'] = 'not-active'
                if "subnavigation" in nav_item:
                    del nav_item["subnavigation"]

        tmpl = self.env.get_template("nav.html.jinja")
        html = tmpl.render(navigation=navigation, **self._get_variables(link))
        return html

    def project_header(self, subtitle=None, link=None):
        """
        This is the project header that can be customised.
        """
        tmpl = self.env.get_template("header.html.jinja")
        html = tmpl.render(subtitle=subtitle, **self._get_variables(link))
        return html

    def project_footer(self, link=None):
        """
        This returns either the standard project footer or the customised footer
        """
        tmpl = self.env.get_template("footer.html.jinja")
        html = tmpl.render(**self._get_variables(link))
        return html

    def details_header(self, details):
        """
        Render the details header if exists
        """
        if details is None:
            return ""

        thumbnail = None
        difficulty = None
        time = None
        skills = None
        extra_details = None
        for key in details:
            if key=='thumbnail':
                thumbnail = _md_to_html_no_par(details[key])
            elif key=='difficulty':
                difficulty = _md_to_html_no_par(details[key])
            elif key=='time':
                time = _md_to_html_no_par(details[key])
            elif key=='skills':
                skills = []
                for skill in details[key]:
                    skills.append(_md_to_html_no_par(skill))
            else:
                if extra_details is None:
                    extra_details = []
                extra_details.append([key, _md_to_html_no_par(details[key])])

        tmpl = self.env.get_template("details_header.html.jinja")
        html = tmpl.render(thumbnail=thumbnail,
                           difficulty=difficulty,
                           time=time,
                           skills=skills,
                           extra_details=extra_details)
        return html

    def favicon_html(self, link):
        """
        This returns the HTML for the favicon. Generates multiple PNG as well
        as ico favicon references based on the custom favicons found.
        """
        tmpl = self.env.get_template("favicon.html.jinja")
        num_custom_favicons = (len(self.custom_favicons['ico'])
                               + len(self.custom_favicons['png']))
        if num_custom_favicons == 0:
            ico_favicons = ["static/Logo/favicon.ico"]
            png_favicons = [("static/Logo/favicon-32x32.png", 32),
                            ("static/Logo/favicon-16x16.png", 16)]
        else:
            ico_favicons = self.custom_favicons['ico']
            png_favicons = self.custom_favicons['png']
        output = tmpl.render(ico_favicons=ico_favicons,
                             png_favicons=png_favicons,
                             **self._get_variables(link))
        return output

    def _replace_galleries(self, md):
        """
        Find galleries in the markdown a line with only images (must be more than
        one image) replace with gallery HTML
        """

        tmpl = self.env.get_template("gallery.html.jinja")
        imlines = re.findall(r'^((?:[ \t]*'+IMAGE_REGEX+'[ \t]*(?:\n|\r\n)?){2,})$',
                             md,
                             re.MULTILINE)
        # imlines uses the IMAGE_REGEX which matches lots of groups. First is the whole line.
        imlines = [line[0] for line in imlines]

        for gallery_number, imline in enumerate(imlines):
            images = re.findall(IMAGE_REGEX, imline)
            gallery_html = tmpl.render(gallery_number=gallery_number,
                                       images=images)
            md = md.replace(imline, gallery_html)
        return md

    def render_md(self, md, link, **kwargs):
        """
        This function returns the rendered HTML for input markdown
        """
        template = kwargs.get('template', self.FULLPAGE)
        if template != self.PDFPAGE:
            md = self._replace_galleries(md)

        pdf = self.config.target_format == "pdf"

        extensions = base_extensions(pdf) + ("gitbuilding.markdown_latex:LatexExtension", "codehilite")

        extension_configs={'codehilite': {'pygments_formatter': CodeBlockFormatter}}


        content_html = markdown(md,
                                tab_length=self.config.tab_length,
                                extensions=extensions,
                                extension_configs=extension_configs)

        return self.render(content_html, link=link, **kwargs)

    def render(self, html, link, **kwargs):
        """
        This function creates the full HTML page from the input HTML generated from BuildUp
        """
        template = kwargs.get('template', self.FULLPAGE)
        nav = kwargs.get('nav', True)
        editorbutton = kwargs.get('editorbutton', False)
        meta_info = kwargs.get('meta_info', {})
        variables = self._get_variables(link)

        details = meta_info.get('details', None)
        if details is not None:
            details_html = self.details_header(details)
            html = html.replace("{{BUILDUPDETAILS}}", details_html)

        if link is None:
            editor_link = "-/editor"
        else:
            editor_link = f"{variables['root']}{link}/-/editor"

        input_dictionary = {'favicon_html': self.favicon_html(link),
                            'content': html,
                            'nav': nav,
                            'nav_links': self.nav_links(link),
                            'project_header': self.project_header(link=link),
                            'project_footer': self.project_footer(link),
                            'static': self._static,
                            'warning_count': self._warning_count,
                            'editorbutton': editorbutton,
                            'editor_link': editor_link,
                            'previewers_used': meta_info.get('previewers_used', []),
                            'target_format': self.config.target_format}

        if template == self.FULLPAGE:
            tmpl = self.env.get_template("full_page.html.jinja")
            input_dictionary['custom_stylesheets'] = self.custom_stylesheets
        elif template == self.IFRAME:
            tmpl = self.env.get_template("iframe.html.jinja")
            custom_style = []
            for sheet in self.custom_stylesheets:
                custom_style.append(read_local_file(sheet, self._working_dir))
            input_dictionary['custom_style'] = custom_style
        elif template == self.PDFPAGE:
            page_id = link.replace('/', '__')
            tmpl = self.env.get_template("pdfpage.html.jinja")
            input_dictionary['page_id'] = page_id
        else:
            raise ValueError(f'Unknown pdf template type: {template}')
        output = tmpl.render(**input_dictionary, **variables)

        return output

    def missing_page(self):
        """
        This returns an HTML page for missing parts.
        """

        missing_html = ("<h1>Missing Part</h1>\n\n"
                        "<p>This documentation has specified a part,"
                        " but not provided a link or further data.</p>")
        return self.render(missing_html, link="missing")

    def empty_homepage(self):
        """
        This returns an HTML page for the homepage if missing. This is only
        shown on the live server.
        """
        html = (r'<h1>No homepage set</h1>'
                r'<h2><a href="-/create-homepage/">Create homepage</a></h2>')
        return self.render(html, editorbutton=False, link=None)

    def warning_page(self, log):
        """
        Return page with warnings for the entire documentation.
        """
        log_html = format_warnings(log, show_page=True)
        style_html = ("<style>\n"
                      "p.fussywarning {background: #fbe09e;}\n"
                      "p.fussywarning a{color: black; font-weight: bold;}\n"
                      "p.warning {background: #fb9e9e;}\n"
                      "p.warning a{color: black; font-weight: bold;}\n"
                      "</style>\n\n")
        return self.render(style_html+"<h1>Documentation warnings</h1>\n\n"+log_html,
                           link="-/warnings")

    def full_pdf(self, html_content, subtitle, title_image=None):
        """
        This method takes all pages as a combined block of html. It then uses the
        full_pdf template to generate an HTML file that WeasyPrint can use to create
        a PDF file.
        """
        pdf_title = self._variables['title']
        if pdf_title is not None and subtitle is not None:
            pdf_title += f' -- {subtitle}'
        tmpl = self.env.get_template("full_pdf.html.jinja")
        if title_image is not None:
            title_image = title_image.image_rel_to_root
        html = tmpl.render(content=html_content,
                           project_header=self.project_header(subtitle=subtitle),
                           project_footer=self.project_footer(),
                           pdf_title=pdf_title,
                           title_image=title_image,
                           **self._get_variables())
        return html
