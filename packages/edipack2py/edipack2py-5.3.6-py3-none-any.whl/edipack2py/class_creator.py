from ctypes import *
import numpy as np
import os, sys
from pathlib import Path
import types
import pkgconfig

#################################
# AUXILIARY FUNCTIONS
#################################


# dummy class, to be filled
class Link:
    def __init__(self, library):
        self.library = library
        try:
            self.has_ineq = bool(c_int.in_dll(self.library, "has_ineq").value)
        except Exception:
            self.has_ineq = None
            print("Cannot init link class: invalid library")
        self.Nineq = None
        self.dim_hloc = 0
        self.Nsym = None
        # utils: colors and bold text
        self.PURPLE = "\033[95m"
        self.CYAN = "\033[96m"
        self.DARKCYAN = "\033[36m"
        self.BLUE = "\033[94m"
        self.GREEN = "\033[92m"
        self.YELLOW = "\033[93m"
        self.RED = "\033[91m"
        self.BOLD = "\033[1m"
        self.UNDERLINE = "\033[4m"
        self.COLOREND = "\033[0m"


# function that will add a variable to the dummy class, will be called
# in variable definition
def add_global_variable(obj, dynamic_name, target_object, target_attribute):
    @property
    def getter(self):
        try:
            attrib = getattr(target_object, target_attribute)
            try:  # this is for strings
                attrib = attrib.decode()
            except Exception:
                pass
        except Exception:  # this is for arrays
            if len(target_object) > 1:
                return [target_object[x] for x in range(len(target_object))]
        return attrib

    @getter.setter
    def setter(self, new_value):
        try:  # this is for arrays
            if len(target_object) > 1:
                if np.isscalar(new_value):
                    new_value = [new_value]
                minlength = min(len(target_object), len(new_value))
                target_object[0:minlength] = new_value[0:minlength]
        except Exception:
            try:
                new_value = new_value.encode()
            except Exception:
                pass
            setattr(target_object, target_attribute, new_value)

    # Dynamically add the property to the class
    setattr(obj.__class__, dynamic_name, getter)
    setattr(obj.__class__, dynamic_name, setter)


# get bath type
def get_bath_type(self):
    """

     This function returns an integer number related to the value of \
     :f:var:`bath_type` in the input file

      - :code:`1` for **normal** bath
      - :code:`2` for **hybrid** bath
      - :code:`3` for **replica** bath
      - :code:`4` for **general** bath

    :return: the integer index
    :rtype: int

    """

    get_bath_type_wrap = self.library.get_bath_type
    get_bath_type_wrap.argtypes = None
    get_bath_type_wrap.restype = c_int
    return get_bath_type_wrap()


# get ed mode
def get_ed_mode(self):
    """

    This function returns an integer number related to the value of \
    :f:var:`ed_mode` in the input file

     - :code:`1` for **normal** mode
     - :code:`2` for **superc** mode
     - :code:`3` for **nonsu2** mode

    :return: the integer index
    :rtype: int

    """

    get_ed_mode_wrap = self.library.get_ed_mode
    get_ed_mode_wrap.argtypes = None
    get_ed_mode_wrap.restype = c_int
    return get_ed_mode_wrap()


######################################
# Load shared library with C-bindings
######################################

custompath = []
default_pc_dir = ".pkgconfig.d"
system = sys.platform
libext = ".dylib" if system == "darwin" else ".so"
libname = "edipack_cbindings"
pathlist = []

# 1st try: use custom env variable
try:
    pathlist += os.environ["EDIPACK_PATH"].split(os.pathsep)
except Exception:
    pass

# 2nd try: use pkgconfig directly
if pkgconfig.exists("edipack"):
    pathlist += [pkgconfig.variables(libname)["libdir"]]

# 3rd try: check PKG_CONFIG_PATH
else:
    try:
        os.environ["PKG_CONFIG_PATH"] += os.pathsep + os.path.join(
            Path.home(), default_pc_dir
        )
    except Exception:
        os.environ["PKG_CONFIG_PATH"] = os.path.join(
            Path.home(), default_pc_dir
        )
    if pkgconfig.exists("edipack"):
        pathlist += [pkgconfig.variables(libname)["libdir"]]

# 4th try: look in standard environment variables
try:
    pathlist += os.environ["LD_LIBRARY_PATH"].split(os.pathsep)
except Exception:
    pass
