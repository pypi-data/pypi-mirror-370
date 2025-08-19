# sclogging

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) 
[![Documentation Status](https://readthedocs.org/projects/sclogging/badge/?version=latest)](https://sclogging.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/sclogging.svg)](https://badge.fury.io/py/sclogging)
[![Anaconda-Server Badge](https://anaconda.org/sshimek42/sclogging/badges/latest_release_date.svg)](https://anaconda.org/sshimek42/sclogging)
[![Anaconda-Server Badge](https://anaconda.org/sshimek42/sclogging/badges/version.svg)](https://anaconda.org/sshimek42/sclogging)


A Python module (with the help of coloredlogs) to add color to logs.

Still working on docs.

[Current docs](https://sclogging.readthedocs.io)

get_logger is where to get started.

Some options allow certain customizations in the records themselves (e.g. %f.red%something%f%) sets the FORE color for that word then returns to default color of that level of logging.


Other options:
Colored spacer

Easily setting seperate options for stderr and file logs

Custom timer class

  Allows this: 

                 var_a = Timer(level="INFO")
                 var_a.start_timer(Note="I started it")
               
  Log record:
    time spacer var_a.module.function.start_timer INFO I started it
  
  
Wraps logging, colorama.BACK, FORE, CURSOR
