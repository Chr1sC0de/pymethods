# pymethods

 A library for coronary artery reconstruction from angriography, OCT + angiography, (specifically for CFD usage)
 statistical shape modelling, CFD mesh generation and surface unwrapping. Documentation [here](https://chr1sc0de.github.io/pymethods/)

 IVOCT + Angiography fusion method is based off the following work:

 Athanasiou LS, Bourantas CV, Siogkas PK, et al. 3D reconstruction of coronary arteries using frequency domain optical coherence tomography images and biplane angiography. Proceedings: Engineering in Medicine and Biology Society (EMBC), 2012 Annual International Conference of the IEEE. San Diego (CA): IEEE, 2012. p. 2647–2650.

 https://ieeexplore.ieee.org/abstract/document/6346508/

Angiography data has been extracted via QAngio XA 3D RE,
(Medis, Leiden, the Netherlands), whilst OCT data has been extracted via QIvus
(version 3.0, Medis Medical Imaging, Leiden, the Netherlands).

## Angiography Surface Generation
![alt](./images/Angiography.PNG)
## Angiography + OCT Surface Generation
![alt](./images/oct_and_angiography.PNG)
## Statistical Shape Modelling
![alt](./images/ssm.PNG)
## Surface Unwrapping
![alt](./images/unwrapping.PNG)
## Mesh Reparameterization to Structured Domains
![alt](./images/mesh_reparameterization.PNG)

# Installation

to unwrap the cylindrical meshes the python bindings found in
`CGALUMethods <https://github.com/Chr1sC0de/CGALUnwrapper>`_ should be
importable. A version which works with python 3.7 is included. At
the moment CGALMethods does not work with python 3.8 and above.

````
from pymethods import CGALMethods as CM
````

To generate meshes for CFD the `pointwise <https://www.pointwise.com/>`_
must be installed.

to install requirements
````
python -m pip install -r requirements.txt
````

to install the modules in release mode

````
python -m pip install .
````
to install in symbolic mode

````
python -m pip install -e .
````

# Examples

in depth examples are located in the ./testsJupyter folder, TBD
