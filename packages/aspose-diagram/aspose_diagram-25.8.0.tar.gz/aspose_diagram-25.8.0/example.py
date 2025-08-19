import jpype
from jpype import java
import asposediagram
jpype.startJVM()
from asposediagram.api import *

lic = License()
# lic.setLicense("Aspose.Diagram.lic")
# with open('Aspose.Diagram.lic', 'rb') as f:
#     lic.setLicense(f.read())

diagram = Diagram()
diagram.save("output-0.vsdx", SaveFileFormat.VSDX)

diagram = Diagram("example.vsdx")
diagram.save("output-1.vsdx", SaveFileFormat.VSDX)

with open("example.vsdx", "rb") as f:
    diagram = Diagram.createDiagramFromBytes(f.read())
    diagram.save("output-2.vsdx", SaveFileFormat.VSDX)

with open("example.vsdx", "rb") as f:
    diagram = Diagram.createDiagramFromBytes(f.read(), loadOptions=LoadFileFormat.VSDX)
    diagram.save("output-3.vsdx", SaveFileFormat.VSDX)

with open("example.vsdx", "rb") as f:
    loadOptions = LoadOptions(LoadFileFormat.VSDX)
    diagram = Diagram.createDiagramFromBytes(f.read(), loadOptions=loadOptions)
    diagram.save("output-4.vsdx", SaveFileFormat.VSDX)

diagram = Diagram("example.vsdx", LoadFileFormat.VSDX)
diagram.save("output-5.vsdx", SaveFileFormat.VSDX)

loadOptions = LoadOptions(LoadFileFormat.VSDX)
diagram = Diagram("example.vsdx", loadOptions)
diagram.save("output-6.vsdx", SaveFileFormat.VSDX)

diagram = Diagram("example.vsdx", LoadFileFormat.VSDX)
with open("output-stream-0.vsdx", "wb") as w:
    options = DiagramSaveOptions(SaveFileFormat.VSDX)
    options.setAutoFitPageToDrawingContent(True)
    content = diagram.saveToBytes(options)
    w.write(content)

diagram = Diagram("example.vsdx", LoadFileFormat.VSDX)
with open("output-stream-1.vsdx", "wb") as w:
    content = diagram.saveToBytes(SaveFileFormat.VSDX)
    w.write(content)

with open("example.vsdx", "rb") as f:
    result = FileFormatUtil.detectFileFormatFromBytes(f.read())
    print("detect result: %d" %(result.getFileFormatType()))

diagram = Diagram("example.vsdx")
page = diagram.getPages().getPage(0)
shape = page.getShapes().get(0)
options = ImageSaveOptions(SaveFileFormat.PNG)
with open("output-shape.png", "wb") as w:
    content = shape.toImageBytes(options)
    w.write(content)

shape = page.getShapes().get(1)
with open("output-shape.pdf", "wb") as w:
    content = shape.toPdfBytes()
    w.write(content)


jpype.shutdownJVM()