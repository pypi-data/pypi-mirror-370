# %%
from pathlib import Path

from umep import (
    skyviewfactor_algorithm,
    wall_heightaspect_algorithm,
)
from umep.functions.SOLWEIGpython import solweig_runner_core

# working folder
working_folder = "tests/data/athens"
working_path = Path(working_folder).absolute()
working_path.mkdir(parents=True, exist_ok=True)
working_path_str = str(working_path)
# output folder
output_folder = "temp/athens"
output_folder_path = Path(output_folder).absolute()
output_folder_path.mkdir(parents=True, exist_ok=True)
output_folder_path_str = str(output_folder_path)
# extents
total_extents = [476800, 4205850, 477200, 4206250]

# %%
# wall info for SOLWEIG
if not Path(output_folder_path_str + "/walls/").exists():
    wall_heightaspect_algorithm.generate_wall_hts(
        dsm_path=working_path_str + "/DSM.tif",
        bbox=total_extents,
        out_dir=output_folder_path_str + "/walls",
    )

# %%
# skyview factor for SOLWEIG
if not Path(output_folder_path_str + "/svf/").exists():
    skyviewfactor_algorithm.generate_svf(
        dsm_path=working_path_str + "/DSM.tif",
        bbox=total_extents,
        out_dir=output_folder_path_str + "/svf",
        cdsm_path=working_path_str + "/CDSM.tif",
        trans_veg_perc=3,
    )

# %%

SRC = solweig_runner_core.SolweigRunCore(
    "tests/data/athens/configsolweig.ini",
    "tests/data/athens/parametersforsolweig.json",
)
SRC.run()
"""
"""
