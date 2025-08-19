from __future__ import absolute_import

import os
from jpype import *

__diagram_jar_dir__ = os.path.dirname(__file__)
addClassPath(os.path.join(__diagram_jar_dir__, "lib", "aspose-diagram-25.8.jar"))
addClassPath(os.path.join(__diagram_jar_dir__, "lib", "DiagramJavaClassBridge.jar"))

__all__ = ['api']