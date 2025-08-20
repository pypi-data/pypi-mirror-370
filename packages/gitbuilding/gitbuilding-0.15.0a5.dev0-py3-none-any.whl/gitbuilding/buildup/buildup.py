"""
The main submodule for parsing BuildUp. This constains both the BuildUpParser class
and classes Links and Images. It also contains the function that parses the inline
part data.
"""
from copy import copy, deepcopy
import logging
import posixpath
import regex as re
from yaml.scanner import ScannerError
from yaml.parser import ParserError
import frontmatter
from frontmatter.default_handlers import YAMLHandler
from marshmallow import ValidationError
from gitbuilding.buildup.link import create_link_object, BaseLink, Image
from gitbuilding.buildup.utilities import clean_id, raise_validation_error_as_warning
from gitbuilding.buildup.basepart import PartDataSchema
from gitbuilding.buildup.url import URLRules, get_root_url
from gitbuilding.buildup.quantity import Quantity

_LOGGER = logging.getLogger('BuildUp')

BUILDUP_DATA_REGEX = r"""{([^:\n\r](?:[^}\'\"\n\r]|\"[^\"\r\n]*\"|\'[^\'\r\n]*\')*)}"""
IMAGE_REGEX = (r'('
               r'!\[([^\]]*)\]\(\s*([^\)\n\r\t\"]+?)\s*(?:\"([^\"\n\r]*)\")?\s*\)'
               r'(?:' + BUILDUP_DATA_REGEX + ')?'
               r')')
LINK_REGEX = (r'(?<!\!)('
              r'(?:\[((?:(?>[^\[\]\n\r]+?)|!\[[^\[\]\n\r]*?\])+?)\])?'
              r'\[((?:(?>[^\[\]\n\r]+?)|!\[[^\[\]\n\r]*?\])+?)\]'
              r'(?:\(\s*([^\n\r\t\)]+?)\s*(?:\"([^\"\n\r]*)\")?\s*\))?'
              r'(?:' + BUILDUP_DATA_REGEX + ')?'
              ')')
LINK_REF_REGEX = (r"""(^[ \t]*\[(.+)\]:[ \t]*([^\"\' \t\n\r]*)"""
                  r"""(?:[ \t]+(\"|')((?:\\\4|(?!\4).)*?)\4)?[ \t]*$)""")


def replace_regex_group(string, replacement, match_obj, group_no):
    """
    For replace a specific regex group in a string with a replacement string.
      string - is the full string before matching,
      replacemnt - string to be replaced
      match_obj - match object, the result of regex.match()
      group_no -  the number of the group to be replaced
    """
    if match_obj.group(group_no) is None:
        return string

    groups_before = match_obj.string[:match_obj.start(group_no)]
    groups_after = match_obj.string[match_obj.end(group_no):]
    rep = groups_before + replacement + groups_after
    return string.replace(match_obj.string, rep)

def _check_if_condition(if_condition, variables):
    if variables is None:
        variables = {}

    cond_regex = (r'^((var_[a-zA-z0-9_\-]+|targetformat) +(is(?: +not)?) +([a-zA-z0-9_\-]+))'
                  r'(?: +(?:and|or) +(?:var_[a-zA-z0-9_\-]+|targetformat) +is(?: +not)? +[a-zA-z0-9_\-]+)*$')

    and_or_regex = r'( +(and|or) +)'

    match = re.match(cond_regex, if_condition)
    if match is None:
        _LOGGER.warning("Cannot parse the if condition %s", if_condition)
        return False

    expression = ''
    while match is not None:
        match_var = match.group(2)
        match_condition = match.group(3)
        match_value = match.group(4)

        result =  variables[match_var] == match_value if match_var in variables else False
        if match_condition == "is not":
            result = not result
        expression += str(result)

        if_condition = if_condition[len(match.group(1)):]
        and_or_match = re.match(and_or_regex, if_condition)
        if and_or_match is not None:
            expression+= " " + and_or_match.group(2) + " "
            if_condition = if_condition[len(and_or_match.group(1)):]
        match = re.match(cond_regex, if_condition)
    # expression can only be boolean operations and should be save to eval
    return eval(expression) #pylint: disable=eval-used

def _parse_include_dict(inc_dict, variables):
    """
    Parse the dictionary representation of an include statment. Return whether the to include
    based on if-condition, and return the variables to be passed into the include.
    """
    execute_include = True
    inc_variables = copy(variables)
    for key in inc_dict:
        if key.startswith('var_'):
            #Create dictionary if currently None
            if inc_variables is None:
                inc_variables = {}
            inc_variables[key] = inc_dict(key)
        if key == "if":
            if_condition = inc_dict['if']
            if if_condition is None:
                _LOGGER.warning("Incomplete if condition for include statement")
            else:
                execute_include = _check_if_condition(if_condition, variables)
        elif key not in ("include", "includetext"):
            _LOGGER.warning("Key '%s' is not recognised for include statement", key)
    return execute_include, inc_variables

