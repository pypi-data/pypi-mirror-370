"""
This module contains the classes used to handle ExSource data in GitBuilding.
These classes can check if output files have been created and are up to date,
and can add important information to preview pages, such as the source files
of an exported object.
"""

import logging
import os
import json
import posixpath
import yaml
from jsonschema import ValidationError
from exsource_tools.exsource import ExSource, ExSourceExport, ExSourceFile
from exsource_tools.tools import ExSourceProcessor
from exsource_tools.enums import Status
from gitbuilding.buildup.url import translate_external

_LOGGER = logging.getLogger('BuildUp')

def check_exists(method):
    """
    Decorator function for methods of classes which have a boolean representation
    If the object is not initialised, or the data required is missing then the object's
    boolean representation should be false. Any method called with this decorator
    automatically returns None.
    """
    def wrapper(*args):
        #args[0] is self. Checks the object is truthy, i.e. initalised
        if args[0]:
            return method(*args)
        return None
    return wrapper

class GBExSource:
    """
    An exsource object for GitBuilding. Note this is NOT a subclass of ExSource from
    exsource-tools. The inputs to initialise are the GitBuilding list of files and the
    config for gitbuilding. Object contains ExSource objects for both the defintion file
    and output file if they both exist. These automatically translate filepaths based
    on external directories. This object also checks the status of each export defined
    in the exsource file
    """
    def __init__(self, config, all_files):
        self._config = config
        [exsource_def, exsource_out, exsource_dir] = self._load(all_files)
        self._exsource_def = exsource_def
        self._exsource_out = exsource_out
        self._exsource_dir = exsource_dir

        if self._exsource_def:
            cur_dir = os.getcwd()
            os.chdir(self._exsource_dir)
            processor = ExSourceProcessor(self._exsource_def, self._exsource_out)
            self.exsource_status = processor.check(echo=False)
            os.chdir(cur_dir)
        else:
            self.exsource_status = {}

    def __bool__(self):
        return self._exsource_def is not None

    def _load(self, all_files):
        if self._config.exsource_def is None:
            return (None, None, None)

        filepath_def = self._config.exsource_def
        exsource_def = self._read_exsource(filepath_def, all_files)

        # If the definition was not read, don't try to read exsource out
        if exsource_def is None:
            return (None, None, None)

        exsource_dir = posixpath.dirname(filepath_def)
        exsource_out = None
        if self._config.exsource_out is not None:
            filepath_out = self._config.exsource_out
            if posixpath.dirname(filepath_out) == exsource_dir:
                exsource_out = self._read_exsource(filepath_out, all_files)
            else:
                _LOGGER.warning("Cannot load ExSourceOut file. Should be in same "
                                "directory as ExSourceDef file.")

        return exsource_def, exsource_out, exsource_dir


    def _read_exsource(self, raw_filepath, all_files):
        if raw_filepath.startswith('..'):
            filepath = translate_external(raw_filepath, self._config.external_dirs)
        else:
            filepath = raw_filepath

        if filepath.lower().endswith('.yml') or filepath.lower().endswith('.yaml'):
            file_format = "YAML"
        elif filepath.lower().endswith('.json'):
            file_format = "JSON"
        else:
            _LOGGER.warning("Couldn't read '%s'. Only YAML and JSON exsource files "
                            "are supported.", filepath)
            return None

        if filepath in all_files:
            file_obj = all_files[all_files.index(filepath)]
            try:
                if file_format == "JSON":
                    input_data = json.loads(file_obj.content)
                else:
                    #only other option is YAML
                    input_data = yaml.safe_load(file_obj.content)
                return ExSource(input_data)
            except ValidationError:
                _LOGGER.warning("Cannot load ExSource file %s", raw_filepath)
        _LOGGER.warning("Specified exsource file now found %s", raw_filepath)
        return None

    @check_exists
    def relative_filename(self, output_file):
        """
        For a given in a FileInfo object return the path relative to the exource
        file directory
        """
        return posixpath.relpath(output_file.location_on_disk, self._exsource_dir)

    @check_exists
    def working_filename(self, filename):
        """
        For a given filename in the exsource file give the file name in the working
        directory.
        """
        return posixpath.normpath(posixpath.join(self._exsource_dir, filename))

    @check_exists
    def export_for(self, output_file):
        """
        Return the export object that defines the output file specified. None is
        returned if no export defines this file. The export object is a
        GBExSourceExoport, a subclass of ExSourceExport that corrects the filenames
        for GitBuilding working directory.
        """
        rel_filename = self.relative_filename(output_file)

        # First try to return the export from the exsource_out file
        if self._exsource_out:
            export_id = self._exsource_out.export_id_for(rel_filename)
            if export_id:
                export = self._exsource_out.exports[export_id]
                return GBExSourceExport(export.dump(), export_id, self)

        # If still here then not able to use exsource_out file, so use def file
        export_id = self._exsource_def.export_id_for(rel_filename)
        if export_id:
            export = self._exsource_def.exports[export_id]
            return GBExSourceExport(export.dump(), export_id, self)
        return None

