# What is GitBuilding

GitBuilding is a program for documenting hardware designs. It's primary focus is on high-quality, up-to-date assembly instructions. GitBuilding gives you the freedom to write instructions in the form and structure that you want using markdown. It uses extra metadata to track component usage, and generate bills of materials. Independent, clear, and consistent documentation can be generated for variations of the same design without specifying the same information multiple times.

In GitBuilding you are able to:

* Write the instructions as you go along in markdown
* Tag links in the code with meta-data to show if they are steps in the build or parts that are needed
* Automatically generate bills of materials
* Create templates for instructions that render differently for different configurations of a design
* 3D preview of manufacturing files
* Define reusable libraries of components
* Export to HTML, Markdown, or PDF (experimental)


# How to install GitBuilding

To install (for Python 3.7+)

    pip install gitbuilding[gui]
    
If you don't want to use the stand-alone GUI, you can avoid installing PyQT with

    pip install gitbuilding[gui]
    
[More details are available on the website.](https://gitbuilding.io/install)

##  Running Gitbuilding

To run the stand-alone GitBuilding GUI run:

    gitbuilding-gui

or to view the same interface in a browser run

    gitbuilding webapp

then navigate to `localhost:6178` in your browser.

From this GUI you can open or create new projects. The GUI will launch a live editor in a browser for previewing and editing your documentation.


[More details are available on the website.](https://gitbuilding.io/usage/run)

### Asking for help

You are welcome to ask for help in the issue tracker. You can also talk to us on [our area of the GOSH forum](https://forum.openhardware.science/c/projects/gitbuilding/55) or on [Gitter](https://gitter.im/gitbuilding/community) (though we may not be too responsive due to Matrix notification issues!)

### Installing from source

If you wish to contribute to development of GitBuilding you can clone the project from GitLab. You will need to install the python package in development mode and build the javascript editor from source.

To do so please see the [contribution page](https://gitlab.com/gitbuilding/gitbuilding/-/blob/master/CONTRIBUTING.md) and the [developer installation instructions](https://gitlab.com/gitbuilding/gitbuilding/-/blob/master/DeveloperInstallation.md).

# Syntax for documentation

The syntax for documentation is in a format we call BuildUp. [More details are available on the website](https://gitbuilding.io/usage/buildup/).


# Funding

## NLnet

This project is funded through [NGI Zero Core](https://nlnet.nl/core), a fund established by [NLnet](https://nlnet.nl) with financial support from the European Commission's [Next Generation Internet](https://ngi.eu) program. Learn more at the [NLnet project page](https://nlnet.nl/project/HardwareManuals).

[<img src="https://nlnet.nl/logo/banner.png" alt="NLnet foundation logo" width="20%" />](https://nlnet.nl)
[<img src="https://nlnet.nl/image/logos/NGI0_tag.svg" alt="NGI Zero Logo" width="20%" />](https://nlnet.nl/core)

## Past funding

GitBuilding has previously received funding from:

* [Open Source Ecology Germany](https://www.ose-germany.de/)
* [LibreHub](https://librehub.github.io/)
* [OpenMake](https://www.openmake.de/)
