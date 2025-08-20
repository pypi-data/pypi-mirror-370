"""
A submodule for parsing QA/QC questions supplied as YAML.
"""
from typing import Optional, Any, Union
from copy import copy
import os
import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError
import yaml

from gitbuilding.buildup import utilities

THIS_PATH = os.path.dirname(__file__)
_LOGGER = logging.getLogger('BuildUp.GitBuilding')

HTML_FOR_INVALID = """<div class="qaqc qaqc-invalid">
<strong>Invalid QaQc data</strong>
</div>
"""

class QaQcBlock:
    """
    A class for parsing and processing QA QC instructions.

    These are written in yaml triple backtick code blocks with a `qaqc` id
    """
    _schema: Optional[str] = None
    _md: str
    _data: Optional[dict] = None
    _valid_yml: bool = False
    _validated: bool = False

    def __init__(self, md, form_id, warn=True):
        if not md.startswith(r"```qaqc") or not md.endswith(r"```"):
            raise ValueError("Not a valid QaQc code block!")
        self._schema = None
        self._md = md
        self._form_id = form_id
        yml = md[7:-3].strip()
        try:
            self._data = self._validate_and_parse_yml(yml)
            self._valid_yml = True
            self._validated = True
        except yaml.YAMLError:
            if warn:
                _LOGGER.warning("Invalid YAML in QAQC block")
        except ValidationError:
            self._valid_yml = True
            if warn:
                _LOGGER.warning("The YAML in QAQC block doesn't match the expected structure")

    @property
    def form_id(self):
        """The identifier for this form."""
        return self._form_id

    @property
    def md(self):
        """The markdown that defined this block"""
        return self._md

    @property
    def data(self):
        """A validated dictionary with the data from this block"""
        return copy(self._data)

    @property
    def valid_yml(self):
        """The supplied markdown contained valid yaml.

        This is set true even if it wasn't validated by the schema
        """
        return self._valid_yml

    @property
    def validated(self):
        """The supplied markdown matches the QaQc schema"""
        return self._validated

    @property
    def schema(self):
        """The schema for QaQC blocks"""
        if self._schema is None:
            schema_file = os.path.join(THIS_PATH, "qaqc-schema.json")
            with open(schema_file, 'r', encoding="utf-8") as file_obj:
                schema = json.loads(file_obj.read())
            self._schema = schema
        return self._schema

    def _validate_and_parse_yml(self, yml):
        data = yaml.safe_load(yml)
        validate(instance=data, schema=self.schema)
        return data

    def as_html(self, build_id:str) -> str:
        """Return the HTML for this QAQC block"""

        if self.data is None:
            return HTML_FOR_INVALID

        html = f'<div class="qaqc qaqc-page-form" data-build-id="{build_id}">\n'
        html += "<h3>QA/QC check</h3>\n"
        html += self._html_form(self._form_id)
        html += '<button class="qaqc-complete qaqc-upload-button">Submit to server</button>'
        html += '<button class="qaqc-complete qaqc-download-button">Download as json</button>'
        html += "\n</div>\n\n"
        return html

    def _html_form(self, form_id:str) -> str:
        """
        Return the HTML form for the given data. No validation as this
        is only to be called from _as_html()
        """
        html = f'<form id="{form_id}">\n'
        for question in self.data:
            html += QaQcQuestion(question).as_html()
        html += "\n</form>\n"
        return html


CHECKBOXINPUT = 0
TEXTINPUT = 1
NUMERICINPUT = 2
PHOTOINPUT = 3
FILEINPUT = 4

INPUT_TYPES = {
    "checkbox": CHECKBOXINPUT,
    "text": TEXTINPUT,
    "numeric": NUMERICINPUT,
    "photo": PHOTOINPUT,
    "file": FILEINPUT
}