def _process_value(value):
    if value is not None:
        #if not none it is a string.
        #Strip any whitespace from either end
        value = value.strip()
        if value.startswith(("'", '"')):
            #remove quotes from quoted values
            value = value[1:-1]
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
    return value

def parse_inline_data(data, allow_line_break_quotes=False):
    """
    Parses the inline key:value pair data. Keys are either strings or boolean
    set with the string "true" or "false" (case insensitive). To set the literal
    string true or false put the value in quotes. Keys are case insensive and can
    only contain the caracters a-z. Cannot contain any of { } : , " '
    To use these character you will need to put the value in single or double
    quotes.
    The keys "step" and "ouput" return True if they are entered with no value.
    """

    empty_is_true = ['step', 'make', 'output', 'bom', 'previewpage', 'zip', 'hidden', 'noicons', 'titleimage']
    if data in [None, '']:
        return None

    # This regex finds a key value pair at the start of the data string
    # the pair ends in the end of the string or a comma
    # The key can is case insensitve and can only be the letters a-z or _
    # The value cannot contain { } : , " '
    # To use these characters the value should be in quotes
    if allow_line_break_quotes:
        reg = re.compile(r'^\s*([a-zA-Z_]+)(?:\s*:\s*'
                         r'''([^{}:,\n\r\"\']*|\"[^\"]*\"|\'[^\']*\'))?'''
                         r'\s*(?:$|,)')
    else:
        reg = re.compile(r'^\s*([a-zA-Z_]+)(?:\s*:\s*'
                         r'''([^{}:,\n\r\"\']*|\"[^\n\r\"]*\"|\'[^\n\r\']*\'))?'''
                         r'\s*(?:$|,)')
    data_dict = {}
    alldata = data
    while len(data.lstrip()) > 0:
        match = reg.match(data)
        if match is None:
            _LOGGER.warning("Cannot parse the buildup data %s.", alldata)
            return None
        key = match.group(1).lower()
        value = _process_value(match.group(2))
        if key in empty_is_true and value is None:
            value = True
        data_dict[key] = value
        data = data[match.end(0):]
    if not data_dict:
        return None
    return data_dict

def separate_yml_md(raw_text):
    """
    Seperate out the yml front matter from markdown.
    Return the metadata as a dictionary, the markdown content (stripped), and the offet of
    the markdown content from the start of the raw text input.
    """
    try:
        md_metadata = frontmatter.loads(raw_text, handler=YAMLHandler()).to_dict()
        md = md_metadata['content']
        del md_metadata['content']
        if not  md_metadata:
            if md.strip() != raw_text.strip():
                _LOGGER.warning("Page starts with unreadable metadata block")
                md = raw_text
    except (ScannerError, ParserError):
        _LOGGER.warning("Page starts with unreadable metadata block")
        md_metadata = {}
        md = raw_text

    md_offset = raw_text.index(md)
    return md_metadata, md, md_offset

def get_variable_uses(md, force_prepended_var=True):
    """
    Returns a list of each variable use. list of 3-tuples containing: full match,
    var name, default value
    """
    if force_prepended_var:
        var_matches =  re.findall(r"(\{\{[ \t]*(var_[0-9a-zA-Z\-_]+)[ \t]*(?:,([^\r\n]+?))?\}\})",
                                  md,
                                  re.MULTILINE)
    else:
        var_matches =  re.findall(r"(\{\{[ \t]*([0-9a-zA-Z\-_]+)[ \t]*(?:,([^\r\n]+?))?\}\})",
                                  md,
                                  re.MULTILINE)
    output_vars = []
    for match in var_matches:
        this_var = (match[0], match[1], None)
        if match[2] == "":
            output_vars.append(this_var)
            continue
        match_data = parse_inline_data(match[2])
        if match_data is None:
            output_vars.append(this_var)
            continue
        for key in match_data:
            if key.lower() == "default":
                this_var = (match[0], match[1], match_data[key])
            else:
                _LOGGER.warning("Could not parse %s during variable use", key)
        output_vars.append(this_var)
    return output_vars

def proccess_buildup_snippet(raw_text, page_path, url_translator, allow_images=False):
    """
    Parses short snippets of buildup such as those in a note feild.
    """
    parser = BuildUpParser(raw_text, page_path)
    if allow_images:
        number_of_links = len(parser.plain_links)+len(parser.images)
    else:
        number_of_links = len(parser.plain_links)

    if len(parser.all_links_and_images) != number_of_links:
        _LOGGER.warning("Build-up snippet can only contain plain links, not images "
                        "or buildup links")
        return raw_text

    processed_text = copy(raw_text)
    for link in parser.plain_links:
        if link.is_inline_ref:
            _LOGGER.warning("The link [%s] is a reference style link. "
                            "Build-up snippets can't include reference links",
                            link.linktext)
        link_md = link.link_md(url_translator)
        processed_text = processed_text.replace(link.fullmatch, link_md)

    if allow_images:
        for image in parser.images:
            processed_text = processed_text.replace(image.fullmatch, image.image_md(url_translator))
    return processed_text

