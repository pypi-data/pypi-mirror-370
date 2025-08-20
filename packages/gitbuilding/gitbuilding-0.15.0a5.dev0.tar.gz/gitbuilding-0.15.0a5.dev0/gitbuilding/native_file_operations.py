"""
This handles native file operations such as checking if files exists
on disk and writing to them. It is not much more than a simple wrapper
around some os.* functions.

The purpose of this module is to ensure that
all paths in other modules can be trated as posix paths. This is important
otherwise you need to track whether a is in posix style for web url use
or is in native style.
"""

import os
import sys
import pathlib
import shutil
import codecs
import re
import zipfile
from tempfile import gettempdir
from gitbuilding.buildup.utilities import as_posix
from gitbuilding.buildup.url import translate_external

GBPATH = os.path.dirname(__file__)
USERDIR = str(pathlib.Path.home())
TMPDIR = gettempdir()
if sys.platform == "win32":
    DATADIR = os.path.join(USERDIR, "AppData", "Roaming", "gitbuilding")
elif sys.platform == "linux":
    DATADIR = os.path.join(USERDIR, ".local", "share", "gitbuilding")
elif sys.platform == "darwin":
    DATADIR = os.path.join(USERDIR, "Library", "Application Support", "gitbuilding")
else:
    raise RuntimeError("Unknown Platform")

def localise(posix_path):
    """
    Covert the input posix path to the correct path for the local file system.
    """
    # Note on Windows os.path.normpath converts posix path seperators to windows ones
    # On Linux os.path.normpath (nor posixpath.normpath) converts from windows to posix
    return os.path.normpath(posix_path)

def as_native_path(posix_path, working_dir):
    """
    Returns the input posix style path as a os native path. Note that
    if you enter a Windows style path on Linux this will not change
    to posix.
    """

    if os.path.isabs(posix_path):
        return localise(posix_path)
    if working_dir is None:
        raise ValueError('The current directory must be specified for absolute paths')
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    joined = os.path.join(working_dir, localise(posix_path))
    return os.path.normpath(joined)

def exists_on_disk(posix_path, working_dir):
    """
    Return whether path exists on disk (can be file or dir)
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    return os.path.exists(fullpath)

def is_local_file(posix_path, working_dir):
    """
    Return whether local file exists and is a file
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    return os.path.isfile(fullpath)

def is_local_dir(posix_path, working_dir):
    """
    Return whether local directory exists and is a directory
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    return os.path.isdir(fullpath)

def directory_is_empty(posix_path, working_dir):
    """
    Return if directory is empty
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    return os.listdir(fullpath) == []

def make_local_dir(posix_path, working_dir, remove_existing=False):
    """
    Make a local directory from a relative path to a specified working directory.
    See also make_dir_if_needed, and make_local_dir_abs
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    if remove_existing:
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)
    os.mkdir(fullpath)

def make_local_dir_abs(posix_path, remove_existing=False):
    """
    Make a local directory from an localised path. See also make_dir_if_needed,
    and make_local_dir
    """

    if not os.path.isabs(posix_path):
        raise ValueError("Expecting an absolute path")
    fullpath = localise(posix_path)
    if remove_existing:
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)
    os.mkdir(fullpath)


def make_dir_if_needed(posix_path, working_dir, isfile=False):
    """Makes the directory if it doesn't exist."""
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Make dir if needed always expects a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    make_dir_if_needed_abs(fullpath, isfile=isfile)

def make_dir_if_needed_abs(abs_local_path, isfile=False):
    """Makes the directory if it doesn't exist. Accepts an absolute file path"""
    if isfile:
        directory = os.path.dirname(abs_local_path)
    else:
        directory = abs_local_path
    if not directory == "":
        if not os.path.exists(directory):
            os.makedirs(directory)

def write_local_file(posix_path, working_dir, contents):
    """
    Write a file to the local hard drive. Inputs are a posix path (that will be converted
    to a local path)
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Attempting to write to an absolute path. "
                         "This should not be possible")

    fullpath = os.path.join(working_dir, localise(posix_path))

    with codecs.open(fullpath, "w", encoding='utf-8') as file_obj:
        file_obj.write(contents)

def read_local_file(posix_path, working_dir):
    """
    Return the contents of a local file
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    with codecs.open(fullpath, mode="r", encoding="utf-8") as file_obj:
        content = file_obj.read()
    return content

def delete_local_file(posix_path, working_dir):
    """
    Delete a local file
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    os.remove(fullpath)

def delete_local_dir(posix_path, working_dir):
    """
    Delete a local directory
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(posix_path):
        raise ValueError("Expecting a relative path")
    fullpath = os.path.join(working_dir, localise(posix_path))
    shutil.rmtree(fullpath)

