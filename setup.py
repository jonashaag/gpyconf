from distutils.core import setup

setup(
    name        = 'gpyconf',
    version     = '0.2beta',
    description = 'a modular Python configuration framework with support for multiple frontends and backends',
    author      = 'Jonas Haag',
    author_email= 'jonas@lophus.org',
    url         = 'http://github.com/jonashaag/gpyconf',
    license     = '2-clause BSD | LGPL 2.1',
    packages    = ['gpyconf',
                   'gpyconf.frontends',
                        'gpyconf.frontends.gtk',
                   'gpyconf._internal',
                   'gpyconf.contrib',
                        'gpyconf.contrib.gtk',
                   'gpyconf.backends',
                        'gpyconf.backends._xml',
                   'gpyconf.fields'
                  ]
)