class BuildUpParser():
    """
    This is main parser for reading the buildup.
    It is not really a parser, it is just about 8 or so regexs that find the BuildUp
    specific syntax.
    An object is initialised with the raw text to parse, the directory of the page the
    text is from so that the any relative links can be translated
    """

    def __init__(self, raw_text, page_path, doc=None, variables=None, live_edit=False):
        self._live_edit = live_edit
        self._reprocess_needed = True
        self._page_path = page_path
        self._raw_text = raw_text
        self._doc = doc
        self._preprocess_warnings = []
        self._includes = []
        self._yml_header, self._raw_md, self._md_offset = separate_yml_md(self._raw_text)
        self._make_data = self._read_make_data()
        self._details = self._read_details_header()
        if variables is None:
            variables = {}
        else:
            #copy so it doesn't affect other uses of variables
            variables = copy(variables)
        if self._doc:
            variables['targetformat'] = self._doc.config.target_format
        self._preprocess_md(variables)
        self._part_data = self._read_part_data()
        self._link_refs = []
        self._buildup_links = []
        self._images = []
        self._plain_links = []

        self._find_links()
        self._qaqc_blocks = self._get_qaqc_blocks()

    @property
    def link_refs(self):
        """
        Returns a list of Link objects, one for each link reference in the page
        """
        return self._link_refs

    @property
    def step_links(self):
        """
        Returns a list of Link objects, one for each link to a step on the page
        """
        return [link for link in self._buildup_links if link.is_step]

    @property
    def reprocess_needed(self):
        """
        Preprocessing did not complete as it is waiting on another page.
        """
        return self._reprocess_needed

    @property
    def part_links(self):
        """
        Returns a list of Link objects, one for each inline part link on the page
        """
        return [link for link in self._buildup_links if link.is_part]

    @property
    def make_links(self):
        """
        Returns a list of Link objects, one for each make link on the page
        """
        return [link for link in self._buildup_links if link.is_make]

    @property
    def outputs(self):
        """
        Returns a list of Link objects, one for each output from the parsed page
        """
        return [link for link in self._buildup_links if link.is_output]

    @property
    def bom_links(self):
        """
        Returns a list of Link objects, one for each output from the parsed page
        """
        return [link for link in self._buildup_links if link.is_bom]

    @property
    def zip_links(self):
        """
        Returns a list of Link objects, one for each output from the parsed page
        """
        return [link for link in self._buildup_links if link.is_zip]

    @property
    def images(self):
        """
        Returns a list of Image objects, one for each image
        """
        return self._images

    @property
    def plain_links(self):
        """
        Returns a list of Link objects, one for each link that is not a build up link
        """
        return self._plain_links

    @property
    def all_links(self):
        """
        Returns a list of Link objects, one for each link in the page.
        Doesn't return images. See all_links_and_images()
        """
        return self._plain_links+self._buildup_links

    @property
    def all_links_and_images(self):
        """
        Returns a list of Link and Image objects, one for each link/image
        in the page.
        """
        return self.all_links+self.images

    @property
    def in_page_steps(self):
        """
        Returns the in-page steps for your page in a dictionary with:
        heading, id, fullmatch
        """
        return self._get_in_page_steps()

    @property
    def steps(self):
        """
        Returns a simple list of the filespaths of all pages linked to a steps
        """
        return [link.link_rel_to_root for link in self.step_links]

    @property
    def inline_boms(self):
        """
        Returns a list of each fullmatch of the syntax for an in-line bill of materials
        """
        return re.findall(r"(\{\{[ \t]*BOM[ \t]*\}\})", self._preprocessed_md, re.MULTILINE)

    @property
    def bom_links_dep(self):
        """
        Returns a list of each fullmatch of the syntax for the old style in-line bill of materials
        """
        bomlinks = re.findall(r"(\{\{[ \t]*BOMlink[ \t]*\}\})", self._preprocessed_md, re.MULTILINE)
        if len(bomlinks) > 0:
            _LOGGER.warning('Depreciation warning. The {{BOMlink}} syntax has been replaced by'
                            ' appending {bom} to a link.')
        return bomlinks

    @property
    def qaqc_blocks(self):
        """
        The blocks of yaml for specifying QA/QC questions
        """
        return copy(self._qaqc_blocks)

    def page_lists(self):
        """
        Returns a list of each page list
        """
        list_matches =  re.findall(r"(\{\{[ \t]*(listpages[^\r\n]*?)[ \t]*\}\})",
                                   self._preprocessed_md,
                                   re.MULTILINE)
        page_lists = []
        for list_match in list_matches:
            page_list_dict = parse_inline_data(list_match[1])
            if page_list_dict is None:
                continue
            page_lists.append((list_match[0], page_list_dict))
        return page_lists

    @property
    def includes(self):
        """returns the pages this page includes"""
        return copy(self._includes)

    def _get_include_statements(self, md):
        """
        Returns a list of each include statement
        """
        return re.findall(r"(\{\{[ \t]*(include:[^\r\n]+?)[ \t]*\}\})", md, re.MULTILINE)

    def _get_includetext_statements(self, md):
        pat = r"""(\{\{[ \t]*(includetext:[ \t]*((?:\"(?:[^\"]|\\\")+\"|\'(?:[^\']|\\\')+\')[ \t]*,[^\r\n]+?))\}\})"""
        return re.findall(pat, md, re.MULTILINE)

    def _get_foreachmakeitem_statements(self, md):
        pat = r"""(\{\{[ \t]*(foreachmakeitem:[ \t]*((?:\"(?:[^\"]|\\\")+\"|\'(?:[^\']|\\\')+\')[ \t]*(?:,[^\r\n]+?)?))\}\})"""
        return re.findall(pat, md, re.MULTILINE)

    def _get_qaqc_blocks(self, md=None):
        if md is None:
            md = self._preprocessed_md
        pat =  r"^```qaqc\s*\n(?:.|\n)*?^```"
        return re.findall(pat, md, re.MULTILINE)

    @property
    def reference_defined_parts(self):
        """
        Returns a list of link objets for the parts defined by references
        """
        list_of_parts = []
        for link_ref in self._link_refs:
            if link_ref.is_part:
                list_of_parts.append(link_ref)
        return list_of_parts

    @property
    def inline_parts(self):
        """
        Returns a list of link objects for the parts defined inline
        """
        list_of_parts = []
        for part_link in self.part_links:
            list_of_parts.append(part_link)
        return list_of_parts

    @property
    def raw_md(self):
        """
        Return the raw markdown (without frontmatter)
        """
        return self._raw_md

    @property
    def metadata(self):
        """
        Return the metadata in the front matter
        """
        return self._yml_header

    @property
    def part_data(self):
        """
        Return the part data from the metadata or return None
        """
        return self._part_data

    @property
    def make_data(self):
        """
        Return the make data from the metadata or return None
        """
        return self._make_data

    @property
    def details(self):
        """
        Return the details header object
        """
        return self._details

    @property
    def preprocessed_md(self):
        """
        Return a text with include statments replaced
        """
        return self._preprocessed_md

    @property
    def preprocessed_md_with_details(self):
        """
        Return a text with include statments replaced and with markdown version of details header
        """
        if self.details is None:
            return self._preprocessed_md
        return self._preprocessed_md_inject_details(self.details.as_markdown())

    @property
    def preprocessed_md_with_details_placeholder(self):
        """
        Return a text with include statments replaced and with a placeholder for the details header
        """
        if self.details is None:
            return self._preprocessed_md
        return self._preprocessed_md_inject_details("\n\n{{BUILDUPDETAILS}}\n\n")

    def _preprocessed_md_inject_details(self, details_md):
        #If there is no title put details at top of page
        if self.get_title_match() == "":
            return details_md+self._preprocessed_md
        return self._preprocessed_md.replace(self.get_title_match(),
                                             self.get_title_match()+details_md)

    @property
    def preprocess_warnings(self):
        """
        Returns a list of tuples which can be raised as logger warnings for
        missing variables. These should be read and output when generating the
        final output. These are raised later so the warnings are not thrown for
        the first pass of a page (without variables) if all output versions of the
        page have variables assigned.
        """
        return self._preprocess_warnings

    def _preprocess_md(self, variables):
        """
        Preprocessing involves replacing variables, include statments, and icon links.
        In the live editor it wraps include statments and adds links back to editor positions.
        """
        updated_md = copy(self._raw_md)
        self._reprocess_needed = False

        if self._live_edit:
            updated_md = self._add_editor_links(updated_md)

        updated_md = self._replace_vars(updated_md, variables)

        ##Return without includes if doc is None. This happens when parsing a snippet.
        if self._doc is None:
            self._preprocessed_md = updated_md
            return

        url_translator = URLRules().create_translator(self._page_path)
        for statement in self._get_include_statements(updated_md):
            updated_md = self._process_include_statment(updated_md,
                                                        statement,
                                                        variables,
                                                        url_translator)
        for statement in self._get_includetext_statements(updated_md):
            updated_md = self._process_includetext_statement(updated_md,
                                                             statement,
                                                             variables)
        for statement in self._get_foreachmakeitem_statements(updated_md):
            updated_md = self._process_foreachmakeitem_statement(updated_md,
                                                             statement,
                                                             variables)
        updated_md = self._process_icon_links(updated_md, url_translator)

        if 'make_linktext' in variables:
            link_txt = variables['make_linktext']
            qtr_str = str(variables['make_qty'])
            out_str = '['+ link_txt + ']{output, hidden, qty:' + qtr_str +'}'
            updated_md += '\n\n' + out_str

        self._preprocessed_md = updated_md

    def _add_editor_links(self, updated_md):
        """
        Add links to the correct place in the editor.
        """

        # Replace external and final match with walrus operator once we drop python 3.7

        block_regex = r'(?<!>)\n\n([^\n<](.|\n)*?)(?:\n\n|$)'

        #Finding any character after 2 or more newlines in a row, unless it is a <
        match = re.search(block_regex, updated_md)
        cumulative_offset = 0
        while match:
            match_start = match.start(1)
            match_raw_start = match_start+self._md_offset-cumulative_offset
            match_end = match.end(1)
            match_raw_end = match_end+self._md_offset-cumulative_offset
            range_txt = str(match_raw_start)+'--'+str(match_raw_end)
            #insert and html tag pointing to the position
            inserted_tag = r'<img class="goto-line" src="/static/Icons/edit.png" id="goto-line-'+range_txt+'">\n\n'
            updated_md = updated_md[:match_start] + inserted_tag + updated_md[match_start:]
            cumulative_offset += len(inserted_tag)
            match = re.search(block_regex, updated_md)
        return updated_md

    def _replace_vars(self, updated_md, variables):
        """Replace the variables in text. A preprocessing step"""
        for var_use in get_variable_uses(self._raw_md):
            var = var_use[1]
            if variables is not None and var in variables:
                replacement = variables[var]
                if replacement is None:
                    #If a variable is defined as empty None is created.
                    replacement = ''
                updated_md = updated_md.replace(var_use[0], replacement)
            elif var_use[2] is None:
                self._preprocess_warnings.append(('Page variable %s used but undefined', var))
                updated_md = updated_md.replace(var_use[0], "")
            else:
                updated_md = updated_md.replace(var_use[0], var_use[2])
        return updated_md

    def _process_include_statment(self, updated_md, inc_statement, variables, url_translator):
        """Process a single include statment and return result"""

        inc_dict = parse_inline_data(inc_statement[1])
        if inc_dict is None:
            _LOGGER.warning('Poorly formatted include statement')
            return updated_md

        execute_include, inc_variables = _parse_include_dict(inc_dict, variables)
        if not execute_include:
            return updated_md.replace(inc_statement[0], '')

        pagename = inc_dict['include']
        page_obj = self._doc.get_page_by_path(pagename)
        if page_obj is None:
            #Page object is None, either page has not yet been created or is missing
            if pagename in self._doc.filelist:
                #Not yet created. Flag that reprocessing is needed and return unchanged md
                self._reprocess_needed = True
                return updated_md
            # Page is missing. Warn and replace statement with a message
            self._preprocess_warnings.append(('Cannot include "%s"', pagename))
            return updated_md.replace(inc_statement[0], f"**Failed to include {pagename}**")

        if len(page_obj.steps) > 0:
            # There are page steps in the page to include. This will cause confusion with
            # the page ordering. Warn and replace statement with message
            _LOGGER.warning("Cannot include page with step links.")
            return updated_md.replace(inc_statement[0], f"**Failed to include {pagename}**")


        page_obj = page_obj.get_variation(inc_variables)

        if page_obj.reprocess_needed:
            # Page to include still needs processing. Flag that a reprocess is needed and
            # return current md
            self._reprocess_needed = True
            return updated_md

        #Finally if not returned yet we can execute the include:
        return self._execute_include_statment(updated_md, inc_statement, page_obj, url_translator)

    def _process_includetext_statement(self, md, inc_statement, variables):
        inc_dict = parse_inline_data(inc_statement[1], allow_line_break_quotes=True)
        if inc_dict is None:
            _LOGGER.warning('Poorly formatted includetext statement')
            return md
        execute_include, _ = _parse_include_dict(inc_dict, variables)
        replacement = inc_dict["includetext"] if execute_include else ""
        return md.replace(inc_statement[0], replacement)

    def _process_foreachmakeitem_statement(self, md, statement, variables):
        statement_dict = parse_inline_data(statement[1], allow_line_break_quotes=True)
        if statement_dict is None:
            _LOGGER.warning('Poorly formatted foreachmakeitem statement')
            return md


        if 'make_template_data' not in variables:
            return md.replace(statement[0], '')

        replacement_lines = []
        output_statements = []
        for key, data in variables['make_template_data'].items():
            item_vars = deepcopy(data)
            item_vars['id'] = key
            if 'qty' not in item_vars:
                _LOGGER.warning("Unknown quantity for make item.")
                item_vars['qty'] = 1
            line = statement_dict['foreachmakeitem']
            for var_use in get_variable_uses(line, force_prepended_var=False):
                var = var_use[1]
                if var in item_vars:
                    replacement = item_vars[var]
                    if replacement is None:
                        #If a variable is defined as empty None is created.
                        replacement = ''
                    if var.endswith('-qty'):
                        replacement = replacement * item_vars['qty']
                    if var.endswith('-file'):
                        page_dir = posixpath.dirname(self._page_path)
                        replacement = posixpath.relpath(replacement, page_dir)
                    line = line.replace(var_use[0], str(replacement))
                elif var_use[2] is None:
                    self._preprocess_warnings.append(('Make template variable %s used but undefined', var))
                    line = line.replace(var_use[0], "")
                else:
                    line = line.replace(var_use[0], var_use[2])

            replacement_lines.append(line)
            out_statement = '['+ key + ']{output, hidden, qty:' + str(item_vars['qty']) +'}'
            output_statements.append(out_statement)

        replacement = '\n'.join(replacement_lines)
        md = md.replace(statement[0], replacement)
        md += "\n\n"+'\n'.join(output_statements)

        return md


    def _execute_include_statment(self, updated_md, inc_statement, page_obj, url_translator):
        """
        Replace incldue stament with contents of page
        """
        try:
            page_obj.set_as_included(self._page_path)
            self._includes.append(page_obj.filepath)
            md = page_obj.preprocessed_md
            for link in page_obj.all_links_and_images:
                translated = url_translator.simple_translate(link.raw_linklocation)
                if isinstance(link, Image):
                    match_obj = re.match(IMAGE_REGEX, link.fullmatch)
                    md = replace_regex_group(md, translated, match_obj, 3)
                else:
                    match_obj = re.match(LINK_REGEX, link.fullmatch)
                    md = replace_regex_group(md, translated, match_obj, 4)
            for link_ref in page_obj.all_link_refs:
                translated = url_translator.simple_translate(link_ref.raw_linklocation)
                match_obj = re.match(LINK_REF_REGEX, link_ref.fullmatch)
                md = replace_regex_group(md, translated, match_obj, 3)
            if self._live_edit:
                html_start = '<div markdown="span" class="live-include">'
                html_start += f'<div class="live-include-link"><a href="/{page_obj.filepath}/-/editor">Included from {page_obj.filepath}</a></div>'
                html_start += '<div markdown="block" class="live-included-content">'
                md = f'{html_start}\n\n{md}\n\n</div></div>'
            return updated_md.replace(inc_statement[0], md)
        except RecursionError:
            # Based on current implementation this shouldn't execute, it is here in case
            _LOGGER.warning("Recursive include detected between %s and %s",
                            self._page_path,
                            page_obj.filename)
            return updated_md.replace(inc_statement[0], "**Recursive page include detected**")

    def _process_icon_links(self, md, url_translator):
        _, plain_links = self._get_links(md=md)
        for link in plain_links:
            if link.linktext == "i":
                icon_link = url_translator.simple_translate('static/Icons/info.png')
                icon_md = f'![info]({icon_link} "More information")'+'{: .smallicon}'
                md = md.replace(link.fullmatch, link.link_md(text_override=icon_md))
        return md

    def get_title(self):
        """
        Gets the page title by looking for the first heading with a single #
        """
        return self._match_title()[1]

    def get_title_match(self):
        """
        Gets the match to page title by looking for the first heading with a
        single #
        """
        return self._match_title()[0]

    def _read_part_data(self):
        if 'PartData' not in self._yml_header:
            return None

        try:
            part_data = self._yml_header['PartData']
            if not isinstance(part_data, dict):
                _LOGGER.warning("Page header part data is incomplete")
                return None
            part_data["Name"] = self.get_title()
            part_data_obj = PartDataSchema().load(part_data)
            return part_data_obj
        except ValidationError as err:
            raise_validation_error_as_warning(err)
            return None
        except ParserError:
            _LOGGER.warning("Invalid yaml in header")
            return None

    def _read_make_data(self):
        if 'Make' not in self._yml_header:
            return {}
        try:
            make = self._yml_header['Make']
            if not isinstance(make, dict):
                _LOGGER.warning("Page header make data is incomplete")
                return {}
            return process_make_data(make, self._page_path)
        except ParserError:
            _LOGGER.warning("Invalid yaml in header")
            return {}
        except (KeyError, ValueError, TypeError, AttributeError):
            _LOGGER.warning("Problem parsing make data")
            return {}

    def _read_details_header(self):
        if 'Details' not in self._yml_header:
            return None
        try:
            details = self._yml_header['Details']
            if not isinstance(details, dict):
                _LOGGER.warning("Page header details are incomplete")
                return None
            return Details(details)
        except ParserError:
            _LOGGER.warning("Invalid yaml in header")
            return None

    def _match_title(self):
        headings = re.findall(r"(^#(?!#)[ \t]*(.*)$)",
                              self._preprocessed_md,
                              re.MULTILINE)
        if len(headings) > 0:
            title = headings[0]
        else:
            title = ("", "")
        return title

    def _find_links(self):
        self._link_refs = self._get_link_references()
        self._buildup_links, self._plain_links = self._get_links()
        self._images = self._get_images()

    def _get_link_references(self):
        """
        Function to find link reference of any reference style links.
        Returns a list of Link objects
        """

        # Looking for link references. These must use "*" or '*' to define alt-text not (*)
        # Group 1: link text
        # Group 2: link location
        # Group 3: either a ' or a ", captured so regex can find the equivalent
        # Group 4: alt text
        link_ref_matches = re.findall(LINK_REF_REGEX,
                                      self._preprocessed_md,
                                      re.MULTILINE)

        link_refs = []
        for link_ref in link_ref_matches:
            alttext = link_ref[4]
            # Search for buildup data in alt-text
            data_match = re.findall(r"""({([^:](?:[^}\'\"]|\'[^\'\r\n]*\'|\"[^\'\r\n]*\")*)})""",
                                    alttext)
            if len(data_match) == 0:
                buildup_data = None
            else:
                if len(data_match) > 1:
                    _LOGGER.warning("Multiple sets of data found in link reference alt-text: %s",
                                    alttext)
                # Only match the last group of data found, warning if more than one
                # buildup_data is the text inside braces
                buildup_data = data_match[-1][1]
                # Replace all including braces
                alttext = alttext.replace(data_match[-1][0], "")
            if link_ref[2] == "":
                location = ""
            else:
                location = link_ref[2]
            link_ref_dict = {"fullmatch": link_ref[0],
                             "linktext": link_ref[1],
                             "linklocation": location,
                             "alttext": alttext,
                             "buildup_data": parse_inline_data(buildup_data)}
            link_refs.append(create_link_object(link_ref_dict,
                                                self._page_path,
                                                link_type=BaseLink.LINK_REF))

        return link_refs


    def _get_links(self, md=None):
        """
        Function to find all markdown links
        Returns two list of Link objects
        The first is a list of buildup links (links with {} after them)
        The second is a list of plain markdown links
        """

        buildup_links = []
        plain_links = []
        if md is None:
            md = self.preprocessed_md_with_details
            link_references = self._link_refs
        else:
            #When just searching some markdown do not replace link references
            link_references = []
        link_matches = re.findall(LINK_REGEX, md, re.MULTILINE)

        for link in link_matches:
            if link[3] == "":
                linklocation = ""
            else:
                linklocation = link[3]
            link_dict = {"fullmatch": link[0],
                         "overridetext": link[1],
                         "linktext": link[2],
                         "linklocation": linklocation,
                         "alttext": link[4],
                         "buildup_data": parse_inline_data(link[5])}
            link_obj = create_link_object(link_dict,
                                          self._page_path,
                                          link_references=link_references,
                                          make_data=self.make_data)
            if link_obj.is_buildup:
                buildup_links.append(link_obj)
            else:
                plain_links.append(link_obj)
        return buildup_links, plain_links

    def _get_images(self):
        """
        Function to find images
        Returns a list of Image objects
        """

        # Find images in the text
        # Group 1: all
        # Group 2: alt-text
        # Group 3: image-path
        # group 4: hover text
        images_info = re.findall(IMAGE_REGEX,
                                 self.preprocessed_md_with_details,
                                 re.MULTILINE)

        images = []
        for image in images_info:
            image_location = image[2]
            image_dict = {"fullmatch": image[0],
                          "alttext": image[1],
                          "imagelocation": image_location,
                          "hovertext": image[3],
                          "buildup_data": parse_inline_data(image[4])}
            images.append(Image(image_dict,
                                self._page_path,
                                link_references=self._link_refs))
        return images

    def _get_in_page_steps(self):
        """
        Returns h2 headings with data info afterwards. Used to locate page steps.
        """

        in_page_steps = []
        step_ids = []

        # regex:
        # Group 1 (heading[0]) Full match
        # Group 2 (heading[1]) is the heading text
        # Group 3 (heading[2]) is the inline buildup data
        headings = re.findall(r"^(##(?!#)[ \t]*(.*?)[ \t]*{([^:][^}\n]*)})$",
                              self._preprocessed_md,
                              re.MULTILINE)

        for heading in headings:
            heading_info = parse_inline_data(heading[2])

            if heading_info is None:
                continue

            if "pagestep" in heading_info:
                step_id = heading_info["pagestep"]
                if step_id is None:
                    step_id = clean_id(heading[1])
                elif clean_id(step_id) != step_id:
                    old_id = step_id
                    step_id = clean_id(step_id)
                    _LOGGER.warning('Step ID "%s" not valid, changed to "%s"', old_id, step_id)

                if "nosubheading" in heading_info:
                    nosubheading = True
                    del heading_info["nosubheading"]
                else:
                    nosubheading = False

                if step_id not in step_ids:
                    step_ids.append(step_id)
                else:
                    _LOGGER.warning('Step ID "%s" is already used', step_id)
                in_page_steps.append({"heading": heading[1],
                                      "id": step_id,
                                      "nosubheading": nosubheading,
                                      "fullmatch": heading[0]})
                del heading_info["pagestep"]

            if len(heading_info.keys()) > 0:
                keynames = ""
                for key in heading_info:
                    keynames += key + ", "
                _LOGGER.warning("Unused keys '%s' in heading [%s]",
                                keynames[:-2],
                                heading[1],
                                extra={'fussy':True})
        return in_page_steps

    def get_special_blockquotes(self, html_blocks=True):
        caution_blocks = self._get_block_by_regex(r"^>!(?!\!)[^\n]*(?:\n>!(?!\!)[^\n]*)*",
                                                  r"^>![ \t]*",
                                                  "caution-block",
                                                  html_blocks)
        warn_blocks = self._get_block_by_regex(r"^>!!(?!\!)[^\n]*(?:\n>!!(?!\!)[^\n]*)*",
                                               r"^>!![ \t]*",
                                               "warning-block",
                                               html_blocks)
        info_blocks = self._get_block_by_regex(r"^>i(?=(?: |\n))[^\n]*(?:\n>i(?=(?: |\n))[^\n]*)*",
                                               r"^>i[ \t]*",
                                               "info-block",
                                               html_blocks)
        help_blocks = self._get_block_by_regex(r"^>\?(?=(?: |\n))[^\n]*(?:\n>\?(?=(?: |\n))[^\n]*)*",
                                               r"^>\?[ \t]*",
                                               "help-block",
                                               html_blocks)
        return caution_blocks + warn_blocks + info_blocks + help_blocks

    def _get_block_by_regex(self, block_regex, line_start_regex, css_class, html_blocks):
        blocks = re.findall(block_regex, self._preprocessed_md, re.MULTILINE)
        block_list = []
        for block in blocks:
            if html_blocks:
                clean_block = re.sub(line_start_regex, "", block, flags=re.MULTILINE)
                rep_block = f'<div markdown="1" class="{css_class}">\n{clean_block}\n</div>'
                block_list.append((block, rep_block))
            else:
                rep_block = re.sub(line_start_regex, "> ", block, flags=re.MULTILINE)
                block_list.append((block, rep_block))
        return block_list

