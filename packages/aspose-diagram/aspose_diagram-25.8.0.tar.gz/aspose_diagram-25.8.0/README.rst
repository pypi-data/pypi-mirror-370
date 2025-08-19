Python Visio API
================

Aspose.Diagram for Python via Java is a scalable and feature-rich API to
process visio files using Python. API offers Visio file creation,
manipulation, conversion, & rendering. Developers can format pages to
the most granular level, create & manipulate shape, render pages, shapes
to PDF & images, and much more - all without any dependency on Microsoft
Office or Visio application.

Python Visio API Features
-------------------------

-  Create visio files via API.
-  Convert shapes to images or PDF.
-  Manage comments & hyperlinks.
-  Convert pages to PDF, XPS & SVG formats.
-  Inter-convert files to popular visio formats.

Read Visio Files
----------------

**Microsoft Visio:**\ VSD,VSS,VST,VSX,VTX, VDX, VSDX, VSTX, VSSX, VSTM,
VSSM

Save Visio Files As
-------------------

**Microsoft Visio:** VSX,VTX, VDX, VSDX, VSTX, VSSX, VSTM, VSSM **Fixed
Layout:** PDF, XPS **Images:** JPEG, PNG, BMP, SVG, TIFF, GIF, EMF
**Web:** HTML

Create Visio File from Scratch using Python
-------------------------------------------

.. code:: python

    import jpype
    import asposediagram
    jpype.startJVM()
    from asposediagram.api import *

    diagram = Diagram()
    diagram.save("output.vsdx", SaveFileFormat.VSDX)

    jpype.shutdownJVM()

Convert Visio VSDX File to PDF using Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import jpype
    import asposediagram
    jpype.startJVM()
    from asposediagram.api import *

    diagram = Diagram("input.vsdx")
    diagram.save("output.pdf",SaveFileFormat.PDF)

    jpype.shutdownJVM()

`Product Page <https://products.aspose.com/diagram/python-java>`__ \|
`Documentation <https://docs.aspose.com/display/diagrampythonjava/Home>`__
\| `Blog <https://blog.aspose.com/category/diagram/>`__ \| `API
Reference <https://apireference.aspose.com/diagram/python>`__ \| `Code
Samples <https://github.com/aspose-diagram/Aspose.Diagram-for-Java>`__
\| `Free Support <https://forum.aspose.com/c/diagram>`__ \| `Temporary
License <https://purchase.aspose.com/temporary-license>`__ \|
`EULA <https://company.aspose.com/legal/eula>`__
