# Species Distribution Database Migration

create table distribution (gid SERIAL PRIMARY KEY, taxon INT, numpolygon INT, id INT);
SELECT AddGeometryColumn('', 'distribution', 'geom', 4326, 'MultiPolygon', 2);

create index distribution_geom_index on distribution USING GIST (geom);

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
            x0 float8 DEFAULT 0, y0 float8 DEFAULT 0,
            OUT "seq" integer, OUT "row" integer, OUT col integer,
            OUT geom geometry)
        RETURNS SETOF record AS
    $$
    SELECT (i*ncol + j) + 1 as seq, i + 1 AS row, j + 1 AS col, ST_Translate(ST_Translate(cell, j * $3 + $5, i * $4 + $6),-180,-90) AS geom
    FROM generate_series(0, $1 - 1) AS i,
         generate_series(0, $2 - 1) AS j,
    (
    SELECT ST_SETSRID(('POLYGON((0 0, 0 '||$4||', '||$3||' '||$4||', '||$3||' 0,0 0))')::geometry, 4326) AS cell
    ) AS foo;
    $$ LANGUAGE sql IMMUTABLE STRICT;

DROP TABLE grid;
CREATE TABLE grid(seq INT, row INT, col INT );
grant all privileges on grid to web;

SELECT AddGeometryColumn('grid', 'geom', 4326, 'POLYGON', 2);
CREATE INDEX geom_index ON grid USING GIST (geom);
INSERT INTO grid (seq, row, col, geom) (select * from ST_CreateFishNet(360,720,.5,.5) as cells );


CREATE MATERIALIZED VIEW distribution_cells AS (select ST_MULTI(ST_COLLECTIONEXTRACT(ST_COLLECT(g.geom),3)) as geom, taxon from grid g JOIN distribution d ON  ST_INTERSECTS(g.geom, d.geom)  group by taxon );

or
create table distribution_cells (taxon INT, seq INT);



