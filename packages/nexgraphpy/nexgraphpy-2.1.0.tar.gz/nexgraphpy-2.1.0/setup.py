"""
NexgraphPy Setup Configuration
"""
from setuptools import setup
setup(
    name = 'nexgraphpy',
    packages = ['nexgraphpy'],
    version = '2.1.0',
    license = 'GNU General Public License',
    description = 'Python library to connect to Nextech DFS or DFT force gauges.',
    author = 'Shawn Myratchapon',
    url = 'https://python.nexgraphapp.com/',
    download_url = 'https://pypi.org/project/nexgraphpy/',
    install_requires=[
          'pyserial',
          'matplotlib',
          'numpy',
      ],
  classifiers=[  # Optional
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Tools',

    # Pick your license as you wish
    'License :: GNU :: General Public License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.12.3',
  ],
)
