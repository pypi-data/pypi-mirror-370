# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['PyXMake']

package_data = \
{'': ['*']}

extras_require = \
{':python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-core>=1.27'],
 ':python_version >= "3.7" and python_version < "4.0"': ['pyx-webservice>=1.27'],
 'all:python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-poetry>=1.27',
                                                                                       'pyc-core>=1.11'],
 'all:python_version >= "3.8" and python_version < "4.0"': ['pyx-client>=1.27'],
 'client:python_version >= "3.8" and python_version < "4.0"': ['pyx-client>=1.27'],
 'confluence:python_version >= "3.7"': ['atlassian-python-api>=3.14'],
 'core:python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-poetry>=1.27',
                                                                                        'poetry-core>=1.0'],
 'devel:python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-poetry>=1.27',
                                                                                         'pyc-core>=1.11'],
 'generator:python_version >= "3.8"': ['meson>=1.8', 'ninja>=1.11'],
 'lint:python_version == "3.7"': ['black>=22.10,<23.0',
                                  'black>=22.10,<23.0',
                                  'pylint',
                                  'pylint'],
 'lint:python_version >= "3.7" and python_version < "4.0"': ['anybadge'],
 'lint:python_version >= "3.8"': ['pylint>=3.0', 'pylint>=3.0'],
 'lint:python_version >= "3.8" and python_version < "4.0"': ['black>=24.1',
                                                             'black>=24.1'],
 'poetry:python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-poetry>=1.27'],
 'setup:python_version == "2.7" or python_version >= "3.5" and python_version < "4.0"': ['pyx-poetry>=1.27',
                                                                                         'poetry-core>=1.0'],
 'setup:python_version >= "3.8"': ['meson>=1.8',
                                   'ninja>=1.11',
                                   'poetry-dynamic-versioning>=1.8'],
 'typer:python_version >= "3.7" and python_version < "4.0"': ['typer>=0.16']}

setup_kwargs = {
    'name': 'pyxmake',
    'version': '1.27.0',
    'description': 'Harmonized software interfaces and workflows to simplify complex build events',
    'long_description': '[![doi](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.13352143-red.svg)](https://zenodo.org/records/13352143)\n[![doc](https://img.shields.io/static/v1?label=Pages&message=User%20Guide&color=blue&style=flat&logo=gitlab)](https://dlr-sy.gitlab.io/pyxmake)\n[![PyPi](https://img.shields.io/pypi/v/pyxmake?label=PyPi)](https://pypi.org/project/pyxmake/)\n[![pipeline status](https://gitlab.com/dlr-sy/pyxmake/badges/master/pipeline.svg)]()\n\n# PyXMake\nPyXMake is a python-based, cross-platform build tool for compiling and distributing software projects and their documentation. The package provides harmonized software interfaces and predefined workflows to selected third-party developer tools with stricter default settings to simplify their handling. Experienced users can use a collection of distinct build classes to set up more elaborate builds jobs.\n## Usage\nThe package is structured into different build classes, whereby each class represents one distinct build event with some presets. These classes can be accessed directly to create a custom python-based build script.\n## Reference\nCurrently, the following SY-STM software projects are built and maintained by using PyXMake:\n* [PyXMake](https://gitlab.com/dlr-sy/pyxmake) (User Guide & Reference Guide)\n* [MCODAC](https://gitlab.com/dlr-sy/mcodac) (Reference Guide, Libraries)\n* [BEOS](https://gitlab.com/dlr-sy/beos) (Reference Guide, Libraries)\n* [Boxbeam](https://gitlab.com/dlr-sy/boxbeam) (Reference Guide, Libraries)\n* [Displam](https://gitlab.com/dlr-sy/displam) (Executable)\n## Example\nPlease refer to the linked [repository](https://gitlab.com/dlr-sy/pyxmake) for additional application examples.\n## Contact\n* [Marc Garbade](mailto:marc.garbade@dlr.de)\n## Support\n* [List of Contributors](https://gitlab.com/dlr-sy/pyxmake/-/blob/master/CONTRIBUTING.md)',
    'author': 'Garbade, Marc',
    'author_email': 'marc.garbade@dlr.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gitlab.com/dlr-sy/pyxmake',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}
from config.build import *
build(setup_kwargs)

setup(**setup_kwargs)
