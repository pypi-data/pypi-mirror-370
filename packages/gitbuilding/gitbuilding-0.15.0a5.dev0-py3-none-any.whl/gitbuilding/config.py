"""
This module deals with loading and parsing the configuration file
the main schema GBConfigSchema is subclassed from buildup.ConfigSchema.
All of extra GitBuilding specific options are added. The helper functions
for loading also deal with removing invalid configuration options and
logging a warning.
"""

import os
import logging
import yaml
from marshmallow import fields
from gitbuilding.buildup import ConfigSchema

_LOGGER = logging.getLogger('BuildUp.GitBuilding')

def default_excludes():
    """
    Defines the default list of excluded files.
    """
    return ['README.md']

class GBConfigSchema(ConfigSchema):
    """
    This is a subclass of buildup.ConfigSchema it is used to add all the extra
    configuration options to the base set of options used by BuildUp.
    """
    authors = fields.List(cls_or_instance=fields.Str, load_default=list, data_key='Authors')
    affiliation = fields.Str(load_default=None, allow_none=True, data_key='Affiliation')
    email = fields.Email(load_default=None, allow_none=True, data_key='Email')
    fussy = fields.Bool(load_default="True", data_key='Fussy')
    include_search = fields.Bool(load_default="True", data_key='IncludeSearch')
    exclude = fields.List(cls_or_instance=fields.Str,
                          load_default=default_excludes,
                          data_key='Exclude')
    website_root = fields.Url(load_default="/",
                              relative=True,
                              require_tld=False,
                              data_key='WebsiteRoot')
    variables = fields.Dict(load_default=dict,
                            keys=fields.Str(),
                            values=fields.Str(),
                            data_key='Variables')
    license = fields.Str(load_default=None, allow_none=True, data_key='License')
    license_file = fields.Str(load_default=None, allow_none=True, data_key='LicenseFile')
    primary_color = fields.Str(load_default=None, allow_none=True, data_key="PrimaryColor")
    secondary_color = fields.Str(load_default=None, allow_none=True, data_key="SecondaryColor")
    hover_color = fields.Str(load_default=None, allow_none=True, data_key="HoverColor")
    remove_images_border = fields.Bool(load_default=None,
                                       allow_none=True,
                                       data_key="RemoveImagesBorder")
    remove_images_background = fields.Bool(load_default=None,
                                           allow_none=True,
                                           data_key="RemoveImagesBackground")
    extra_pages_for_pdf = fields.List(cls_or_instance=fields.Str,
                                      load_default=list,
                                      allow_none=True,
                                      data_key="ExtraPagesForPDF")
    # Allow custom tab length: https://python-markdown.github.io/reference/#tab_length
    tab_length = fields.Int(load_default=4, allow_none=False, data_key='TabLength')

def check_config_string(yaml_string):
    """
    Check yaml string to see if valid config
    """
    schema = GBConfigSchema()
    return schema.validate(yaml.safe_load(yaml_string))

def load_config(config_dictionary):
    """
    Loads the build up configuration, any fields in the config_dictionary
    which fail validation are removed. Logging warnings are raised for
    each validation error. A dataclass object containing the
    validated configuration.
    """
    schema = GBConfigSchema()
    # Must run the validation twice as some keys validate off another. If one key is
    # invalid it is removed on the first pass. Second pass will still error
    for _ in range(2):
        warnings = schema.validate(config_dictionary)
        _log_warnings(warnings)
        for key in warnings:
            del config_dictionary[key]
        if warnings == {}:
            #break if there are no warnings
            break
    return schema.load(config_dictionary)

def get_raw_config_data(yamlfile, working_dir):
    """
    Return the raw data from configuration file
    """
    fullpath = os.path.normpath(os.path.join(working_dir, yamlfile))
    if not os.path.exists(fullpath):
        return {}

    try:
        with open(fullpath, "r", encoding='utf-8') as stream:
            config_dictionary = yaml.load(stream, Loader=yaml.SafeLoader)
            # Sometimes invalid yaml returns a string instead of a dictionary
            if not isinstance(config_dictionary, dict):
                raise yaml.scanner.ScannerError('Scanned to wrong class')
    except yaml.scanner.ScannerError:
        _LOGGER.warning("BuildConf.yaml is an invalid YAML file. Ignoring configuration.")
        config_dictionary = {}
    return config_dictionary

def load_config_from_file(yamlfile, working_dir):
    """
    Runs load_config on the input yamlfile.
    """

    config_dictionary = get_raw_config_data(yamlfile, working_dir)
    return load_config(config_dictionary)

def _log_warnings(warnings, breadcrumbs=None):
    """
    The validator returns a nested dictionary of issues. Note that the top level
    option is removed in load_config if the validation fails
    """
    if breadcrumbs is None:
        breadcrumbs = []
    for key in warnings:
        if isinstance(warnings[key], dict):
            new_breadcrumbs = breadcrumbs[:]
            new_breadcrumbs.append(key)
            _log_warnings(warnings[key], new_breadcrumbs)
        else:
            if len(breadcrumbs) == 0:
                keys = key
                remkey = key
            else:
                remkey = breadcrumbs[0]
                keys = ''
                for crumb in breadcrumbs:
                    keys += str(crumb)+'->'
                keys += key
            _LOGGER.warning('Problem parsing configuration - %s: %s  '
                            'All configuration in %s will not be used.',
                            keys,
                            warnings[key][0],
                            remkey)
