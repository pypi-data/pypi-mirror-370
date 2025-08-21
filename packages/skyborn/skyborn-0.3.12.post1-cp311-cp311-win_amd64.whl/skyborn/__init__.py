# skyborn/__init__.py


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'skyborn.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

# Import calculation functions
from .calc import (
    linear_regression,
    convert_longitude_range,
    pearson_correlation,
    spearman_correlation,
    kendall_correlation,
    calculate_potential_temperature,
    # Mann-Kendall functions
    mann_kendall_test,
    mann_kendall_multidim,
    mann_kendall_xarray,
    trend_analysis,
    mk_test,
    mk_multidim,
    # New emergent constraint function names
    gaussian_pdf,
    emergent_constraint_posterior,
    emergent_constraint_prior,
    # Legacy names for backward compatibility
    calc_GAUSSIAN_PDF,
    calc_PDF_EC,
    find_std_from_PDF,
    calc_PDF_EC_PRIOR,
)

from .gradients import (
    calculate_gradient,
    calculate_meridional_gradient,
    calculate_zonal_gradient,
    calculate_vertical_gradient,
)

from .causality import liang_causality, granger_causality

# Import conversion functions for easy access
from .conversion import (
    convert_grib_to_nc,
    convert_grib_to_nc_simple,
    batch_convert_grib_to_nc,
    grib2nc,
    grib_to_netcdf,
    GribToNetCDFError,
)


# Import submodules
from . import plot
from . import interp
from . import ROF
from . import conversion
from . import calc
from . import spharm
from . import windspharm
from . import gridfill

# Import key gridfill functions for convenient access
from .gridfill import fill as gridfill_fill, fill_cube as gridfill_fill_cube

# Expose gridfill functions at top level with clear names
fill = gridfill_fill
fill_cube = gridfill_fill_cube


__version__ = "0.3.12.post1"
