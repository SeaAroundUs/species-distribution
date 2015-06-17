# Species Distribution Database Migration

The original data lived in Access and has been ported to PostgreSQL for this updated tool.  Here are the steps to migrate the required data.

## 
required DB files:

import 
Distribution_Polygons/

create table distribution (gid SERIAL PRIMARY KEY, taxon INT, numpolygon INT, id INT);
SELECT AddGeometryColumn('', 'distribution', 'geom', 4326, 'MultiPolygon', 2);

for x in *.shp ;   do echo $x ; shp2pgsql  -s 4326  -a $x distribution > `basename $x .shp`.sql ; done

create index geom_index USING GIST (geom);

insert:
# some geometries have inconsistent attributes: psql:601048.sql:4: ERROR:  column "taxonid" of relation "distribution" does not exist
LINE 1: INSERT INTO "distribution" ("id","taxonid","polyid","long","...

Create world DB with bin/create_tables.py

Insert world data:
mdb-export    -I postgres  World2.mdb  world | psql -f - specdis


used RazorSQL to export QRYALLTAXON view from TaxonTable_working.mdb.    Modified dump with:
- DOUBLE->FLOAT
- BOOLEAN(0) -> BOOLEAN
- VARCHAR(167...4234) -> TEXT

psql -f QRYALLTAXON.sql specdis

create index geom_index on distribution USING GIST  (geom);
create index gid_index on distribution(gid);
create index taxon_index on distribution(taxon);

CREATE GRID:

    CREATE OR REPLACE FUNCTION ST_CreateFishnet(
            nrow integer, ncol integer,
            xsize float8, ysize float8,
            OUT "seq" integer, OUT "row" integer, OUT col integer,
            OUT geom geometry)
        RETURNS SETOF record AS
    $$
    SELECT (i*ncol + j + 1)  as seq, i+1  AS row, j+1 AS col, ST_Translate(cell, -180 + j * $3, 90 - i * $4) AS geom
    FROM generate_series(0, $1-1 ) AS i,
         generate_series(0, $2-1 ) AS j,
    (
    SELECT ST_SETSRID(('POLYGON((0 0, 0 '||(-1*$4)||', '||$3||' '||(-1*$4)||', '||$3||' 0,0 0))')::geometry, 4326) AS cell
    ) AS foo;
    $$ LANGUAGE sql IMMUTABLE STRICT;

DROP TABLE grid;
CREATE TABLE grid(seq INT PRIMARY KEY, row INT, col INT );
grant all privileges on grid to web;
SELECT AddGeometryColumn('grid', 'geom', 4326, 'POLYGON', 2);
CREATE INDEX geom_index ON grid USING GIST (geom);
INSERT INTO grid (seq, row, col, geom) (select * from ST_CreateFishNet(360,720,.5,.5) as cells );


CREATE MATERIALIZED VIEW distribution_cells AS (select ST_MULTI(ST_COLLECTIONEXTRACT(ST_COLLECT(g.geom),3)) as geom, taxon from grid g JOIN distribution d ON  ST_INTERSECTS(g.geom, d.geom)  group by taxon );

delete from grid g where seq IN (select g.seq from grid g JOIN world w ON (g.seq = w."Seq") where "PWater" = 0);


CREATE TABLE taxon_distribution(id SERIAL PRIMARY KEY, taxonkey INT, cellid INT, relativeabundance FLOAT);
CREATE INDEX taxon_distribution_taxonkey_idx ON taxon_distribution(taxonkey);
ALTER TABLE taxon_distribution ADD CONSTRAINT taxonkey_cellid_key UNIQUE(taxonkey, cellid);

CREATE VIEW v_taxon_distribution AS (
 SELECT a.id,
    a.taxonkey,
    a.relativeabundance,
    g.seq,
    g.geom
   FROM grid g
     JOIN taxon_distribution a ON g.seq = a.cellid
);
