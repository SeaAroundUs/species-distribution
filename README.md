# species-distribution

Next generation of https://github.com/SeaAroundUs/SpeDisBuilder

## Build

The preferred build format is a Python wheel.
<pre>python setup.py bdist_wheel</pre>
will build something like
dist/species_distribution-2.0.0_dev1e7e8a4-py3-none-any.whl
The .whl file can then be distributed and installed anywhere via
<pre>pip install species_distribution-2.0.0_dev1e7e8a4-py3-none-any.whl</pre>
## Installation

from this directory, run

python setup.py install

The system depends on several database tables. These names will likely change
as we consolidate and move to AWS

Input tables:
- qryalltaxon
- taxon_habitat
- world
- grid

Output table:
- distribution

Database configuration can be made by creating a local_settings.py in the same format
as settings.py

Several tools are provided in bin/ to execute the distribution and process
the resulting dataset.  These will be installed in your path if you installed the
package:

### Usage

<pre>
from species_distribution import create_taxon_distribution

distribution = create_taxon_distribution(600323)

# distribution is a 2d numpy array.
# use it as is, or persist to an hdf5, database, or PNG preview:

from species_distribution import io
io.save_database(distribution)
io.save_hdf5(distribution)
io.save_png(distribution)

# Cells can be georeferenced with species_distribution.models.world.Grid

</pre>
### Tools
<pre>
usage: species-distribution [-h] [-f] [-t TAXON] [-l LIMIT] [-c THREADS] [-v]

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
  -c THREADS, --threads THREADS
                        use N threads
  -v, --verbose         be verbose

</pre>

### h5-to-database
<pre>
usage: h5-to-database [-h] [-t TAXON]

Species Distribution DB Load

optional arguments:
  -h, --help            show this help message and exit
  -t TAXON, --taxon TAXON
                        process this taxon only, can specify multiple -t
                        options
</pre>
