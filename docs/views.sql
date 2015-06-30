CREATE OR REPLACE VIEW v_taxon_distribution AS (
 SELECT a.id,
    a.taxonkey,
    a.relativeabundance,
    g.seq,
    g.geom
   FROM grid g
     JOIN taxon_distribution a ON g.seq = a.cellid
);


CREATE OR REPLACE VIEW v_taxon_distribution_archive AS
 SELECT a.id,
    a.taxonkey,
    a.relativeabundance,
    g.seq,
    g.geom
   FROM grid g
     JOIN taxon_distribution_archive a ON g.seq = a.cellid;


CREATE OR REPLACE VIEW v_world as
 SELECT w."Seq",
    w."Lon",
    w."Lat",
    w."Row",
    w."Col",
    w."TArea",
    w."Area",
    w."PWater",
    w."PLand",
    w."EleMin",
    w."EleMax",
    w."EleAvg",
    w."Elevation_Min",
    w."Elevation_Max",
    w."Elevation_Mean",
    w."Bathy_Min",
    w."Bathy_Max",
    w."Bathy_Mean",
    w."FAO",
    w."LME",
    w."BGCP",
    w."Distance",
    w."CoastalProp",
    w."Shelf",
    w."Slope",
    w."Abyssal",
    w."Estuary",
    w."Mangrove",
    w."SeamountSAUP",
    w."Seamount",
    w."Coral",
    w."PProd",
    w."IceCon",
    w."SST",
    w."EEZcount",
    w."SST2001",
    w."BT2001",
    w."PP10YrAvg",
    w."SSTAvg",
    w."PPAnnual",
    g.geom
   FROM grid g
     JOIN world w ON w."Seq" = g.seq;




grant all privileges on grid to web;
grant all privileges on v_world to web;
grant all privileges on v_taxon_distribution to web;
grant all privileges on v_taxon_distribution_archive to web;



grant all privileges on grid to postgres;
grant all privileges on v_world to postgres;
grant all privileges on v_taxon_distribution to postgres;
grant all privileges on v_taxon_distribution_archive to postgres;
