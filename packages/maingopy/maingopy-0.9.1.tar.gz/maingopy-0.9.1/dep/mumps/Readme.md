The folder MUMPS-5.4.0 contains MUMPS version 5.4.0 as obtained on April 20th, 2021, from http://mumps.enseeiht.fr/.
For license information, please refer to the files in the folder MUMPS-5.4.0.

The only additions compared to the original version are
  - the CMake files in the present folder,
  - the pre-compiled binaries for Visual Studio 2017, and
  - the blas and lapack libraries included as git submodules (in the dep folder).

Additionally, the fake MPI implementation provided by MUMPS to enable the use of MUMPS as a sequential program was changed, in that
  - all fake MPI calls start with the prefix FPI_ rather than MPI_, and
  - libseq/mpi.h was renamend to libseq/mumps_mpi.h.