try:
    pathlist += os.environ["DYLD_LIBRARY_PATH"].split(os.pathsep)
except Exception:
    pass

# try loading the library
dynamic_library = None
error_message = []

for ipath in pathlist:
    try:
        libfile = os.path.join(ipath, "lib" + libname + libext)
        dynamic_library = CDLL(libfile)
        break
    except Exception as e:
        error_message.append(str(e))
else:
    print("Library loading failed. List of error messages:")
    print(*error_message, sep="\n")


####################################################################
# Create the global_env class (this is what the python module sees)
####################################################################

global_env = Link(dynamic_library)

######################################
# GLOBAL VARIABLES
######################################

try:
    add_global_variable(
        global_env, "Nbath", c_int.in_dll(dynamic_library, "Nbath"), "value"
    )
    add_global_variable(
        global_env, "Norb", c_int.in_dll(dynamic_library, "Norb"), "value"
    )
    add_global_variable(
        global_env, "Nspin", c_int.in_dll(dynamic_library, "Nspin"), "value"
    )
    add_global_variable(
        global_env, "Nloop", c_int.in_dll(dynamic_library, "Nloop"), "value"
    )
    add_global_variable(
        global_env, "Nph", c_int.in_dll(dynamic_library, "Nph"), "value"
    )
    add_global_variable(
        global_env,
        "Nsuccess",
        c_int.in_dll(dynamic_library, "Nsuccess"),
        "value",
    )
    add_global_variable(
        global_env, "Lmats", c_int.in_dll(dynamic_library, "Lmats"), "value"
    )
    add_global_variable(
        global_env, "Lreal", c_int.in_dll(dynamic_library, "Lreal"), "value"
    )
    add_global_variable(
        global_env, "Ltau", c_int.in_dll(dynamic_library, "Ltau"), "value"
    )
    add_global_variable(
        global_env, "Lfit", c_int.in_dll(dynamic_library, "Lfit"), "value"
    )
    add_global_variable(
        global_env, "Lpos", c_int.in_dll(dynamic_library, "Lpos"), "value"
    )
    add_global_variable(
        global_env,
        "LOGfile",
        c_int.in_dll(dynamic_library, "LOGfile"),
        "value",
    )

    add_global_variable(
        global_env,
        "Uloc",
        ARRAY(c_double, 5).in_dll(dynamic_library, "Uloc"),
        "value",
    )
    add_global_variable(
        global_env, "Ust", c_double.in_dll(dynamic_library, "Ust"), "value"
    )
    add_global_variable(
        global_env, "Jh", c_double.in_dll(dynamic_library, "Jh"), "value"
    )
    add_global_variable(
        global_env, "Jx", c_double.in_dll(dynamic_library, "Jx"), "value"
    )
    add_global_variable(
        global_env, "Jp", c_double.in_dll(dynamic_library, "Jp"), "value"
    )
    add_global_variable(
        global_env, "xmu", c_double.in_dll(dynamic_library, "xmu"), "value"
    )
    add_global_variable(
        global_env, "beta", c_double.in_dll(dynamic_library, "beta"), "value"
    )
    add_global_variable(
        global_env,
        "dmft_error",
        c_double.in_dll(dynamic_library, "dmft_error"),
        "value",
    )
    add_global_variable(
        global_env, "eps", c_double.in_dll(dynamic_library, "eps"), "value"
    )
    add_global_variable(
        global_env, "wini", c_double.in_dll(dynamic_library, "wini"), "value"
    )
    add_global_variable(
        global_env, "wfin", c_double.in_dll(dynamic_library, "wfin"), "value"
    )
    add_global_variable(
        global_env, "xmin", c_double.in_dll(dynamic_library, "xmin"), "value"
    )
    add_global_variable(
        global_env, "xmax", c_double.in_dll(dynamic_library, "xmax"), "value"
    )
    add_global_variable(
        global_env,
        "sb_field",
        c_double.in_dll(dynamic_library, "sb_field"),
        "value",
    )
    add_global_variable(
        global_env, "nread", c_double.in_dll(dynamic_library, "nread"), "value"
    )

    add_global_variable(
        global_env,
        "ed_total_ud",
        c_bool.in_dll(dynamic_library, "ed_total_ud"),
        "value",
    )
    add_global_variable(
        global_env,
        "ed_twin",
        c_bool.in_dll(dynamic_library, "ed_twin"),
        "value",
    )
    add_global_variable(
        global_env,
        "chispin_flag",
        c_bool.in_dll(dynamic_library, "chispin_flag"),
        "value",
    )
    add_global_variable(
        global_env,
        "chidens_flag",
        c_bool.in_dll(dynamic_library, "chidens_flag"),
        "value",
    )
    add_global_variable(
        global_env,
        "chipair_flag",
        c_bool.in_dll(dynamic_library, "chipair_flag"),
        "value",
    )
    add_global_variable(
        global_env,
        "chiexct_flag",
        c_bool.in_dll(dynamic_library, "chiexct_flag"),
        "value",
    )
