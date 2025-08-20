'''
A number of miscellaneous functions
'''

import os
import datetime
import logging
from gitbuilding.buildup.buildup import BuildUpParser
from gitbuilding.buildup.files import FileInfo, read_directory
from gitbuilding.config import load_config_from_file
from gitbuilding.native_file_operations import (GBPATH,
                                                is_local_file,
                                                is_local_dir,
                                                read_local_file,
                                                get_matches_from_dir)

_LOGGER = logging.getLogger('BuildUp.GitBuilding')
_LICENSE_DIR = GBPATH+"/licenses"

def get_project_title(working_dir):
    """
    Return the title for a GitBuilding project without fully building the project
    """
    working_dir = os.path.abspath(working_dir)
    if not is_local_dir('.', working_dir):
        raise FileNotFoundError("Cannot get title as working directory doesn't exist")
    config_file = 'buildconf.yaml'
    configuration = load_config_from_file(config_file, working_dir)
    if configuration.title is not None:
        return configuration.title
    if configuration.landing_page is None:
        landing_page_name = "index.md"
    else:
        landing_page_name = configuration.landing_page
    file_list = read_directory(working_dir, exclude_list=configuration.exclude)
    if landing_page_name in file_list:
        landing_page_content = read_local_file(landing_page_name, working_dir)
        return BuildUpParser(landing_page_content, landing_page_name).get_title()
    return "Untitled project"

def handle_licenses(configuration):
    """
    Modifies the configuration to auto include licenses by SPDX. If an extra file is needed then
    a FileInfo object is returned, else None is returned
    """

    if configuration.license_file is not None:
        #A licence file was explicitly specified in the configuration
        if configuration.license is None:
            _LOGGER.warning('License file set in configuration but no license name set.')
            configuration.license = 'Unknown license'
        configuration.force_output.append(configuration.license_file)
        return None
    #No licence file specified in configuration
    if configuration.license is None:
        #if no license or license_file is set just leave as is
        return None
    # Licence file is not specified by a license name is. Try to get the license text by
    # SPDX identifier:
    license_text = _get_license_text(configuration)
    if license_text is None:
        _LOGGER.warning('License %s set configuration. Could not match to licence text.',
                        configuration.license)
        return None
    configuration.license_file = 'license.md'
    if configuration.target_format != 'pdf':
        configuration.force_output.append('license.md')
    return FileInfo('license.md', dynamic_content=True, content=license_text)

def _get_license_text(configuration):

    # note all license files are in the format '<SPDX_IDN>.txt' where
    # <SPDX_IDN> is the SPDX license identifier

    licence_file =  configuration.license+".txt"
    if not is_local_file(licence_file, _LICENSE_DIR):
        return None

    license_text = read_local_file(licence_file, _LICENSE_DIR)

    this_year = str(datetime.datetime.now().year)
    authors = author_list(configuration, default="Copyright Holders")

    license_text = license_text.replace("[year]", this_year)
    license_text = license_text.replace("[fullname]", authors)
    license_text = f"# License\n```license\n{license_text}\n```"
    return license_text

def supported_licenses():
    """
    Return a dictionary with all licenses. The dictionary has two keys "Hardware licenses"
    and "Other licenses" each wich contain a list of the SPDX licenses.
    """
    license_files =  get_matches_from_dir('.', _LICENSE_DIR, r'.+\.txt', relative=True)
    licenses = [lic_file[:-4] for lic_file in license_files]
    hardware_prefixes = ("CERN-OHL-", "SHL-", "TAPR-OHL-")
    hardware = sorted([lic for lic in licenses if lic.startswith(hardware_prefixes)])
    other = sorted([lic for lic in licenses if not lic.startswith(hardware_prefixes)])
    return {"Hardware licenses": hardware, "Other licenses": other}

def author_list(configuration, default=None):
    """
    This function returns the list of authors as a string.
    """
    authors = configuration.authors
    if len(authors) == 0:
        return default
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return authors[0] + ' and ' + authors[1]
    #if more than two authors make a list
    text = ""
    for i, author in enumerate(authors):
        if i == 0:
            pass
        elif i == len(configuration.authors) - 1:
            text += ", and "
        else:
            text += ", "
        text += f"{author}"
    return text