class Details:
    """
    Class to store and process the details headers at the top of buildup pages
    """

    def __init__(self, details_dict):
        self.thumbnail = None
        self.difficulty = None
        self.time = None
        self.skills = None
        self._validate(details_dict)


    def _validate(self, details_dict):
        # As schema is simple, but may be extended freely not using marshmallow to
        # parse. This might need to change
        self._dict = {}
        for key in details_dict:
            if key.lower() == "thumbnail":
                if not isinstance(details_dict[key], str):
                    _LOGGER.warning("Could not parse page thumbnail")
                else:
                    self.thumbnail = details_dict[key]
            elif key.lower() == "difficulty":
                if not isinstance(details_dict[key], str):
                    _LOGGER.warning("Could not parse page difficulty")
                else:
                    self.difficulty = details_dict[key]
            elif key.lower() == "time":
                if not isinstance(details_dict[key], str):
                    _LOGGER.warning("Could not parse page time")
                else:
                    self.time = details_dict[key]
            elif key.lower() == "skills":
                if not isinstance(details_dict[key], list):
                    _LOGGER.warning("Could not parse page skills")
                else:
                    self.skills = []
                    for skill in details_dict[key]:
                        if not isinstance(skill, str):
                            _LOGGER.warning("Problem occured parsing skill list")
                        else:
                            self.skills.append(skill)
            elif isinstance(details_dict[key], str):
                self._dict[key] = details_dict[key]
            else:
                _LOGGER.warning("Could not parse %s in page details", key)

    def as_markdown(self):
        """
        Return a markdown interpretation of the details header. This is not used when generating
        HTML due to the serious limitations of markdown tables.
        """
        md = "\n\n"
        if self.thumbnail is not None:
            md = f"![page thumbnail]({self.thumbnail})\n\n"
        if (self.difficulty is not None) or (self.time is not None) or (self.skills is not None) or self._dict:
            md += "| Detail        | Value                       |\n"
            md += "|---------------|-----------------------------|\n"
            if self.difficulty is not None:
                md += f"| Difficulty    | {self.difficulty}      |\n"
            if self.time is not None:
                md += f"| Time Required | {self.difficulty}      |\n"
            if self.skills is not None:
                skills_str = ', '.join(self.skills)
                md += f"| Skills        | {skills_str}      |\n"
            for key, value in self._dict.items():
                md += f"| {key}        | {value}      |\n"
        md += "\n\n"
        return md

    def as_output_dict(self, page_path, url_translator):
        """
        Return an dictionary of the details with buildup processed and urls translated
        """
        out_dict = {}
        if self.thumbnail is not None:
            raw_md = f"![page thumbnail]({self.thumbnail})"
            md = proccess_buildup_snippet(raw_md, page_path, url_translator, allow_images=True)
            out_dict['thumbnail'] = md
        if self.difficulty is not None:
            md = proccess_buildup_snippet(self.difficulty, page_path, url_translator)
            out_dict['difficulty'] = md
        if self.time is not None:
            md = proccess_buildup_snippet(self.time, page_path, url_translator)
            out_dict['time'] = md
        if self.skills is not None:
            out_dict['skills'] = []
            for skill in self.skills:
                md = proccess_buildup_snippet(skill, page_path, url_translator)
                out_dict['skills'].append(md)
        for key, value in self._dict.items():
            md = proccess_buildup_snippet(value, page_path, url_translator)
            out_dict[key] = md
        return out_dict

def process_make_data(make_dict, page_path):
    make_data = {}
    for name, data in make_dict.items():
        if 'template' not in [key.lower() for key in data.keys()]:
            _LOGGER.warning('Make data for "%s" is missing a template', name)
            continue
        make_data[name.lower()] = {}
        for key, value in data.items():
            l_key = key.lower()
            if l_key.endswith('-qty'):
                proc_value = Quantity(str(value))
            elif l_key.endswith('-file'):
                proc_value = get_root_url(value, page_path)
            else:
                proc_value = str(value)
            make_data[name.lower()][l_key] = proc_value
    return make_data