except Exception:
    print(
        "Could not setup global vars. Is EDIpack (or EDIpack2ineq) installed?"
    )


######################################
# GLOBAL FUNCTIONS
######################################

# from here
global_env.get_bath_type = types.MethodType(get_bath_type, global_env)
global_env.get_ed_mode = types.MethodType(get_ed_mode, global_env)

# parse umatrix (newer EDIpack)
try:
    from . import func_parse_umatrix

    global_env.reset_umatrix = types.MethodType(
        func_parse_umatrix.reset_umatrix, global_env
    )
    global_env.add_twobody_operator = types.MethodType(
        func_parse_umatrix.add_twobody_operator, global_env
    )
except Exception:
    pass

# read_input
from . import func_read_input

global_env.read_input = types.MethodType(
    func_read_input.read_input, global_env
)

# aux_funx
from . import func_aux_funx

global_env.set_hloc = types.MethodType(func_aux_funx.set_hloc, global_env)
global_env.search_variable = types.MethodType(
    func_aux_funx.search_variable, global_env
)
global_env.check_convergence = types.MethodType(
    func_aux_funx.check_convergence, global_env
)

# bath
from . import func_bath

global_env.get_bath_dimension = types.MethodType(
    func_bath.get_bath_dimension, global_env
)
global_env.set_hreplica = types.MethodType(func_bath.set_hreplica, global_env)
global_env.set_hgeneral = types.MethodType(func_bath.set_hgeneral, global_env)
global_env.break_symmetry_bath = types.MethodType(
    func_bath.break_symmetry_bath, global_env
)
global_env.spin_symmetrize_bath = types.MethodType(
    func_bath.spin_symmetrize_bath, global_env
)
global_env.orb_symmetrize_bath = types.MethodType(
    func_bath.orb_symmetrize_bath, global_env
)
global_env.orb_equality_bath = types.MethodType(
    func_bath.orb_equality_bath, global_env
)
global_env.ph_symmetrize_bath = types.MethodType(
    func_bath.ph_symmetrize_bath, global_env
)
global_env.save_array_as_bath = types.MethodType(
    func_bath.save_array_as_bath, global_env
)

global_env.bath_inspect = types.MethodType(func_bath.bath_inspect, global_env)


# main
from . import func_main

global_env.init_solver = types.MethodType(func_main.init_solver, global_env)
global_env.solve = types.MethodType(func_main.solve, global_env)
global_env.finalize_solver = types.MethodType(
    func_main.finalize_solver, global_env
)

# io
from . import func_io

global_env.build_sigma = types.MethodType(func_io.build_sigma, global_env)
global_env.build_gimp = types.MethodType(func_io.build_gimp, global_env)
global_env.get_sigma = types.MethodType(func_io.get_sigma, global_env)
global_env.get_gimp = types.MethodType(func_io.get_gimp, global_env)
global_env.get_g0and = types.MethodType(func_io.get_g0and, global_env)
global_env.get_delta = types.MethodType(func_io.get_delta, global_env)
global_env.get_dens = types.MethodType(func_io.get_dens, global_env)
global_env.get_mag = types.MethodType(func_io.get_mag, global_env)
global_env.get_docc = types.MethodType(func_io.get_docc, global_env)
global_env.get_phi = types.MethodType(func_io.get_phi, global_env)
global_env.get_eimp = types.MethodType(func_io.get_eimp, global_env)
global_env.get_chi = types.MethodType(func_io.get_chi, global_env)
global_env.get_impurity_rdm = types.MethodType(
    func_io.get_impurity_rdm, global_env
)

# bath_fit
from . import func_bath_fit

global_env.chi2_fitgf = types.MethodType(func_bath_fit.chi2_fitgf, global_env)