class QaQcQuestion:
    """
    A class for processing individual QA QC questions
    """

    _data: dict
    _type: int

    def __init__(self, data:dict):
        self._data = data
        # Already validated by jsonschema!
        self._input_type = INPUT_TYPES[data["type"]]

    @property
    def input_type(self) -> int:
        """The input type.

        This is an int that matches one of:
        CHECKBOXINPUT, TEXTINPUT, NUMERICINPUT, PHOTOINPUT, FILEINPUT
        """
        return self._input_type

    def as_html(self) -> str:
        """Return the HTML for this QAQC block"""

        html_id = self._data["id"]
        title = self._data["title"]
        description = self._data.get("description", None)
        html = f'<label for="{html_id}">{title}</label>\n'
        if description is not None:
            html += f'<p class="qaqc-description">{description}</p>\n'

        if self.input_type == CHECKBOXINPUT:
            html += f'<input type="checkbox" id="{html_id}" name="{html_id}"><br>'
        elif self.input_type == TEXTINPUT:
            html += f'<input type="text" id="{html_id}" name="{html_id}"><br>'
        elif self.input_type == NUMERICINPUT:
            html += f'<input type="number" id="{html_id}" name="{html_id}"><br>'
        elif self.input_type == PHOTOINPUT:
            html += f'<input type="file" id="{html_id}" name="{html_id}" accept="image/*" ><br>'
        elif self.input_type == FILEINPUT:
            html += f'<input type="file" id="{html_id}" name="{html_id}" accept="*" ><br>'

        return html

class QaQcStartPage():
    """The data for the page that starts a quality managed build."""

    def __init__(self, pagelist, doc):
        self._pagelist = pagelist
        self._doc = doc
        # The page object for the first page this page ordering.
        self._root_page = self._doc.get_page_by_path(self._pagelist[0])
        page_ordering = utilities.nav_order_from_pagelist(self._pagelist)
        self._next_page = page_ordering[1]
        self._full_qaqc_form = self._generate_full_qaqc_form(page_ordering)

    def _generate_full_qaqc_form(self, page_ordering) -> list[dict[str, Union[str,dict[str, Any]]]]:
        all_valid = True
        full_form = []
        for pagename in page_ordering:

            page = self._doc.get_page_by_path(pagename)
            if page is None:
                continue
            # Page will be None for BOM pages.
            page_blocks = page.get_qaqc_blocks(warn=False)

            for block in page_blocks:
                if block.data is None:
                    all_valid = False
                    continue
                full_form.append({"form_id": block.form_id, "form_structure": block.data})

        if not all_valid:
            _LOGGER.warning("Skipping invalid QaQc blocks when creating full QaQC structure.")
        return full_form

    @property
    def url(self):
        """The url of the start page."""
        return self._root_page.filepath[:-3] + "_qaqc_start.md"

    @property
    def json_url(self):
        """The url for the json form data for this start_page."""
        return self._root_page.filepath[:-3] + "_qaqc_full_form.json"

    @property
    def title(self):
        """The title of the start page."""
        return f"Start quality managed build of {self._root_page.title}"

    @property
    def full_form_json(self) -> str:
        """The full form as json
        
        The form is a list of dictionaries, one for each QaQc block. Each dictionary
        has 2 keys. The form_id, and the form_structure which contains the data for
        that block.
        """
        return json.dumps(self._full_qaqc_form)

    def as_md(self, url_translator) -> str:
        """Return markdown (for with embedded html) for the start page."""
        next_link = url_translator.simple_translate(self._next_page)
        json_link = url_translator.simple_translate(self.json_url)

        md = (f"# {self.title}\n\n"
              "To start a quality managed build either enter a server url or "
              "select build locally."
              "\n\n"
              '<div class="qaqc">\n'
              "  <form\n"
              '    id="qaqc-start-server-form"\n'
              f'    data-build-id="{self._root_page.id_code}"\n'
              f'    data-device-title="{self._root_page.title}"\n'
              f'    data-next-page="{next_link}"\n'
              f'    data-json-url="{json_link}"\n'
              "  >\n"
              '    <label for="qaqc-server-url">QA/QC Server URL:</label>\n'
              '    <input type="text" id="qaqc-server-url" name="server-url" size="40">\n'
              ' </form>\n'
              ' <button class="qaqc-complete" id="qaqc-start-upload-btn">Upload results during build</button>\n'
              ' <button class="qaqc-complete" id="qaqc-start-local-btn">Record locally</button>\n'
              "</div>\n\n")
        return md
