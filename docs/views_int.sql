CREATE OR REPLACE VIEW v_taxon_distribution AS (
 SELECT a.taxon_distribution_id,
    a.cell_id,
    a.taxon_key,
    a.relative_abundance,
    g.geom
   FROM grid g
     JOIN taxon_distribution a ON g.id = a.cell_id
);

CREATE OR REPLACE VIEW v_world as
 SELECT w.cell_id,
    w.lon,
    w.lat,
    w.cell_row,
    w.cell_col,
    w.t_area,
    w.area,
    w.p_water,
    w.p_land,
    w.ele_min,
    w.ele_max,
    w.ele_avg,
    w.fao_area_id,
    w.lme_id,
    w.coastal_prop,
    w.shelf,
    w.slope,
    w.abyssal,
    w.estuary,
    w.mangrove,
    w.seamount_saup,
    w.seamount,
    w.coral,
    w.pprod,
    w.ice_con,
    w.sst,
    w.eez_count,
    w.sst_2001,
    w.bt_2001,
    w.pp_10Yr_avg,
    w.sst_avg,
    w.pp_annual,
    g.geom
   FROM grid g
     JOIN cell w ON w.cell_id = g.id;


grant all privileges on grid to sau_int;
grant all privileges on v_world to sau_int;
grant all privileges on v_taxon_distribution to sau_int;

grant all privileges on grid to postgres;
grant all privileges on v_world to postgres;
grant all privileges on v_taxon_distribution to postgres;
