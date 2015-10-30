# species-distribution

github: https://github.com/SeaAroundUs/species-distribution

A Python module and command line tool which creates distribution datasets for taxa. The methods are described in docs/14-4.pdf and http://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/#_Toc421534359

## Installation

from this directory, run

python setup.py install

## Database

The system depends on several database tables, which are specified by the SQLAlchemy models in species_distribution/models

Input tables:
- taxon
- taxon_extent
- taxon_habitat
- cell
- grid

Output tables:
- taxon_distribution
- taxon_distribution_log

Database configuration can be made by creating a file species_distribution/.settings.json with this format:

    {
        "DB": {
            "username": "your_username_here",
            "port": "5432",
            "password": "your_password_here",
            "db": "database_name_here",
            "host": "database_hostname_here"
        },
        "NUMPY_WARNINGS": "warn",
        "PNG_DIR": "png",
        "DEBUG": false
    }

Several tools are provided in bin/ to execute the distribution and process
the resulting dataset.  These will be installed in your path if you installed the
package.

### Usage

<pre>
from species_distribution import create_taxon_distribution

distribution = create_taxon_distribution(600323)

# distribution is a 2d numpy array.
# use it as is, or persist to an hdf5, database, or PNG preview:

from species_distribution import sd_io
sd_io.save_database(distribution)
sd_io.save_png(distribution)

# Cells can be georeferenced with species_distribution.models.world.Grid

</pre>
## Tools

### bin/species-distribution

<pre>
usage: species-distribution [-h] [-f] [-t TAXON] [-l LIMIT] [-p PROCESSES] [-v]

Species Distribution

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           overwrite any existing output file: species-
                        distribution.hdf5
  -t TAXON, --taxon TAXON
                        process this taxon only, can specify multiple -t
                        options
  -l LIMIT, --limit LIMIT
                        process this many taxa only
  -p PROCESSES, --processes PROCESSES
                        use N processes in parallel, one per taxon

  -v, --verbose         be verbose

</pre>

With no arguments, this will create a distribution for every taxon with a record in the taxon_extent table. To create a distribution for a single taxon, use the -t option.  For example:

    $ bin/species-distribution -v -t 690690
    2015-10-30 11:27:58,647 species_distribution.main INFO  starting distribution
    2015-10-30 11:27:58,647 species_distribution.main INFO  connecting to Host: [..] DB: [..] User: [..]
    2015-10-30 11:28:00,095 species_distribution.main INFO  taxon 690690 exists in output, skipping it.  Use -f to force
    2015-10-30 11:28:00,095 species_distribution.main INFO  Found 0 taxa
    2015-10-30 11:28:00,095 species_distribution.main INFO  distribution complete

If a distribution data for a taxon exists, this will skip that taxon unless the -f option is specified.

## Build

The preferred build format is a Python wheel.
<pre>python setup.py bdist_wheel</pre>
will build something like
dist/species_distribution-2.0.0_dev1e7e8a4-py3-none-any.whl
The .whl file can then be distributed and installed anywhere via
<pre>pip install species_distribution-2.0.0_dev1e7e8a4-py3-none-any.whl</pre>

## Develop

<pre>python setup.py develop</pre>

## Test

<pre>
nosetests
</pre>
