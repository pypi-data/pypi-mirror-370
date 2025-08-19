/* Define to be the name of C-function for Inf check */
#cmakedefine HAVE_FINITE 1
#cmakedefine HAVE_UNDERSCORE_FINITE 1

#undef COIN_C_FINITE
#ifndef COIN_C_FINITE 
	#ifdef HAVE_UNDERSCORE_FINITE 
		#define COIN_C_FINITE _finite
	#endif
#endif
#ifndef COIN_C_FINITE 
	#ifdef HAVE_FINITE 
		#define COIN_C_FINITE finite
	#endif
#endif
#ifndef COIN_C_FINITE
  #error "No finite/_finite function available"
#endif


/* Define to 1 if Pardiso is available */
/* #undef HAVE_PARDISO */

/* Define to 1 if you are not using at least a 4.0 version of Pardiso */
/* #undef HAVE_PARDISO_OLDINTERFACE */

/* Define to 1 if you are using the parallel version of Pardiso */
/* #undef HAVE_PARDISO_PARALLEL */

/* Define to 1 if the ASL package is available */
#undef COIN_HAS_ASL

/* If defined, the BLAS Library is available. */
#define COIN_HAS_BLAS 1

/* Define to 1 if the HSL package is available */
#undef COIN_HAS_HSL

/* If defined, the LAPACK Library is available. */
#define COIN_HAS_LAPACK 1

/* Define to 1 if the Mumps package is available */
#define COIN_HAS_MUMPS 1

/* Define to 1 if WSMP is available */
/* #undef HAVE_WSMP */

/* Define to the debug sanity check level (0 is no test) */
#define COIN_IPOPT_CHECKLEVEL 0

/* Define to the debug verbosity level (0 is no output) */
#define COIN_IPOPT_VERBOSITY 0

/* Define to 1 if the linear solver loader should be compiled to allow dynamic
   loading of shared libaries with linear solvers */
#undef HAVE_LINEARSOLVERLOADER 

/* Define to dummy `main' function (if any) required to link to the Fortran
   libraries. */
/* #undef F77_DUMMY_MAIN */

/* Define to a macro mangling the given C identifier (in lower and upper
   case), which must not contain underscores, for linking with Fortran. */
// SVT.SVT, 01.10.2018: Adapted according to MAiNGO build system
//#include "CFortranNameMangling/CFortranNameMangling.h"
#include "lapackNameMangling.h"
#define F77_FUNC(name,NAME) FCLAPACK_GLOBAL(name,NAME)

/* As F77_FUNC, but for C identifiers containing underscores. */
#define F77_FUNC_(name,NAME) FCLAPACK_GLOBAL_(name,NAME)_

/* Define if F77 and FC dummy `main' functions are identical. */
/* #undef FC_DUMMY_MAIN_EQ_F77 */

/* Define to the C type corresponding to Fortran INTEGER */
#define FORTRAN_INTEGER_TYPE int

/* Check for system headers and functions*/

/* Define to 1 if you have the <cassert> header file. */
#cmakedefine HAVE_CASSERT 1

/* Define to 1 if you have the <cctype> header file. */
#cmakedefine HAVE_CCTYPE 1

/* Define to 1 if you have the <cfloat> header file. */
#cmakedefine HAVE_CFLOAT 1

/* Define to 1 if you have the <cieeefp> header file. */
#cmakedefine HAVE_CIEEEFP 1

/* Define to 1 if you have the <cmath> header file. */
#cmakedefine HAVE_CMATH 1

/* Define to 1 if you have the <cstdarg> header file. */
#cmakedefine HAVE_CSTDARG 1

/* Define to 1 if you have the <cstddef> header file. */
#cmakedefine HAVE_CSTDDEF 1

/* Define to 1 if you have the <cstdio> header file. */
#cmakedefine HAVE_CSTDIO 1

/* Define to 1 if you have the <cstdlib> header file. */
#cmakedefine HAVE_CSTDLIB 1

/* Define to 1 if you have the <cstring> header file. */
#cmakedefine HAVE_CSTRING 1

/* Define to 1 if you have the <ctime> header file. */
#cmakedefine HAVE_CTIME 1

/* Define to 1 if you have the <ctype.h> header file. */
#cmakedefine HAVE_CTYPE_H 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#cmakedefine HAVE_DLFCN_H 1

/* Define to 1 if function drand48 is available */
#cmakedefine HAVE_DRAND48 1

/* Define to 1 if you have the <float.h> header file. */
#cmakedefine HAVE_FLOAT_H 1

/* Define to 1 if you have the <ieeefp.h> header file. */
#cmakedefine HAVE_IEEEFP_H 1

/* Define to 1 if you have the <inttypes.h> header file. */
#cmakedefine HAVE_INTTYPES_H 1

/* Define to 1 if you have the <math.h> header file. */
#cmakedefine HAVE_MATH_H 1

/* Define to 1 if you have the <memory.h> header file. */
#cmakedefine HAVE_MEMORY_H 1

/* Define to 1 if function rand is available */
#cmakedefine HAVE_RAND 1

/* Define to 1 if you have the `snprintf' function. */
#cmakedefine HAVE_SNPRINTF 1

/* Define to 1 if you have the <stdarg.h> header file. */
#cmakedefine  HAVE_STDARG_H 1

/* Define to 1 if you have the <stddef.h> header file. */
#cmakedefine HAVE_STDDEF_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#cmakedefine HAVE_STDINT_H 1

/* Define to 1 if you have the <stdio.h> header file. */
#cmakedefine HAVE_STDIO_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#cmakedefine HAVE_STDLIB_H 1

/* Define to 1 if function std::rand is available */
#cmakedefine HAVE_STD__RAND 1

/* Define to 1 if you have the <strings.h> header file. */
#cmakedefine HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#cmakedefine HAVE_STRING_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#cmakedefine HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#cmakedefine HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <time.h> header file. */
#cmakedefine HAVE_TIME_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#cmakedefine HAVE_UNISTD_H 1

/* Define to 1 if va_copy is avaliable */
#cmakedefine HAVE_VA_COPY 1

/* Define to 1 if you have the `vsnprintf' function. */
#cmakedefine HAVE_VSNPRINTF 1

/* Define to 1 if you have the <windows.h> header file. */
#cmakedefine HAVE_WINDOWS_H 1

/* Define to 1 if you have the `_snprintf' function. */
#cmakedefine  HAVE__SNPRINTF 1

/* Define to 1 if you have the `_vsnprintf' function. */
#cmakedefine HAVE__VSNPRINTF 1

/* SVN revision number of project */
/* #undef IPOPT_SVN_REV */

/* Version number of project */
#define IPOPT_VERSION "3.12.12"

/* Major Version number of project */
#define IPOPT_VERSION_MAJOR 3

/* Minor Version number of project */
#define IPOPT_VERSION_MINOR 12

/* Release Version number of project */
#define IPOPT_VERSION_RELEASE 12

/* Name of package */
#define PACKAGE "ipopt"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT "http://projects.coin-or.org/Ipopt/newticket"

/* Define to the full name of this package. */
#define PACKAGE_NAME "Ipopt"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "Ipopt 3.12.12"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "ipopt"

/* Define to the version of this package. */
#define PACKAGE_VERSION "3.12.12"

/* Set to extension for shared libraries in quotes. */
#ifdef HAVE_WINDOWS_H
	#define SHAREDLIBEXT "dll"
#else
	#define SHAREDLIBEXT "so"
#endif
	
/* The size of a `int *', as computed by sizeof. */
#define SIZEOF_INT_P 8

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Version number of package */
#define VERSION "3.12.12"

