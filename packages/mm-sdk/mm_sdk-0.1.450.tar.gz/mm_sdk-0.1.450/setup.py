# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdk', 'sdk.mis', 'sdk.utils']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.3,<0.24.0', 'pydantic>=1.10,<2.0']

setup_kwargs = {
    'name': 'mm-sdk',
    'version': '0.1.450',
    'description': '',
    'long_description': 'None',
    'author': 'dyus',
    'author_email': 'dyuuus@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