def copy_local_files(posix_path_in, posix_path_out, working_dir, force_relative=True):
    """
    Copy a local file to a new path
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if force_relative:
        if os.path.isabs(posix_path_in):
            raise ValueError("Expecting a relative path")
        if os.path.isabs(posix_path_out):
            raise ValueError("Expecting a relative path")
        fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        fullpath_out = os.path.join(working_dir, localise(posix_path_out))
    else:
        if os.path.isabs(posix_path_in):
            fullpath_in = localise(posix_path_in)
        else:
            fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        if os.path.isabs(posix_path_out):
            fullpath_out = localise(posix_path_out)
        else:
            fullpath_out = os.path.join(working_dir, localise(posix_path_out))
    shutil.copy(fullpath_in, fullpath_out)

def move_local_file(posix_path_in, posix_path_out, working_dir, force_relative=True):
    """
    Move a local file to a new path
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if force_relative:
        if os.path.isabs(posix_path_in):
            raise ValueError("Expecting a relative path")
        if os.path.isabs(posix_path_out):
            raise ValueError("Expecting a relative path")
        fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        fullpath_out = os.path.join(working_dir, localise(posix_path_out))
    else:
        if os.path.isabs(posix_path_in):
            fullpath_in = localise(posix_path_in)
        else:
            fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        if os.path.isabs(posix_path_out):
            fullpath_out = localise(posix_path_out)
        else:
            fullpath_out = os.path.join(working_dir, localise(posix_path_out))
    shutil.move(fullpath_in, fullpath_out)

def copy_local_directory(posix_path_in,
                         posix_path_out,
                         working_dir,
                         force_relative=True,
                         ignore_dirs=None,
                         ignore_files=None):
    """
    Copy a local directory into another directory. Optionally can ignore
    given directories
    """

    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if force_relative:
        if os.path.isabs(posix_path_in):
            raise ValueError("Expecting a relative path")
        if os.path.isabs(posix_path_out):
            raise ValueError("Expecting a relative path")
        fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        fullpath_out = os.path.join(working_dir, localise(posix_path_out))
    else:
        if os.path.isabs(posix_path_in):
            fullpath_in = localise(posix_path_in)
        else:
            fullpath_in = os.path.join(working_dir, localise(posix_path_in))
        if os.path.isabs(posix_path_out):
            fullpath_out = localise(posix_path_out)
        else:
            fullpath_out = os.path.join(working_dir, localise(posix_path_out))


    parent_of_input = os.path.split(fullpath_in)[0]
    if ignore_dirs is None:
        ignore_dirs = []
    if ignore_files is None:
        ignore_files = []

    for root, _, files in os.walk(fullpath_in):
        for filename in files:
            rel_root = os.path.relpath(root, fullpath_in)
            ignored = filename in ignore_files
            for dir_name in ignore_dirs:
                if dir_name in rel_root:
                    ignored = True

            if not ignored:
                filepath = os.path.join(root, filename)
                relative_filepath = os.path.relpath(filepath, parent_of_input)
                out_file = os.path.join(fullpath_out, relative_filepath)
                make_dir_if_needed_abs(out_file, isfile=True)
                shutil.copy(filepath, out_file)

def get_matches_from_dir(directory, working_dir, regex, relative=False):
    """
    Return all files within the given directory that match a rexex pattern
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    matches = []
    if os.path.isabs(directory):
        raise ValueError("Expecting a relative path")
    full_dir_path = os.path.join(working_dir, localise(directory))
    for root, _, files in os.walk(full_dir_path):
        for filename in files:
            match = re.match(regex, filename)
            if match is not None:
                filepath = os.path.join(root, filename)
                if relative:
                    filepath = os.path.relpath(filepath, working_dir)
                matches.append(as_posix(filepath))
    return matches

def list_dirs_and_files(directory, working_dir):
    """
    Returns the result of os.scandir as a list
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    if os.path.isabs(directory):
        raise ValueError("Expecting a relative path")
    full_dir_path = os.path.join(working_dir, localise(directory))
    return list(os.scandir(full_dir_path))

def is_valid_directory_name(path):
    """
    Check if directory name is a valid single directory
    """
    match = re.match(r"^[a-zA-Z0-9 _\-]+$", path)
    return match is not None

def create_zip(zipfilename, files_to_zip, working_dir, ext_dirs=None, zip_abs=False):
    """
    Create a zip archive in the local file system
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    local_files_to_zip = []
    for filename in files_to_zip:
        if os.path.isabs(filename):
            raise ValueError("Expecting a relative path")
        fullpath = os.path.join(working_dir, localise(filename))
        archive_path = translate_external(filename, ext_dirs)
        local_files_to_zip.append((fullpath, archive_path))

    if not zip_abs:
        if os.path.isabs(zipfilename):
            raise ValueError("Expecting a relative path")
        zipfilename = os.path.join(working_dir, localise(zipfilename))

    with zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED) as zipfile_obj:
        for fullpath, archive_path in local_files_to_zip:
            if os.path.isfile(fullpath):
                zipfile_obj.write(fullpath, archive_path)


def clean_documentation_dir(working_dir):
    """
    Removes the files built by gitbuilding
    """
    if not os.path.isabs(working_dir):
        raise ValueError('Working directory must be an absolute path')
    dirs_to_remove = ['_build', '_site', '_pdf']
    for directory in dirs_to_remove:
        if exists_on_disk(directory, working_dir):
            delete_local_dir(directory, working_dir)
