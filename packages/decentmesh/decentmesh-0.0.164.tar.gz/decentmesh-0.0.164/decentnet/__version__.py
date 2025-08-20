"""
__version__.py
~~~~~~~~~~~~~~

Information about the current version of the py-package-template package.
"""

__title__ = "decentmesh"
__description__ = (
    "Simple connection over decentralized network"
)

__version__ = "0.0.164"
__author__ = "Jiri Otoupal"
__author_email__ = "jiri-otoupal@ips-database.eu"
__license__ = "JO-CAL"
__url__ = "https://github.com/jiri-otoupal/DecentNet-Py"
__pypi_repo__ = "https://pypi.org/project/decentmesh/"

___nv = __version__.split(".")
NETWORK_VERSION = bytes((int(___nv[0]), int(___nv[1]), int(___nv[2])))
