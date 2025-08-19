This is a wrapper for Artely Knitro.
It requires a separate Knitro installation and merely provides the CMakeLists.txt and FindKNITRO.cmake for including it in MAiNGO.
If Knitro is not found, a pre-processor flag will be set accordingly and MAiNGO will be compiled without Knitro.
