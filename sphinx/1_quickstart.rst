Quickstart
##########

coronary artery reconstruction from OCT + angiography or simply angiography

Angiography data has been extracted via QAngio XA 3D RE, (Medis, Leiden, the Netherlands),
whilst OCT data has been extracted via QIvus (version 3.0, Medis Medical Imaging, Leiden, the Netherlands).

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

