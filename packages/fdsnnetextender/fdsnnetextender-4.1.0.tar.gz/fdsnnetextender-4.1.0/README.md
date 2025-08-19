[![pipeline status](https://gricad-gitlab.univ-grenoble-alpes.fr/OSUG/RESIF/fdsnextender/badges/master/pipeline.svg)](https://gricad-gitlab.univ-grenoble-alpes.fr/OSUG/RESIF/fdsnextender/commits/master)

[![coverage report](https://gricad-gitlab.univ-grenoble-alpes.fr/OSUG/RESIF/fdsnextender/badges/master/coverage.svg)](https://gricad-gitlab.univ-grenoble-alpes.fr/OSUG/RESIF/fdsnextender/commits/master)

# Generic tool to extend fdsn network code

FDSN (https://fdsn.org) creates seismic network codes.

Those can be in 2 forms : short or extended.

This module uses FDSN network API (http://www.fdsn.org/ws/networks/) to find the extended network code, given a short form and a date.

## Installation

``` shell
pip install fdsnnetextender
```

## Usage

``` python

from fdsnnetextender import FdsnNetExtender

extender = FdsnNetExtender()
ext_code = extender.extend('ZO', '2013-01-01')
```
Returns a string `ZO2008` for instance.

