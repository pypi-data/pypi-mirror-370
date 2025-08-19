# EDIpack2py: A Python API for the EDIpack Quantum Impurity Solver
[![api docs](https://img.shields.io/static/v1?label=API&message=documentation&color=734f96&logo=read-the-docs&logoColor=white&style=flat-square)](https://edipack.github.io/EDIpack2py/)
[![PyPI](https://img.shields.io/pypi/v/edipack2py.svg)](https://pypi.org/project/edipack2py)
[![Anaconda-Server Badge](https://anaconda.org/edipack/edipack/badges/version.svg)](https://anaconda.org/edipack/edipack)

A Python module interfacing to [EDIpack](https://github.com/edipack/EDIpack), 
a  Lanczos based method for the solution of generic Quantum Impurity problems, 
exploiting distributed memory MPI parallelisation. This module offers all the 
features included in EDIpack, solving  *normal*, *superconducting* (s-wave) 
or *Spin-non-conserving* (e.g. with Spin-Orbit Coupling or in-plane magnetization) 
problems, including electron-phonons coupling.

### Install & Use

*EDIpack2py* is easily installable using pip. It automatically detects and loads the
EDIpack library using pkg-config. 

### Documentation
All the information about the installation, structure and operation of the module 
is available at [edipack.github.io/EDIpack2py/](https://edipack.github.io/EDIpack2py/)  

### Authors
[Lorenzo Crippa](https://github.com/lcrippa)  
[Adriano Amaricci](https://github.com/aamaricci)  


### Issues
If you encounter bugs or difficulties, please 
[file an issue](https://github.com/edipack/EDIpack2py/issues/new/choose). 
For any other communication, please reach out any of the developers.          
