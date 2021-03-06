#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/09/09
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import os, sys, setuptools
from setuptools import setup, find_packages

# require python 2.7+
if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

heredir = os.path.abspath(os.path.dirname(__file__))
def read(*parts, **kw):
  try:    return open(os.path.join(heredir, *parts)).read()
  except: return kw.get('default', '')

test_dependencies = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.5.3',
  'WebTest              >= 1.4.0',
  'pdfkit               >= 0.4.1',
  'pxml                 >= 0.2.10',
]

dependencies = [
  'argparse             >= 1.2.1',
  'pyramid              >= 1.4.2',
  'pyramid-controllers  >= 0.3.24',
  'pyramid-iniherit     >= 0.1.9',
  'six                  >= 1.6.1',
  'docutils             >= 0.10',
  'PyYAML               >= 3.10',
  'numpydoc             >= 0.4',        # => Sphinx Jinja2
  'globre               >= 0.1.3',
  'aadict               >= 0.2.2',
  'asset                >= 0.6.9',
  'morph                >= 0.1.2',
]

extras_dependencies = {
  'pdf':  'pdfkit       >= 0.4.1',
}

entrypoints = {
  'console_scripts': [
    'pdescribe          = pyramid_describe.cli:main',
    'rst2rst.py         = pyramid_describe.writers.tools_rst2rst:main',
  ],
  'pyramid_describe.plugins.entry.parsers': [
    'docref             = pyramid_describe.syntax.docref:entry_parser',
    'title              = pyramid_describe.syntax.title:entry_parser',
    'numpydoc           = pyramid_describe.syntax.numpydoc:entry_parser',
    'docorator          = pyramid_describe.syntax.docorator:entry_parser',
  ],
  'pyramid_describe.plugins.type.parsers': [
  ],
  'pyramid_describe.plugins.catalog.parsers': [
    'numpydoc           = pyramid_describe.syntax.numpydoc:catalog_parser',
    'docorator          = pyramid_describe.syntax.docorator:catalog_parser',
  ],
  'pyramid_describe.plugins.entry.filters': [
    'access             = pyramid_describe.access:entry_filter',
  ],
  'pyramid_describe.plugins.type.filters': [
    'access             = pyramid_describe.access:type_filter',
  ],
  'pyramid_describe.plugins.catalog.filters': [
    'access             = pyramid_describe.access:catalog_filter',
  ],
}

classifiers = [
  'Development Status :: 4 - Beta',
  #'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Programming Language :: Python',
  'Operating System :: OS Independent',
  'Natural Language :: English',
  'License :: OSI Approved :: MIT License',
  'License :: Public Domain',
]

setup(
  name                  = 'pyramid_describe',
  version               = read('VERSION.txt', default='0.0.1').strip(),
  description           = 'A pyramid plugin that describes a pyramid application URL hierarchy via inspection.',
  long_description      = read('README.rst'),
  classifiers           = classifiers,
  author                = 'Philip J Grabner, Cadit Health Inc',
  author_email          = 'oss@cadit.com',
  url                   = 'http://github.com/cadithealth/pyramid_describe',
  keywords              = 'pyramid application url inspection reflection description describe',
  packages              = find_packages(),
  platforms             = ['any'],
  include_package_data  = True,
  zip_safe              = True,
  install_requires      = dependencies,
  extras_require        = extras_dependencies,
  tests_require         = test_dependencies,
  test_suite            = 'pyramid_describe',
  entry_points          = entrypoints,
  license               = 'MIT (http://opensource.org/licenses/MIT)',
)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
