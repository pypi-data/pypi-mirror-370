# pkgs/sage-conf/_sage_conf/_conf.py.  Generated from _conf.py.in by configure.

VERSION = "10.6.5"

# The following must not be used during build to determine source or installation
# location of sagelib.  See comments in SAGE_ROOT/src/Makefile.in
# These variables come first so that other substituted variable values can refer
# to it.
SAGE_LOCAL = "/home/runner/work/passagemath/passagemath/local"
SAGE_ROOT = "/home/runner/work/passagemath/passagemath"

# The semicolon-separated list of GAP root paths. This is the list of
# locations that are searched for GAP packages. This is passed directly
# to GAP via the -l flag.
GAP_ROOT_PATHS = "${prefix}/lib/gap;${prefix}/share/gap".replace('${prefix}', SAGE_LOCAL)

# The path to the standalone maxima executable.
MAXIMA = "${prefix}/bin/maxima".replace('${prefix}', SAGE_LOCAL)

# Set this to the empty string if your ECL can load maxima without
# further prodding.
MAXIMA_FAS = "${prefix}/lib/ecl/maxima.fas".replace('${prefix}', SAGE_LOCAL)

# Delete this line if your ECL can load Kenzo without further prodding.
KENZO_FAS = "${prefix}/lib/ecl/kenzo.fas".replace('${prefix}', SAGE_LOCAL)

NTL_INCDIR = ""
NTL_LIBDIR = ""

# Path to the ecl-config script
ECL_CONFIG = "${prefix}/bin/ecl-config".replace('${prefix}', SAGE_LOCAL)

SAGE_NAUTY_BINS_PREFIX = ""

SAGE_ECMBIN = "ecm"

# Names or paths of the 4ti2 executables
FOURTITWO_HILBERT = ""
FOURTITWO_MARKOV = ""
FOURTITWO_GRAVER = ""
FOURTITWO_ZSOLVE = ""
FOURTITWO_QSOLVE = ""
FOURTITWO_RAYS = ""
FOURTITWO_PPI = ""
FOURTITWO_CIRCUITS = ""
FOURTITWO_GROEBNER = ""

# Colon-separated list of pkg-config modules to search for cblas functionality.
# We hard-code it here as cblas because configure (build/pkgs/openblas/spkg-configure.m4)
# always provides cblas.pc, if necessary by creating a facade pc file for a system BLAS.
CBLAS_PC_MODULES = "cblas"

# for sage_setup.setenv
SAGE_ARCHFLAGS = "unset"
SAGE_PKG_CONFIG_PATH = "$SAGE_LOCAL/lib/pkgconfig".replace('$SAGE_LOCAL', SAGE_LOCAL)

# Used in sage.repl.ipython_kernel.install
MATHJAX_DIR = "${prefix}/share/mathjax/mathjax".replace('${prefix}', SAGE_LOCAL)
THREEJS_DIR = SAGE_LOCAL + "/share/threejs-sage"

# OpenMP flags, if available.
OPENMP_CFLAGS = "-fopenmp"
OPENMP_CXXFLAGS = "-fopenmp"

# Installation location of wheels. This is determined at configuration time
# and does not depend on the installation location of sage-conf.
SAGE_SPKG_WHEELS = "${SAGE_LOCAL}/var/lib/sage/venv-python3.12".replace('${SAGE_LOCAL}', SAGE_LOCAL) + "/var/lib/sage/wheels"
