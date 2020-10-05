Quickstart
##########

A library for coronary artery reconstruction from angriography, OCT + angiography,
(specifically for CFD usage) statistical shape modelling, CFD mesh generation and
surface unwrapping.

IVOCT + Angiography fusion method is based off the following work:

Athanasiou LS, Bourantas CV, Siogkas PK, et al. 3D reconstruction of coronary
arteries using frequency domain optical coherence tomography images and biplane
angiography. Proceedings: Engineering in Medicine and Biology Society (EMBC), 2012
Annual International Conference of the IEEE. San Diego (CA): IEEE, 2012. p.
2647–2650.

https://ieeexplore.ieee.org/abstract/document/6346508/

Angiography data has been extracted via QAngio XA 3D RE, (Medis, Leiden, the
Netherlands), whilst OCT data has been extracted via QIvus (version 3.0, Medis
Medical Imaging, Leiden, the Netherlands).

installation
------------

to unwrap the cylindrical meshes the python bindings found in `CGALUMethods <https://github.com/Chr1sC0de/CGALUnwrapper>`_ should be installed.
The methods can be imported via

.. code-block:: Python
   from pymethods import CGALMethods as CM

To generate meshes for CFD the `pointwise <https://www.pointwise.com/>`_ must be installed.

To install the necessary python requirements,

.. code-block:: PowerShell

    python -m pip install -r requirements.txt

to install the modules in release mode, in the to directory,

.. code-block:: PowerShell

    python -m pip install .

to install in symbolic mode

.. code-block:: PowerShell

    python -m pip install -e .


new users
---------

For new python users a document outlining setting up python with visual studio code is contained in ./Documentation