## version 0.1.9
- moved interface to stream-fitter to NEF-Pipelines to avoid missing dependency errors
  in NEF-Piplines.

## version 0.1.8
- added tests of montecarlo error analyses
- added a mean 'fitter'
- fixed an off by 1 error
- made various parst of the package more robust
- added a symmetric exponential pair fitter [for Paul A. O’Brien's & Art Palmer's TROSY pulse
  sequence for simultaneous measurement of the 15N R1 and {1H}–15N NOE in deuterated proteins
  doi: 10.1007/s10858-018-0181-6]
- added a 3 parameter exponential fitter
- fitter protocol supports linear functions as well as non linear ones
- streamfitter can be loaded without loading JAX

## version 0.1.7
- streamfitter functions are now called funtions in their symbolic names

## version 0.1.6
- add default random number seed
- when fitting return estimates as well as fits
- support calculations without montecarlo cycles
- isolate 2 point fitter in a separate class
- pass fitter to use to fit
- fitting function is now called fit not fitter
- add tests of 2 parameter exponential decay
- streamfitter is now a proper package with an __init__
- add function to retrieve fitters by name
- better exception hierarchy

## version 0.1.5
- uppgrade to pynmrstar 3.3.4 to avoid installation problems

## version 0.1.4
- further changes to dependecies and build dependencies to avoid problems with installation

## version 0.1.3
- now uses pynmrstar 3.3.3 to avoid problems installing cnmrstar

## version 0.1.2
- add missing dependency on jaxlib

## version 0.1.1
- added checks that montecarlo errors added properly
- added return of statistics of stdev for each data point in the montecarlo error calculation

## version 0.1.0
- initial release
