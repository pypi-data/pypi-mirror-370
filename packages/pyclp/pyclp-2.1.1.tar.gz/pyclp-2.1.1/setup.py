# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyclp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyclp',
    'version': '2.1.1',
    'description': 'Python library to interface ECLiPSe Constraint Programmig System.',
    'long_description': 'Introduction\n############\n\n`PyCLP <https://github.com/pellico/pyclp>`_ \nis a Python library to interface ECLiPSe Constraint Programming System.\n\nThis module try to implement a pythonic interface to `ECLiPSe <http://www.eclipseclp.org/>`_ \n(alias easy to use) by compromising on a little bit on performance.\n\n\nDocumentation\n*************\n\n`PyCLP pythonhosted documentation <https://pyclp.readthedocs.io/en/latest/>`__\n\n\nMajor differences from ECLiPSe standard interface libraries\n***********************************************************\n\nThe main difference compared to embedded interface provided  by ECLiPSe system is \nthe persistence of constructed terms after calling the `pyclp.resume` (check \n`3.1.2  Building ECLiPSe terms <http://www.eclipseclp.org/doc/embedding/embroot008.html#toc11>`_ ) function.\nIn ECLiPSe standard interfaces compound terms are destroyed after resume while in PyCLP are\nstored in a reference that survives after resuming. PyCLP will destroy the reference only when python\ndestroys the linked python object (garbage collection). This consumes more memory but now\nthe python object and the related ECLiPSe object have the same *lifetime*.\n\nMoreover, in the definition of the API I tried to take advantage of a common property of python and \nECLiPSe: both are weak typed languages.\n\n\nNext steps\n**********\n\n   * Add support for multi-engine/multi-thread\n   * Extend functionality of set_option function\n\n\n  \n\n\n\n\n\n\n',
    'author': 'pellico',
    'author_email': 'pellico@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pellico/pyclp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