class GBExSourceExport(ExSourceExport):
    """
    A subclass of ExSourceExport that corrects the filenames for GitBuilding
    working directory."
    """

    def __init__(self, data, dict_id, gb_exsource):
        self._gb_exsource = gb_exsource
        self._dict_id = dict_id
        super().__init__(data)

    def _working_filename(self, filename):
        return self._gb_exsource.working_filename(filename)

    def _working_filenames(self, filelist):
        output_list = []
        for file in filelist:
            data = file.dump()
            if isinstance(data, dict):
                data['filepath'] = self._working_filename(data['filepath'])
            else:
                data = self._working_filename(data)
            output_list.append(ExSourceFile(data))
        return output_list

    @property
    def output_files(self):
        """
        Return the output files, witht the filenames corrected for GitBuilding
        working directory.
        """
        return self._working_filenames(super().output_files)

    @property
    def source_files(self):
        """
        Return the source files, witht the filenames corrected for GitBuilding
        working directory.
        """
        return self._working_filenames(super().source_files)

    @property
    def dependencies(self):
        """
        Return the dependencies, witht the filenames corrected for GitBuilding
        working directory.
        """
        return self._working_filenames(super().dependencies)

    @property
    def name(self):
        """
        Return the name with an appropriate file-name based place holder if
        no name is specified
        """
        if super().name is not None:
            return super().name
        file_name =  posixpath.basename(super().output_files[0])
        return posixpath.splitext(file_name)[0]

    def as_markdown(self, preview_code=None):
        """
        Return a summary of the export in markdown. Any code to preview the file
        can be added as an optional input.
        """
        page_md = f"# {self.name}\n\n"
        if self.description is not None:
            page_md += f"{self.description}\n\n"
        page_md += preview_code
        page_md += "\n\n---\n\n"
        page_md += ('<details markdown="1">\n')
        page_md += ('<summary>Extra details</summary>\n')
        if self._gb_exsource.exsource_status[self._dict_id] != Status.UNCHANGED:
            _LOGGER.warning("The export displayed, or associacted information on preview "
                            "page for %s may be out of date.", self.name)
            page_md += ('<div markdown="1" class="caution-block">\n'
                        '**NOTE:** Details or dependencies may have changed since this file '
                        'was generated.\n</div>\n\n')
        page_md += self.sources_md()
        page_md += self.dependencies_md()
        page_md += ('</details>\n')
        return page_md

    def sources_md(self):
        """
        Return the source files as a list in markdown
        """
        sources = self.source_files
        if len(sources)==1:
            return f"**Source files:** [{sources[0]}]({sources[0]})\n\n"

        md = "**Source files:**\n\n"
        for source in sources:
            md += f"* [{source}]({source})\n"
        md += "\n"
        return md

    def dependencies_md(self):
        """
        Return the dependencies as a list in markdown
        """
        deps = self.dependencies
        if len(deps)==1:
            md = f"**Dependencies:** [{deps[0]}]({deps[0]})\n\n"
        else:
            md = "**Dependencies:**\n\n"
            for dep in deps:
                md += f"* [{dep}]({dep})\n"
            md += "\n"
        if not self.dependencies_exhaustive:
            md += "***Note:** This list of dependencies may not be complete.*"
        return md
