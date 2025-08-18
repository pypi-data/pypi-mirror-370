# %%
from importlib import reload
from pathlib import Path

import geopandas as gpd
import pandas as pd

from umep import (
    common,
    shadow_generator_algorithm,
    skyviewfactor_algorithm,
    solweig_algorithm,
    wall_heightaspect_algorithm,
)

reload(solweig_algorithm)

#
bbox = [476070, 4203550, 477110, 4204330]
working_folder = "temp/tests/athens"
pixel_resolution = 1  # metres
working_crs = 2100

working_path = Path(working_folder).absolute()
working_path.mkdir(parents=True, exist_ok=True)
working_path_str = str(working_path)

# input files for computing
bldgs_path = "tests/data/athens/bldgs_clip.gpkg"
trees_path = "tests/data/athens/trees_clip.gpkg"
tree_canopies_path = "tests/data/athens/tree_canopies_clip.gpkg"

# %%
# create DSM if necessary
# the algorithm creates a new folder
# if this folder / file already exists then this step is skipped
# this saves unnecessary repetition
# if wanting to repeat, then delete (or rename) the folders / files
# same idea for remaining cells
if not Path.exists(working_path / "DSM.tif") or not Path.exists(working_path / "CDSM.tif"):
    # buildings
    bldgs_gdf = gpd.read_file(bldgs_path)
    bldgs_gdf = bldgs_gdf.to_crs(working_crs)
    # convert to raster by "burning" height column
    bldgs_rast, bldgs_transf = common.rasterise_gdf(
        bldgs_gdf,
        "geometry",
        "Height",
        bbox=bbox,
        pixel_size=pixel_resolution,
    )
    # save to geotiff
    common.save_raster(working_path_str + "/DSM.tif", bldgs_rast, bldgs_transf.to_gdal(), bldgs_gdf.crs.to_wkt())
    # GDF1 trees - load and buffer by diameter
    trees_gdf = gpd.read_file(trees_path)
    trees_gdf = trees_gdf.to_crs(working_crs)
    trees_gdf["geometry"] = trees_gdf["geometry"].buffer(trees_gdf["dia"])
    # GDF2 canopies - load and assign height column "ht" to match bldg ht column name
    tree_canopies_gdf = gpd.read_file(tree_canopies_path)
    tree_canopies_gdf = tree_canopies_gdf.to_crs(working_crs)
    tree_canopies_gdf["ht"] = 6  # set ht
    green_gdf = pd.concat(
        [
            trees_gdf[["ht", "geometry"]],  # GDF1
            tree_canopies_gdf[["ht", "geometry"]],  # GDF2
        ],
        ignore_index=True,
    )
    # create new GDF
    green_gdf = gpd.GeoDataFrame(green_gdf, geometry="geometry", crs=trees_gdf.crs)
    # rasterise by burning ht column
    veg_rast, veg_transf = common.rasterise_gdf(
        green_gdf,
        "geometry",
        "ht",
        bbox=bbox,
        pixel_size=pixel_resolution,
    )
    # flatten canopy raster where overlapping buildings
    veg_rast[bldgs_rast > 0] = 0
    # save
    common.save_raster(working_path_str + "/CDSM.tif", veg_rast, veg_transf.to_gdal(), trees_gdf.crs.to_wkt())

# %%
# wall info for SOLWEIG
if not Path.exists(working_path / "walls"):
    wall_heightaspect_algorithm.generate_wall_hts(
        dsm_path=working_path_str + "/DSM.tif",
        bbox=bbox,
        out_dir=working_path_str + "/walls",
    )

# %%
# shadows (not required for SOLWEIG)
for shadow_date_Ymd in ["2024-03-21"]:
    shadow_dir_name = f"shadow_{shadow_date_Ymd}"
    if not Path.exists(working_path / shadow_dir_name):
        shadow_generator_algorithm.generate_shadows(
            dsm_path=working_path_str + "/DSM.tif",
            # target date to caculate shadows for
            shadow_date_Ymd=shadow_date_Ymd,  # %Y-%m-%d"
            wall_ht_path=working_path_str + "/walls/wall_hts.tif",
            wall_aspect_path=working_path_str + "/walls/wall_aspects.tif",
            bbox=bbox,
            out_dir=working_path_str + "/" + shadow_dir_name,
            # if wanting a specific time then specify below
            # otherwise computed for intervals
            shadow_time_HM=None,  # "%H:%M"
            time_interval_M=60,  # interval in minutes - if not computing specific time
            veg_dsm_path=working_path_str + "/CDSM.tif",
        )

# %%
# skyview factor for SOLWEIG
if not Path.exists(working_path / "svf"):
    skyviewfactor_algorithm.generate_svf(
        dsm_path=working_path_str + "/DSM.tif",
        bbox=bbox,
        out_dir=working_path_str + "/svf",
        cdsm_path=working_path_str + "/CDSM.tif",
        trans_veg_perc=5,
    )

# %%
# POIs for sampling UTCI
pois_gdf = gpd.read_file("tests/data/athens/pois.gpkg")
# iter EPWs
for epw_path, solweig_dir_name, start_date_Ymd, end_date_Ymd in [
    (
        "tests/data/athens/athens_2050.epw",
        "solweig_2050_07",
        "2050-07-21",
        "2050-07-22",
    ),
]:
    if not Path.exists(working_path / solweig_dir_name):
        # run algorithm - requires paths to files calculated in previous steps
        solweig_algorithm.generate_solweig(
            dsm_path=working_path_str + "/DSM.tif",
            wall_ht_path=working_path_str + "/walls/wall_hts.tif",
            wall_aspect_path=working_path_str + "/walls/wall_aspects.tif",
            svf_path=working_path_str + "/svf/svfs.zip",
            # the EPW file
            epw_path=epw_path,
            # the bounding box
            bbox=bbox,
            # the output directory
            out_dir=working_path_str + "/" + solweig_dir_name,
            # start and end date for range to filter from EPW
            start_date_Ymd=start_date_Ymd,  # year must match EPW file!
            end_date_Ymd=end_date_Ymd,
            # hours to run
            hours=[7, 11, 15, 19],
            # canopy DSM
            veg_dsm_path=working_path_str + "/CDSM.tif",
            # optional POIs GDF
            pois_gdf=pois_gdf,
            trans_veg=5,
        )

# %%
