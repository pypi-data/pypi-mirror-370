''' The BuildUp module will eventually be split out of GitBuilding it doesn't
contain anything that it GitBuilding specific.

Importing this module imports the Documentation class, the URLRules class, the
ConfigSchema class, and the FileInfo class. It also imports the read_directory
function. This should be enough to access all core functionality of the module.
You many have to import other submodules if you want to  do more than simply
build documentation.
'''

from .core import Documentation
from .url import URLRules
from .config import ConfigSchema
from .files import FileInfo, read_directory, read_external_directories
