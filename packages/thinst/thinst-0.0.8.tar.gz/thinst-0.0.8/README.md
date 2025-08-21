# thinst: Thin data spatiotemporally

## Description
Thin points spatiotemporally, spatially, or temporally (hence 'thinst', 'thin' + 'ST' for spatiotemporal).
<br>Spatial thinning will remove points so that no two points are within a given spatial threshold of each other. 
<br>Temporal thinning will remove points so that no two points are within a given temporal threshold of each other. 
<br>Spatiotemporal thinning will remove points so that no two points are within a given spatial threshold _and_ within a
given temporal threshold of each other. Accordingly, two points may overlap spatially, provided that they do not overlap
temporally, and vice versa.

Thinning is set up to retain the maximum number of points.

Thinning (whether it is spatiotemporal, spatial, or temporal) is conducted with the ```thinst``` function with the type
 of thinning determined by the input parameters.

Simple plots of points are also included within the ```plots``` module.

## Installation
```pip install thinst```

## Import
For general use, the line below will load the function ```thinst``` from the package of the same name.
```from thinst import thinst```

To access the underlying functions, use:
```from thinst.core import *```

To access the plotting functions, use:
```from thinst.plots import *```

## Documentation
For more information on the ```thinst``` function (or any other function) use one of the following:
<br>```?thinst```
<br>```help(thinst)```

## Example usage
An exemplar illustrating how to use ```thinst``` is available on GitHub at: 
https://github.com/JSBigelow/thinst/blob/main/exemplar.ipynb

## License
MIT
