"""This module is for making an simple example GitBuilding project.

It is used when you run `gitbuilding new`"""


import yaml
from gitbuilding.native_file_operations import (directory_is_empty,
                                                is_valid_directory_name,
                                                exists_on_disk,
                                                write_local_file,
                                                make_local_dir)

def output_example_project(working_dir, interactive=True, title=None, config=None):
    """
    Outputs the new project to a folder.
    """
    if directory_is_empty(".", working_dir):
        newdir = "."
    else:
        if not interactive:
            return False
        ans = input("This directory is not empty. Build to new sub-dir? [y/N]: ")
        if ans in ("y", "Y"):
            newdir = input("Enter subdir name: ")
            if not is_valid_directory_name(newdir):
                print("\n\ngitbuilding new only supports creating a single subdirectory"
                      " to the current folder, not nested directories or full paths\n\n")
                return False
            if exists_on_disk(newdir, working_dir):
                print(f"\n\nCannot create directory '{newdir}', as it already exists\n\n")
                return False
            try:
                make_local_dir(newdir, working_dir)
            except (PermissionError, FileNotFoundError):
                print(f"\n\nFailed to create directory '{newdir}'"
                      "do you have the correct permissions?\n\n")
                return False
        else:
            if ans not in ("n", "N", ""):
                print("Invalid response.")
            return False
    # writing example project

    # IMAGE DIRECTORY
    make_local_dir(newdir+"/images", working_dir)

    # CONFIG FILE
    if config is None:
        config_yaml = example_config()
    else:
        config_yaml = yaml.dump(config)
    write_local_file(newdir+"/buildconf.yaml", working_dir, config_yaml)

    # OVERVIEW FILE
    write_local_file(newdir+"/index.md", working_dir, example_landing(title=title))

    # TESTPAGES
    for i, page in enumerate(["testpage1.md", "testpage2.md"]):
        write_local_file(newdir+"/"+page, working_dir, testpage(f"Test Page {i+1}"))

    write_local_file(newdir+"/widget.md", working_dir, example_part_page())

    # PARTS LIST
    write_local_file(newdir+"/Parts.yaml", working_dir, example_partlib())

    # README
    write_local_file(newdir+"/README.md", working_dir, example_readme())

    # PARTS LIST
    write_local_file(newdir+"/.gitignore", working_dir, example_gitignore())

    return True


def example_config():
    """This function returns and example config"""

    return """# Recommended information
Authors:
    - My Name

Affiliation: My Affiliation

#License: CERN-OHL-1.2

Email: my-email@my.domain


#Uncomment below to add custom categories
#CustomCategories:
#    printedtool:
#        Reuse: False
#        DisplayName: Printed tools

#Uncomment below to set a custom default category
#DefaultCategory: printedtool

#Uncomment below to set the title for the bill of material on a page
#PageBOMTitle: '##For this step you will need'

#Uncomment below to override the project title
#Title: 'My project'

#Uncomment below to set a custom Website root for static HTML builds
#WebsiteRoot: '/path/'

#Uncomment below to disable fussy warnings
#Fussy: False

#Uncomment below to disable search functionality in the output
#IncludeSearch: False

"""


def example_landing(title=None):
    """This function returns and example landing page"""
    if title is None:
        title = "Test Project"

    return f"# {title}" +"""

This is a great place to start making your documentation!

You should link to a couple of pages:

* [.](testpage1.md){step}
* [.](testpage2.md){step}

And you should definitely let people know about the [bill of materials]{BOM} page."""


def testpage(name):
    """This function returns and example instruction page"""

    return ("[M4x10 screws]:Parts.yaml#M4x10PanSteel\n"
            "[No. 2 Phillips screwdriver]:Parts.yaml#Screwdriver_Philips_No2\n"
            f"# {name}\n\n"
            "{{BOM}}\n\n"
            "## Put screws into the widget {pagestep}\n\n"
            "* Get a [No. 2 Phillips screwdriver]{Qty: 1, Cat: tool} ready\n"
            "* Take three [M4x10 screws]{Qty: 3} and screw them into the [widget](widget.md){Qty: 1}\n\n"
            "## Put more screws into the widget {pagestep}\n\n"
            "* Find the [screwdriver][No. 2 Phillips screwdriver]{Qty: 1, Cat: tool} again\n"
            "* Take two more [M4x10 screws]{Qty: 2} and screw them into the same widget\n\n")

def example_part_page():
    """
    Return and example page with part data:
    """
    return """
---
PartData:
    Specs:
        Type: Unknown
        Quality: Fantastic
    Suppliers:
        Widget Shop:
            PartNo: Widget1
            Link: https://dictionary.cambridge.org/dictionary/english/widget
---

# Widget

This is an example page for a part that needs more information than can be provided
in a part library. You can also add links and images into this page.
"""

def example_partlib():
    """This function returns and example part library"""

    return """
M4x10PanSteel:
    Name: M4x10 Pan Head Steel
    Description: >
        This is lots of text
        about some screws?
    Specs:
        Head: Pan
        Length: 10 mm
        Material: Stainless Steel
        Pitch: 0.7
    Suppliers:
        RS:
            PartNo: 528-817
            Link: https://uk.rs-online.com/web/p/machine-screws/0528817/
        McMasterCarr:
            PartNo: 90116A207
            Link: https://www.mcmaster.com/90116A207
Screwdriver_Philips_No2:
    Name: No. 2 Phillips screwdriver
    Description: >
        No2 Phillips screwdriver. This is the correct size
        form an M4 pan head screw
    Specs:
        Drive Size: No. 2
"""

def example_gitignore():
    """
    Returns the text for an example gitignore file for a BuildUp project
    """
    return """#This file was auto generated by GitBuilding

# Ignore the directory that GitBuilding will build markdown to
_build/
# Ignore the directory that GitBuilding will HTML markdown to
_site/
"""

def example_readme():
    """
    Returns an example README for a GitBuilding project
    """

    return """# This project is documented with GitBuilding

## What is GitBuilding

GitBuilding is an OpenSource project for documenting hardware projects with minimal
effort, so you can stop writing and GitBuilding. GitBuilding is a python program that
works on Windows, Linux, and MacOS. More information on the GitBuilding project, or how
to install GitBuilding please see the [GitBuilding website](http://gitbuilding.io)

## How do I edit the documentation?

To edit the documentation you do not need to install anything, the documentation files can
be opened in a plain text editor such as Windows Notepad, Notepad++, gedit, VS Code, etc.
We recommend installing GitBuilding to preview any changes to the documentation.
GitBuilding also comes with a browser-based editor that has a live display of the final HTML documentation.

If you have ever used [markdown](https://www.markdownguide.org/basic-syntax/) you will
notice that the files you are editing are markdown files. GitBuilding uses an extended
markdown syntax (that we call BuildUp). This allows you to keep track of parts in the
documentation. More detailed documentation is available on the
[GitBuilding website](https://gitbuilding.io)."""
