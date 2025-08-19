from __future__ import absolute_import

from enum import IntEnum
from array import array

from jpype import *
from jpype.types import *
from jpype import imports

from com.aspose.diagram.wrapper import StreamBuffer
@JImplementationFor("com.aspose.diagram.wrapper.StreamBuffer")
class _StreamBuffer(object):

    @JOverride(sticky=False)
    def write(self, chunk):
        if chunk == None:
            raise Exception("chunk is required")
        elif chunk.__class__.__name__ != 'bytes':
            raise TypeError("a bytes-like object is required")
        elif len(chunk) <= 0:
            raise ValueError("no content")
        self.writeStream(chunk, 0, len(chunk))

class ActiveXPersistenceType(IntEnum):
    PROPERTY_BAG = 0,
    STORAGE = 1,
    STREAM = 2,
    STREAM_INIT = 3,
class AlignmentValue(IntEnum):
    CENTER = 1,
    DECIMAL = 3,
    LEFT = 0,
    RIGHT = 2,
    UNDEFINED = -2147483648,
class AlignNameValue(IntEnum):
    ALIGN_TEXT_CENTER = 2,
    ALIGN_TEXT_LEFT = 1,
    ALIGN_TEXT_RIGHT = 3,
    UNDEFINED = -2147483648,
class ArrowSizeValue(IntEnum):
    COLOSSAL = 6,
    EXTRA_LARGE = 4,
    JUMBO = 5,
    LARGE = 3,
    MEDIUM = 2,
    SMALL = 1,
    UNDEFINED = -2147483648,
    VERY_SMALL = 0,
class BevelLightingTypeValue(IntEnum):
    BALANCED = 0,
    BRIGHT_ROOM = 1,
    CHILLY = 2,
    CONTRASTING = 3,
    FLAT = 4,
    FLOOD = 5,
    FREEZING = 6,
    GLOW = 7,
    HARSH = 8,
    LEGACY_FLAT_1 = 9,
    LEGACY_FLAT_2 = 10,
    LEGACY_FLAT_3 = 11,
    LEGACY_FLAT_4 = 12,
    LEGACY_HARSH_1 = 13,
    LEGACY_HARSH_2 = 14,
    LEGACY_HARSH_3 = 15,
    LEGACY_HARSH_4 = 16,
    LEGACY_NORMAL_1 = 17,
    LEGACY_NORMAL_2 = 18,
    LEGACY_NORMAL_3 = 19,
    LEGACY_NORMAL_4 = 20,
    MORNING = 21,
    SOFT = 22,
    SUNRISE = 23,
    SUNSET = 24,
    THREE_POINT = 25,
    TWO_POINT = 26,
    UNDEFINED = 27,
class BevelMaterialTypeValue(IntEnum):
    CLEAR = 0,
    DARK_EDGE = 1,
    FLAT = 2,
    LEGACY_MATTE = 3,
    LEGACY_METAL = 4,
    LEGACY_PLASTIC = 5,
    LEGACY_WIREFRAME = 6,
    MATTE = 7,
    METAL = 8,
    PLASTIC = 9,
    POWDER = 10,
    SOFT_EDGE = 11,
    SOFT_METAL = 12,
    TRANSLUCENT_POWDER = 13,
    UNDEFINED = 15,
    WARM_MATTE = 14,
class BevelPresetType(IntEnum):
    ANGLE = 1,
    ART_DECO = 2,
    CIRCLE = 3,
    CONVEX = 4,
    COOL_SLANT = 5,
    CROSS = 6,
    DIVOT = 7,
    HARD_EDGE = 8,
    NONE = 0,
    RELAXED_INSET = 9,
    RIBLET = 10,
    SLOPE = 11,
    SOFT_ROUND = 12,
class BevelTypeValue(IntEnum):
    ANGLE = 1,
    ART_DECO = 2,
    CIRCLE = 3,
    CONVEX = 4,
    COOL_SLANT = 5,
    CROSS = 6,
    DIVOT = 7,
    HARD_EDGE = 8,
    NONE = 0,
    RELAXED_INSET = 9,
    RIBLET = 10,
    SLOPE = 11,
    SOFT_ROUND = 12,
    UNDEFINED = -2147483648,
class BOOL(IntEnum):
    FALSE = 1,
    TRUE = 2,
    UNDEFINED = 0,
class BulletValue(IntEnum):
    NONE = 0,
    STYLE_1 = 1,
    STYLE_2 = 2,
    STYLE_3 = 3,
    STYLE_4 = 4,
    STYLE_5 = 5,
    STYLE_6 = 6,
    STYLE_7 = 7,
    UNDEFINED = -2147483648,
class CalendarValue(IntEnum):
    ARABIC_HIJIRI = 1,
    ENGLISH_TRANSLITERATED = 8,
    FRENCH_TRANSLITERATED = 9,
    HEBREW_LUNAR = 2,
    JAPANESE_EMPEROR_REIGN = 4,
    KOREAN_DANKI = 6,
    SAKA_ERA = 7,
    TAIWAN_CALENDAR = 3,
    THAI_BUDDHIST = 5,
    UNDEFINED = -2147483648,
    WESTERN = 0,
class CaseValue(IntEnum):
    ALL_CAPITAL_LETTERS = 1,
    INITIAL_CAPITAL_LETTERS_ONLY = 2,
    NORMAL_CASE = 0,
    UNDEFINED = -2147483648,
class CheckValueType(IntEnum):
    CHECKED = 1,
    MIXED = 2,
    UN_CHECKED = 0,
class CompositingQuality(IntEnum):
    ASSUME_LINEAR = 4,
    DEFAULT = 0,
    GAMMA_CORRECTED = 3,
    HIGH_QUALITY = 2,
    HIGH_SPEED = 1,
    INVALID = -1,
class CompoundTypeValue(IntEnum):
    SINGLE = 0,
    THICK_BETWEEN_THIN = 1,
    THICK_THIN = 3,
    THIN_THICK = 2,
    THIN_THIN = 4,
    UNDEFINED = -2147483648,
class CompressionType(IntEnum):
    GIF = 2,
    JPEG = 1,
    NO = 0,
    PNG = 4,
    TIFF = 3,
    UNDEFINED = -2147483648,
class ConFixedCodeValue(IntEnum):
    NEVER_REROUTE = 2,
    REROUTE_FREELY = 0,
    REROUTE_NEEDED = 1,
    REROUTE_ON_CROSSOVER = 3,
    RESERVED_1 = 4,
    RESERVED_2 = 5,
    RESERVED_3 = 6,
    UNDEFINED = -2147483648,
class ConLineJumpCodeValue(IntEnum):
    ALWAYS = 2,
    NEITHER_CONNECTOR_JUMPS = 4,
    NEVER = 1,
    OTHER_CONNECTOR_JUMPS = 3,
    PAGE_DEFAULT = 0,
    UNDEFINED = -2147483648,
class ConLineJumpDirXValue(IntEnum):
    DOWN = 2,
    PAGE_DEFAULT = 0,
    UNDEFINED = -2147483648,
    UP = 1,
class ConLineJumpDirYValue(IntEnum):
    LEFT = 1,
    PAGE_DEFAULT = 0,
    RIGHT = 2,
    UNDEFINED = -2147483648,
class ConLineJumpStyleValue(IntEnum):
    ARC = 1,
    GAP = 2,
    PAGE_DEFAULT = 0,
    SIDES_2 = 4,
    SIDES_3 = 5,
    SIDES_4 = 6,
    SIDES_5 = 7,
    SIDES_6 = 8,
    SIDES_7 = 9,
    SQUARE = 3,
    UNDEFINED = -2147483648,
class ConLineRouteExtValue(IntEnum):
    CURVED = 2,
    PAGE_DEFAULT = 0,
    STRAIGHT = 1,
    UNDEFINED = -2147483648,
class ConnectedShapesFlags(IntEnum):
    CONNECTED_SHAPES_ALL_NODES = 0,
    CONNECTED_SHAPES_INCOMING_NODES = 1,
    CONNECTED_SHAPES_OUTGOING_NODES = 2,
class ConnectionPointPlace(IntEnum):
    BOTTOM = 1,
    CENTER = 4,
    LEFT = 2,
    RIGHT = 3,
    TOP = 0,
class ConnectorsTypeValue(IntEnum):
    CURVED_LINES = 2,
    RIGHT_ANGLE = 0,
    STRAIGHT_LINES = 1,
    UNDEFINED = -2147483648,
class ContainerTypeValue(IntEnum):
    DOCUMENT = 0,
    MASTER = 2,
    PAGE = 1,
    STYLE = 3,
    UNDEFINED = -2147483648,
class ContextTypeValue(IntEnum):
    DATA_1 = 11,
    DATA_2 = 12,
    DATA_3 = 13,
    GEOMETRY_ANGLE = 4,
    GEOMETRY_HEIGHT = 6,
    GEOMETRY_WIDTH = 5,
    MASTER_NAME = 8,
    SHAPE_DATA_ITEM_CUSTOM_PROPERTY_LABEL = 2,
    SHAPE_ID = 7,
    SHAPE_LOCAL_NAME = 9,
    SHAPE_TEXT = 1,
    SHAPE_TYPE = 10,
    UNDEFINED = -2147483648,
    USER_CELL_LOCAL_ROW_NAME = 3,
class ControlBorderType(IntEnum):
    NONE = 0,
    SINGLE = 1,
class ControlCaptionAlignmentType(IntEnum):
    LEFT = 0,
    RIGHT = 1,
class ControlListStyle(IntEnum):
    OPTION = 1,
    PLAIN = 0,
class ControlMatchEntryType(IntEnum):
    COMPLETE = 1,
    FIRST_LETTER = 0,
    NONE = 2,
class ControlMousePointerType(IntEnum):
    APP_STARTING = 13,
    ARROW = 1,
    CROSS = 2,
    CUSTOM = 99,
    DEFAULT = 0,
    HELP = 14,
    HOUR_GLASS = 11,
    I_BEAM = 3,
    NO_DROP = 12,
    SIZE_ALL = 15,
    SIZE_NESW = 6,
    SIZE_NS = 7,
    SIZE_NWSE = 8,
    SIZE_WE = 9,
    UP_ARROW = 10,
class ControlPictureAlignmentType(IntEnum):
    BOTTOM_LEFT = 3,
    BOTTOM_RIGHT = 4,
    CENTER = 2,
    TOP_LEFT = 0,
    TOP_RIGHT = 1,
class ControlPicturePositionType(IntEnum):
    ABOVE_CENTER = 458753,
    ABOVE_LEFT = 393216,
    ABOVE_RIGHT = 524290,
    BELOW_CENTER = 65543,
    BELOW_LEFT = 6,
    BELOW_RIGHT = 131080,
    CENTER = 262148,
    LEFT_BOTTOM = 524294,
    LEFT_CENTER = 327683,
    LEFT_TOP = 131072,
    RIGHT_BOTTOM = 393224,
    RIGHT_CENTER = 196613,
    RIGHT_TOP = 2,
class ControlPictureSizeMode(IntEnum):
    CLIP = 0,
    STRETCH = 1,
    ZOOM = 3,
class ControlScrollBarType(IntEnum):
    BARS_BOTH = 3,
    BARS_VERTICAL = 2,
    HORIZONTAL = 1,
    NONE = 0,
class ControlScrollOrientation(IntEnum):
    AUTO = 3,
    HORIZONTAL = 1,
    VERTICAL = 0,
class ControlSpecialEffectType(IntEnum):
    BUMP = 6,
    ETCHED = 3,
    FLAT = 0,
    RAISED = 1,
    SUNKEN = 2,
class ControlType(IntEnum):
    CHECK_BOX = 2,
    COMBO_BOX = 1,
    COMMAND_BUTTON = 0,
    IMAGE = 8,
    LABEL = 7,
    LIST_BOX = 3,
    RADIO_BUTTON = 6,
    SCROLL_BAR = 10,
    SPIN_BUTTON = 5,
    TEXT_BOX = 4,
    TOGGLE_BUTTON = 9,
    UNKNOWN = 11,
class ConValue(IntEnum):
    OFFSET_FROM_CENTER = 3,
    OFFSET_FROM_CENTER_HIDDEN = 8,
    OFFSET_FROM_LEFT_EDGE = 2,
    OFFSET_FROM_LEFT_EDGE_HIDDEN = 7,
    OFFSET_FROM_RIGHT_EDGE = 4,
    OFFSET_FROM_RIGHT_EDGE_HIDDEN = 9,
    PROPORTIONAL = 0,
    PROPORTIONAL_HIDDEN = 5,
    PROPORTIONAL_LOCKED = 1,
    PROPORTIONAL_LOCKED_HIDDEN = 6,
    UNDEFINED = -2147483648,
class CountryCode(IntEnum):
    ALGERIA = 213,
    AUSTRALIA = 61,
    AUSTRIA = 43,
    BELGIUM = 32,
    BRAZIL = 55,
    CANADA = 2,
    CHINA = 86,
    CZECH = 420,
    DEFAULT = 0,
    DENMARK = 45,
    EGYPT = 20,
    FINLAND = 358,
    FRANCE = 33,
    GERMANY = 49,
    GREECE = 30,
    HUNGARY = 36,
    ICELAND = 354,
    INDIA = 91,
    IRAN = 981,
    IRAQ = 964,
    ISRAEL = 972,
    ITALY = 39,
    JAPAN = 81,
    JORDAN = 962,
    KUWAIT = 965,
    LATIN_AMERIC = 3,
    LEBANON = 961,
    LIBYA = 218,
    MEXICO = 52,
    MOROCCO = 216,
    NETHERLANDS = 31,
    NEW_ZEALAND = 64,
    NORWAY = 47,
    POLAND = 48,
    PORTUGAL = 351,
    QATAR = 974,
    RUSSIA = 7,
    SAUDI = 966,
    SOUTH_KOREA = 82,
    SPAIN = 34,
    SWEDEN = 46,
    SWITZERLAND = 41,
    SYRIA = 963,
    TAIWAN = 886,
    THAILAND = 66,
    TURKEY = 90,
    UNITED_ARAB_EMIRATES = 971,
    UNITED_KINGDOM = 44,
    USA = 1,
    VIET_NAM = 84,
class DataConnectionType(IntEnum):
    ODBC = 2,
    QLEDB = 1,
    SQL = 0,
    UNKNOWN = 3,
class DisplayModeSmartTagDefValue(IntEnum):
    ALL_TIME = 2,
    MOUSE_IS_PAUSED = 0,
    SHAPE_IS_SELECTED = 1,
    UNDEFINED = -2147483648,
class DisplayModeValue(IntEnum):
    DISPLAYS_SHAPE_BEHIND_MEMBER_SHAPES = 1,
    DISPLAYS_SHAPE_FRONT_MEMBER_SHAPES = 2,
    HIDES_SHAPE_TEXT = 0,
    UNDEFINED = -2147483648,
class DrawingResizeTypeValue(IntEnum):
    AUTOMATICALLY = 1,
    DEPENDS_ON_DRAWING_SIZE_TYPE = 0,
    NOT_AUTOMATICALLY = 2,
    UNDEFINED = -2147483648,
class DrawingScaleTypeValue(IntEnum):
    ARCHITECTURAL_SCALE = 1,
    CIVIL_ENGINEERING_SCALE = 2,
    CUSTOM_SCALE = 3,
    MECHANICAL_ENGINEERING_SCALE = 5,
    METRIC_SCALE = 4,
    NO_SCALE = 0,
    UNDEFINED = -2147483648,
class DrawingSizeTypeValue(IntEnum):
    ANSI_ARCHITECTURAL = 7,
    ANSI_ENGINEERING = 6,
    CUSTOM_PAGE_SIZE = 3,
    CUSTOM_SCALED_DRAW_SIZE = 4,
    FIT_PAGE_DRAW_CONTENTS = 1,
    METRIC_ISO = 5,
    SAME_AS_PRINTER = 0,
    STANDARD = 2,
    UNDEFINED = -2147483648,
class DropButtonStyle(IntEnum):
    ARROW = 1,
    ELLIPSIS = 2,
    PLAIN = 0,
    REDUCE = 3,
class DynFeedbackValue(IntEnum):
    REMAIN_STRAIGHT = 0,
    SHOW_FIVE_LEGS = 2,
    SHOW_THREE_LEGS = 1,
    UNDEFINED = -2147483648,
class EmfRenderSetting(IntEnum):
    EMF_ONLY = 0,
    EMF_PLUS_PREFER = 1,
class FileFormatType(IntEnum):
    BMP = 54,
    CSV = 10,
    DIF = 27,
    DOC = 28,
    DOCM = 33,
    DOCX = 26,
    DOTM = 35,
    DOTX = 34,
    EMF = 258,
    EXCEL_2003_XML = 20,
    EXCEL_97_TO_2003 = 19,
    GIF = 322,
    HTML = 17,
    JPG = 261,
    MAPI_MESSAGE = 30,
    MS_EQUATION = 31,
    ODS = 18,
    OLE_10_NATIVE = 32,
    OOXML = 41,
    PDF = 22,
    PNG = 262,
    POTM = 38,
    POTX = 37,
    PPSM = 40,
    PPSX = 39,
    PPT = 29,
    PPTM = 36,
    PPTX = 47,
    SLDX = 46,
    SVG = 25,
    TAB_DELIMITED = 16,
    TIFF = 24,
    UNKNOWN = 255,
    VDW = 6,
    VDX = 0,
    VSD = 1,
    VSDM = 42,
    VSDX = 7,
    VSS = 3,
    VSSM = 43,
    VSSX = 9,
    VST = 5,
    VSTM = 44,
    VSTX = 8,
    VSX = 2,
    VTX = 4,
    WMF = 259,
    XLAM = 15,
    XLSB = 21,
    XLSM = 12,
    XLSX = 11,
    XLTM = 14,
    XLTX = 13,
    XML = 45,
    XPS = 23,
class FillType(IntEnum):
    AUTOMATIC = 0,
    GRADIENT = 3,
    NONE = 1,
    PATTERN = 5,
    SOLID = 2,
    TEXTURE = 4,
class FontSourceType(IntEnum):
    FONT_FILE = 0,
    FONTS_FOLDER = 1,
    MEMORY_FONT = 2,
class ForeignType(IntEnum):
    BITMAP = 32,
    ENH_METAFILE = 8,
    INK = 64,
    METAFILE = 16,
    OBJECT = 4,
    UNDEFINED = -2147483648,
class FromPartValue(IntEnum):
    BEGIN_X_CELL = 7,
    BEGIN_X_OR_BEGIN_Y_POINT = 9,
    BEGIN_Y_CELL = 8,
    BOTTOM_EDGE = 4,
    CENTER_EDGE = 2,
    CONTROL_POINT = 100,
    END_X_CELL = 10,
    END_X_OR_END_Y_POINT = 12,
    END_Y_CELL = 11,
    LEFT_EDGE = 1,
    MIDDLE_EDGE = 5,
    NONE = 0,
    RIGHT_EDGE = 3,
    TOP_EDGE = 6,
    UNDEFINED = -2147483648,
class GluedShapesFlags(IntEnum):
    GLUED_SHAPES_ALL_1_D = 0,
    GLUED_SHAPES_ALL_2_D = 3,
    GLUED_SHAPES_INCOMING_1_D = 1,
    GLUED_SHAPES_INCOMING_2_D = 4,
    GLUED_SHAPES_OUTGOING_1_D = 2,
    GLUED_SHAPES_OUTGOING_2_D = 5,
class GlueSettings(IntEnum):
    CONNECTION_POINTS = 8,
    DISABLED = 32768,
    GEOMETRY = 32,
    GUIDES = 1,
    HANDLES = 2,
    NONE = 0,
    UNDEFINED = -2147483648,
    VERTICES = 4,
class GlueSettingsValue(IntEnum):
    GLUE_IS_DISABLED = 32768,
    GLUE_IS_ENABLED = 0,
    GLUE_TO_CONNECTION_POINTS = 8,
    GLUE_TO_GEOMETRY = 32,
    GLUE_TO_GUIDES = 1,
    GLUE_TO_HANDLES = 2,
    GLUE_TO_VERTICES = 4,
    UNDEFINED = -2147483648,
class GlueTypeValue(IntEnum):
    ALLOW_DYNAMIC_GLUE = 2,
    ALLOW_DYNAMIC_GLUE_2002 = 1,
    ALLOW_DYNAMIC_GLUE_FOR_DYNAMIC_CONNECTOR = 0,
    NO_ALLOW_2_D_SHAPE = 8,
    NO_ALLOW_DYNAMIC_GLUE = 4,
    UNDEFINED = -2147483648,
class GradientDirectionType(IntEnum):
    FROM_CENTER = 4,
    FROM_LOWER_LEFT_CORNER = 2,
    FROM_LOWER_RIGHT_CORNER = 3,
    FROM_UPPER_LEFT_CORNER = 0,
    FROM_UPPER_RIGHT_CORNER = 1,
    UNKNOWN = 5,
class GradientFillDir(IntEnum):
    LINEAR = 0,
    PATH = 13,
    RADIAL_FROM_BOTTOM_LEFT = 2,
    RADIAL_FROM_BOTTOM_RIGHT = 1,
    RADIAL_FROM_CENTER = 3,
    RADIAL_FROM_CENTER_BOTTOM = 4,
    RADIAL_FROM_CENTER_TOP = 5,
    RADIAL_FROM_TOP_LEFT = 7,
    RADIAL_FROM_TOP_RIGHT = 6,
    RECTANGLE_FROM_BOTTOM_LEFT = 9,
    RECTANGLE_FROM_BOTTOM_RIGHT = 8,
    RECTANGLE_FROM_CENTER = 10,
    RECTANGLE_FROM_TOP_LEFT = 12,
    RECTANGLE_FROM_TOP_RIGHT = 11,
class GradientFillType(IntEnum):
    LINEAR = 0,
    PATH = 3,
    RADIAL = 1,
    RECTANGLE = 2,
class GradientStyleType(IntEnum):
    DIAGONAL_DOWN = 0,
    DIAGONAL_UP = 1,
    FROM_CENTER = 2,
    FROM_CORNER = 3,
    HORIZONTAL = 4,
    UNKNOWN = 6,
    VERTICAL = 5,
class GridDensityValue(IntEnum):
    COARSE = 2,
    FINE = 8,
    FIXED = 0,
    NORMAL = 4,
    UNDEFINED = -2147483648,
class HorzAlignValue(IntEnum):
    CENTER = 1,
    FORCE_JUSTIFY = 4,
    JUSTIFY = 3,
    LEFT_ALIGN = 0,
    RIGHT_ALIGN = 2,
    UNDEFINED = -2147483648,
class IconSizeValue(IntEnum):
    DOUBLE = 4,
    NORMAL = 1,
    TALL = 2,
    UNDEFINED = -2147483648,
    WIDE = 3,
class ImageColorMode(IntEnum):
    BLACK_AND_WHITE = 2,
    GRAYSCALE = 1,
    NONE = 0,
class InputMethodEditorMode(IntEnum):
    ALPHA = 8,
    ALPHA_FULL = 7,
    DISABLE = 3,
    HANGUL = 10,
    HANGUL_FULL = 9,
    HANZI = 12,
    HANZI_FULL = 11,
    HIRAGANA = 4,
    KATAKANA = 5,
    KATAKANA_HALF = 6,
    NO_CONTROL = 0,
    OFF = 2,
    ON = 1,
class InterpolationMode(IntEnum):
    BICUBIC = 4,
    BILINEAR = 3,
    DEFAULT = 0,
    HIGH = 2,
    HIGH_QUALITY_BICUBIC = 7,
    HIGH_QUALITY_BILINEAR = 6,
    INVALID = -1,
    LOW = 1,
    NEAREST_NEIGHBOR = 5,
class LayoutDirection(IntEnum):
    BOTTOM_TO_TOP = 1,
    DOWN_THEN_LEFT = 7,
    DOWN_THEN_RIGHT = 4,
    LEFT_THEN_DOWN = 6,
    LEFT_TO_RIGHT = 2,
    RIGHT_THEN_DOWN = 5,
    RIGHT_TO_LEFT = 3,
    TOP_TO_BOTTOM = 0,
class LayoutStyle(IntEnum):
    CIRCULAR = 3,
    COMPACT_TREE = 1,
    FLOW_CHART = 0,
    RADIAL = 2,
class LightRigDirectionType(IntEnum):
    BOTTOM = 0,
    BOTTOM_LEFT = 1,
    BOTTOM_RIGHT = 2,
    LEFT = 3,
    RIGHT = 4,
    TOP = 5,
    TOP_LEFT = 6,
    TOP_RIGHT = 7,
class LineAdjustFromValue(IntEnum):
    ALL_LINES = 1,
    NO_LINES = 2,
    ROUTING_STYLE_DEFAULT = 3,
    UNDEFINED = -2147483648,
    UNRELATED_LINES = 0,
class LineAdjustToValue(IntEnum):
    ALL_LINES_CLOSE = 1,
    NO_LINES = 2,
    RELATEDLINES = 3,
    ROUTING_STYLE_DEFAULT = 0,
    UNDEFINED = -2147483648,
class LineJumpCodeValue(IntEnum):
    FIRST_DISPLAYED_LINE = 5,
    HORIZONTAL_LINES = 1,
    LAST_DISPLAYED_LINE = 4,
    LAST_ROUTED_LINE = 3,
    NONE = 0,
    UNDEFINED = -2147483648,
    VERTICAL_LINES = 2,
class LineJumpStyleValue(IntEnum):
    ARC = 1,
    DEFAULT = 0,
    GAP = 2,
    SIDES_2 = 4,
    SIDES_3 = 5,
    SIDES_4 = 6,
    SIDES_5 = 7,
    SIDES_6 = 8,
    SIDES_7 = 9,
    SQUARE = 3,
    UNDEFINED = -2147483648,
class LineRouteExtValue(IntEnum):
    CURVED = 2,
    DEFAULT = 0,
    STRAIGHT = 1,
    UNDEFINED = -2147483648,
class LoadDataFilterOptions(IntEnum):
    ALL = 2147483647,
    DOCUMENT_PROPERTIES = 1,
    FONT = 8,
    SOLUTION_XML = 4,
    VBA = 2,
class LoadFileFormat(IntEnum):
    HTML = 13,
    VDW = 6,
    VDX = 0,
    VSD = 1,
    VSDM = 10,
    VSDX = 7,
    VSS = 3,
    VSSM = 11,
    VSSX = 9,
    VST = 5,
    VSTM = 12,
    VSTX = 8,
    VSX = 2,
    VTX = 4,
class LocalizeFontValue(IntEnum):
    ALWAYS_LOCALIZE_FONT = 1,
    LOCALIZE_FONT_ONLY_ARIAL_SYMBOL = 0,
    NEVER_LOCALIZE_FONT = 2,
    UNDEFINED = -2147483648,
class MeasureConst(IntEnum):
    AC = 36,
    AD = 81,
    AM = 84,
    AS = 85,
    BOOL = 97,
    C = 54,
    C_D = 52,
    CM = 69,
    COLOR = 251,
    CY = 111,
    D = 53,
    DA = 80,
    DATE = 40,
    DE = 42,
    DEG = 82,
    DL = 64,
    DP = 63,
    DT = 48,
    ED = 44,
    EH = 45,
    EM = 46,
    ES = 47,
    EW = 43,
    F_I = 67,
    FT = 66,
    GUID = 95,
    HA = 37,
    IN = 65,
    IN_F = 73,
    KM = 72,
    M = 71,
    MI = 68,
    MI_F = 74,
    MM = 70,
    MULTIDIM = 233,
    NM = 76,
    NUM = 32,
    NURBS = 138,
    P = 51,
    P_PT = 49,
    PER = 33,
    PNT = 225,
    POLYLINE = 139,
    PT = 50,
    RAD = 83,
    STR = 231,
    UNDEFINED = -2147483648,
    YD = 75,
class ObjectKindValue(IntEnum):
    HORIZONTAL_IN_VERTICAL = 1,
    STANDARD = 0,
    UNDEFINED = -2147483648,
class ObjectType(IntEnum):
    CONTROL = 1024,
    EMBEDDED_OBJECT = 512,
    LINKED_OBJECT = 256,
    OLE_2_NAMED = 16384,
    OLE_2_OBJECT = 32768,
    UNDEFINED = -2147483648,
class ObjTypeValue(IntEnum):
    DRAWING_CONTEXT = 0,
    SHAPE_NOT_PLACEABLE_NOT_ROUTABLE = 4,
    SHAPE_PLACEABLE = 1,
    SHAPE_PLACEABLE_ROUTABLE = 8,
    SHAPE_ROUTABLE = 2,
    UNDEFINED = -2147483648,
class OptionsValue(IntEnum):
    DELAY_QUERY = 8,
    NO_ADV_CONFIG = 4,
    NO_EXTERNAL_DATA_UI = 1,
    NO_LINK_ON_PASTE = 16,
    NO_REFRESH_UI = 2,
    UNDEFINED = -2147483648,
class OutputFormatValue(IntEnum):
    DEFAULT_PRINT = 0,
    HTML_OR_GIF_OUTPUT = 2,
    POWER_POINT_SLIDE_SHOW = 1,
    UNDEFINED = -2147483648,
class PageLineJumpDirXValue(IntEnum):
    DEFAULT_UP = 0,
    DOWN = 2,
    UNDEFINED = -2147483648,
    UP = 1,
class PageLineJumpDirYValue(IntEnum):
    DEFAULTLEFT = 0,
    LEFT = 1,
    RIGHT = 2,
    UNDEFINED = -2147483648,
class PaperSizeFormat(IntEnum):
    A_0 = 1,
    A_1 = 2,
    A_2 = 3,
    A_3 = 4,
    A_4 = 5,
    A_5 = 6,
    A_6 = 7,
    A_7 = 8,
    B_0 = 9,
    B_1 = 10,
    B_2 = 11,
    B_3 = 12,
    B_4 = 13,
    B_5 = 14,
    B_6 = 15,
    B_7 = 16,
    C_0 = 17,
    C_1 = 18,
    C_2 = 19,
    C_3 = 20,
    C_4 = 21,
    C_5 = 22,
    C_6 = 23,
    C_7 = 24,
    COM_10 = 32,
    COM_9 = 31,
    CUSTOM = 0,
    DL = 30,
    EXECUTIVE = 29,
    LEGAL = 26,
    LEGAL_13 = 27,
    LETTER = 25,
    MONARCH = 33,
    TABLOID = 28,
class PdfCompliance(IntEnum):
    PDF_15 = 0,
    PDF_A_1_A = 1,
    PDF_A_1_B = 2,
class PdfDigitalSignatureHashAlgorithm(IntEnum):
    MD_5 = 4,
    SHA_1 = 0,
    SHA_256 = 1,
    SHA_384 = 2,
    SHA_512 = 3,
class PdfEncryptionAlgorithm(IntEnum):
    RC_4_128 = 1,
    RC_4_40 = 0,
class PdfPermissions(IntEnum):
    ALLOW_ALL = 65535,
    CONTENT_COPY = 16,
    CONTENT_COPY_FOR_ACCESSIBILITY = 512,
    DISALLOW_ALL = 0,
    DOCUMENT_ASSEMBLY = 1024,
    FILL_IN = 256,
    HIGH_RESOLUTION_PRINTING = 2052,
    MODIFY_ANNOTATIONS = 32,
    MODIFY_CONTENTS = 8,
    PRINTING = 4,
class PdfTextCompression(IntEnum):
    FLATE = 1,
    NONE = 0,
class PinPosValue(IntEnum):
    BOTTOM_CENTER = 7,
    BOTTOM_LEFT = 6,
    BOTTOM_RIGHT = 8,
    CENTER_CENTER = 4,
    CENTER_LEFT = 3,
    CENTER_RIGHT = 5,
    TOP_CENTER = 1,
    TOP_LEFT = 0,
    TOP_RIGHT = 2,
    UNDEFINED = -2147483648,
class PixelOffsetMode(IntEnum):
    DEFAULT = 0,
    HALF = 4,
    HIGH_QUALITY = 2,
    HIGH_SPEED = 1,
    INVALID = -1,
    NONE = 3,
class PlaceDepthValue(IntEnum):
    DEEP = 2,
    MEDIUM = 1,
    PAGE_DEFAULT = 0,
    SHALLOW = 3,
    UNDEFINED = -2147483648,
class PlaceFlipValue(IntEnum):
    DEFAULT_NO_FLIP = 0,
    FLIP_90_INCREMENTS = 3,
    FLIP_HORIZONTAL = 1,
    FLIP_VERTICAL = 2,
    NO_FLIP = 4,
    UNDEFINED = -2147483648,
class PlaceStyleValue(IntEnum):
    BOTTOM_TO_TOP = 4,
    CIRCULAR = 6,
    DEFAULT_RADIAL = 0,
    LEFT_TO_RIGHT = 2,
    RADIAL = 3,
    RIGHT_TO_LEFT = 5,
    TOP_TO_BOTTOM = 1,
    UNDEFINED = -2147483648,
class PosValue(IntEnum):
    NORMAL_POSITION = 0,
    SUBSCRIPT = 2,
    SUPERSCRIPT = 1,
    UNDEFINED = -2147483648,
class PresetCameraType(IntEnum):
    ISOMETRIC_BOTTOM_DOWN = 0,
    ISOMETRIC_BOTTOM_UP = 1,
    ISOMETRIC_LEFT_DOWN = 2,
    ISOMETRIC_LEFT_UP = 3,
    ISOMETRIC_OFF_AXIS_1_LEFT = 4,
    ISOMETRIC_OFF_AXIS_1_RIGHT = 5,
    ISOMETRIC_OFF_AXIS_1_TOP = 6,
    ISOMETRIC_OFF_AXIS_2_LEFT = 7,
    ISOMETRIC_OFF_AXIS_2_RIGHT = 8,
    ISOMETRIC_OFF_AXIS_2_TOP = 9,
    ISOMETRIC_OFF_AXIS_3_BOTTOM = 10,
    ISOMETRIC_OFF_AXIS_3_LEFT = 11,
    ISOMETRIC_OFF_AXIS_3_RIGHT = 12,
    ISOMETRIC_OFF_AXIS_4_BOTTOM = 13,
    ISOMETRIC_OFF_AXIS_4_LEFT = 14,
    ISOMETRIC_OFF_AXIS_4_RIGHT = 15,
    ISOMETRIC_RIGHT_DOWN = 16,
    ISOMETRIC_RIGHT_UP = 17,
    ISOMETRIC_TOP_DOWN = 18,
    ISOMETRIC_TOP_UP = 19,
    LEGACY_OBLIQUE_BOTTOM = 20,
    LEGACY_OBLIQUE_BOTTOM_LEFT = 21,
    LEGACY_OBLIQUE_BOTTOM_RIGHT = 22,
    LEGACY_OBLIQUE_FRONT = 23,
    LEGACY_OBLIQUE_LEFT = 24,
    LEGACY_OBLIQUE_RIGHT = 25,
    LEGACY_OBLIQUE_TOP = 26,
    LEGACY_OBLIQUE_TOP_LEFT = 27,
    LEGACY_OBLIQUE_TOP_RIGHT = 28,
    LEGACY_PERSPECTIVE_BOTTOM = 29,
    LEGACY_PERSPECTIVE_BOTTOM_LEFT = 30,
    LEGACY_PERSPECTIVE_BOTTOM_RIGHT = 31,
    LEGACY_PERSPECTIVE_FRONT = 32,
    LEGACY_PERSPECTIVE_LEFT = 33,
    LEGACY_PERSPECTIVE_RIGHT = 34,
    LEGACY_PERSPECTIVE_TOP = 35,
    LEGACY_PERSPECTIVE_TOP_LEFT = 36,
    LEGACY_PERSPECTIVE_TOP_RIGHT = 37,
    OBLIQUE_BOTTOM = 38,
    OBLIQUE_BOTTOM_LEFT = 39,
    OBLIQUE_BOTTOM_RIGHT = 40,
    OBLIQUE_LEFT = 41,
    OBLIQUE_RIGHT = 42,
    OBLIQUE_TOP = 43,
    OBLIQUE_TOP_LEFT = 44,
    OBLIQUE_TOP_RIGHT = 45,
    ORTHOGRAPHIC_FRONT = 46,
    PERSPECTIVE_ABOVE = 47,
    PERSPECTIVE_ABOVE_LEFT_FACING = 48,
    PERSPECTIVE_ABOVE_RIGHT_FACING = 49,
    PERSPECTIVE_BELOW = 50,
    PERSPECTIVE_CONTRASTING_LEFT_FACING = 51,
    PERSPECTIVE_CONTRASTING_RIGHT_FACING = 52,
    PERSPECTIVE_FRONT = 53,
    PERSPECTIVE_HEROIC_EXTREME_LEFT_FACING = 54,
    PERSPECTIVE_HEROIC_EXTREME_RIGHT_FACING = 55,
    PERSPECTIVE_HEROIC_LEFT_FACING = 56,
    PERSPECTIVE_HEROIC_RIGHT_FACING = 57,
    PERSPECTIVE_LEFT = 58,
    PERSPECTIVE_RELAXED = 59,
    PERSPECTIVE_RELAXED_MODERATELY = 60,
    PERSPECTIVE_RIGHT = 61,
class PresetColorMatricsValue(IntEnum):
    COLOR_1 = 200,
    COLOR_2 = 201,
    COLOR_3 = 202,
    COLOR_4 = 203,
    COLOR_5 = 204,
    COLOR_6 = 205,
    COLOR_7 = 206,
class PresetQuickStyleValue(IntEnum):
    VARIANT_STYLE_1 = 100,
    VARIANT_STYLE_2 = 101,
    VARIANT_STYLE_3 = 102,
    VARIANT_STYLE_4 = 103,
class PresetShadowType(IntEnum):
    BELOW = 22,
    CUSTOM = 1,
    INSIDE_BOTTOM = 18,
    INSIDE_CENTER = 15,
    INSIDE_DIAGONAL_BOTTOM_LEFT = 17,
    INSIDE_DIAGONAL_BOTTOM_RIGHT = 19,
    INSIDE_DIAGONAL_TOP_LEFT = 11,
    INSIDE_DIAGONAL_TOP_RIGHT = 13,
    INSIDE_LEFT = 14,
    INSIDE_RIGHT = 16,
    INSIDE_TOP = 12,
    NO_SHADOW = 0,
    OFFSET_BOTTOM = 3,
    OFFSET_CENTER = 6,
    OFFSET_DIAGONAL_BOTTOM_LEFT = 4,
    OFFSET_DIAGONAL_BOTTOM_RIGHT = 2,
    OFFSET_DIAGONAL_TOP_LEFT = 10,
    OFFSET_DIAGONAL_TOP_RIGHT = 8,
    OFFSET_LEFT = 7,
    OFFSET_RIGHT = 5,
    OFFSET_TOP = 9,
    PERSPECTIVE_DIAGONAL_LOWER_LEFT = 23,
    PERSPECTIVE_DIAGONAL_LOWER_RIGHT = 24,
    PERSPECTIVE_DIAGONAL_UPPER_LEFT = 20,
    PERSPECTIVE_DIAGONAL_UPPER_RIGHT = 21,
class PresetStyleMatricsValue(IntEnum):
    STYLE_1 = 1,
    STYLE_2 = 2,
    STYLE_3 = 3,
    STYLE_4 = 4,
    STYLE_5 = 5,
    STYLE_6 = 6,
class PresetThemeValue(IntEnum):
    BUBBLE = 46,
    CLOUDS = 47,
    DAYBREAK = 39,
    FACET = 50,
    GEMSTONE = 48,
    INTEGRAL = 36,
    ION = 43,
    LINEAR = 34,
    LINES = 49,
    MARKER = 57,
    NO_THEME = 0,
    OFFICE = 33,
    ORGANIC = 45,
    PARALLEL = 40,
    PEN = 56,
    PENCIL = 55,
    PROMINENCE = 51,
    RADIANCE = 53,
    RETROSPECT = 44,
    SEQUENCE = 41,
    SHADE = 54,
    SIMPLE = 37,
    SLICE = 42,
    SMOKE = 52,
    WHISP = 38,
    WHITE_BOARD = 58,
    ZEPHYR = 35,
class PresetThemeVariantValue(IntEnum):
    VARIANT_1 = 0,
    VARIANT_2 = 1,
    VARIANT_3 = 2,
    VARIANT_4 = 3,
class PreviewScopeValue(IntEnum):
    ALL_PAGES = 2,
    FIRST_PAGE = 0,
    NO_PREVIEW = 1,
    UNDEFINED = -2147483648,
class PrintPageOrientationValue(IntEnum):
    LANDSCAPE = 2,
    PORTRAIT = 1,
    SAME_AS_PRINTER = 0,
    UNDEFINED = -2147483648,
class PropType(IntEnum):
    BOOL = 1,
    DATE = 2,
    NUMBER = 3,
    STRING = 0,
class RectangleAlignmentType(IntEnum):
    BOTTOM = 0,
    BOTTOM_LEFT = 1,
    BOTTOM_RIGHT = 2,
    CENTER = 3,
    LEFT = 4,
    RIGHT = 5,
    TOP = 6,
    TOP_LEFT = 7,
    TOP_RIGHT = 8,
class ReflectionEffectType(IntEnum):
    CUSTOM = 1,
    FULL_REFLECTION_4_PT_OFFSET = 7,
    FULL_REFLECTION_8_PT_OFFSET = 10,
    FULL_REFLECTION_TOUCHING = 4,
    HALF_REFLECTION_4_PT_OFFSET = 6,
    HALF_REFLECTION_8_PT_OFFSET = 9,
    HALF_REFLECTION_TOUCHING = 3,
    NONE = 0,
    TIGHT_REFLECTION_4_PT_OFFSET = 5,
    TIGHT_REFLECTION_8_PT_OFFSET = 8,
    TIGHT_REFLECTION_TOUCHING = 2,
class RelationFlag(IntEnum):
    ASSOCIATED_WITH_CALLOUTS = 3,
    BOTTOM_BOUNDARY_EDGE = 10,
    LEFT_BOUNDARY_EDGE = 7,
    LIST_OVERLAPS = 11,
    MEMBER_OF_CONTAINERS = 4,
    MEMBER_OF_LIST = 5,
    MEMBERS_OF_CONTAINER_SHAPES = 1,
    MEMBERS_OF_LIST_SHAPES = 2,
    RIGHT_BOUNDARY_EDGE = 8,
    SHAPE_ASSOCIATED_WITH_CALLOUT = 6,
    TOP_BOUNDARY_EDGE = 9,
    UNDEFINED = -2147483648,
class RemoveHiddenInfoItem(IntEnum):
    DATA_RECORD_SETS = 16,
    MASTERS = 4,
    PERSONAL_INFO = 1,
    SHAPES = 2,
    STYLES = 8,
    UNDEFINED = -2147483648,
class ResizeModeValue(IntEnum):
    REPOSITION_ONLY = 1,
    SCALE_WITH_GROUP = 2,
    UNDEFINED = -2147483648,
    USE_GROUP_SETTING = 0,
class RotationTypeValue(IntEnum):
    NONE = 0,
    OBLIQUE_FROM_BOTTOM_LEFT = 5,
    OBLIQUE_FROM_BOTTOM_RIGHT = 6,
    OBLIQUE_FROM_TOP_LEFT = 3,
    OBLIQUE_FROM_TOP_RIGHT = 4,
    PARALLEL = 1,
    PERSPECTIVE = 2,
    UNDEFINED = 7,
class RouteStyleValue(IntEnum):
    CENTER_TO_CENTER = 16,
    DEFAULT_RIGHT_ANGLE = 0,
    FLOWCHART_BOTTOM_TO_TOP = 12,
    FLOWCHART_LEFT_TO_RIGHT = 6,
    FLOWCHART_RIGHT_TO_LEFT = 13,
    FLOWCHART_TOP_TO_BOTTOM = 5,
    NETWORK = 9,
    ORGANIZATION_CHART_BOTTOM_TO_TOP = 10,
    ORGANIZATION_CHART_LEFT_TO_RIGHT = 4,
    ORGANIZATION_CHART_RIGHT_TO_LEFT = 11,
    ORGANIZATION_CHART_TOP_TO_BOTTOM = 3,
    RIGHT_ANGLE = 1,
    SIMPLE_BOTTOM_TO_TOP = 19,
    SIMPLE_HORIZONTAL_VERTICAL = 21,
    SIMPLE_LEFT_TO_RIGHT = 18,
    SIMPLE_RIGHT_TO_LEFT = 20,
    SIMPLE_TOP_TO_BOTTOM = 17,
    SIMPLE_VERTICAL_HORIZONTAL = 22,
    STRAIGHT = 2,
    TREE_BOTTOM_TO_TOP = 14,
    TREE_LEFT_TO_RIGHT = 8,
    TREE_RIGHT_TO_LEFT = 15,
    TREE_TOP_TO_BOTTOM = 7,
    UNDEFINED = -2147483648,
class RulerDensityValue(IntEnum):
    COARSE = 8,
    FINE = 32,
    NORMAL = 16,
    UNDEFINED = -2147483648,
class SaveFileFormat(IntEnum):
    BMP = 5,
    CSV = 21,
    EMF = 6,
    GIF = 10,
    HTML = 11,
    JPEG = 7,
    PDF = 8,
    PNG = 4,
    SVG = 12,
    TIFF = 3,
    VDX = 0,
    VSD = 22,
    VSDM = 18,
    VSDX = 15,
    VSS = 23,
    VSSM = 19,
    VSSX = 17,
    VST = 24,
    VSTM = 20,
    VSTX = 16,
    VSX = 1,
    VTX = 2,
    XAML = 14,
    XPS = 9,
class SelectModeValue(IntEnum):
    GROUP_SHAPE_FIRST = 1,
    GROUP_SHAPE_ONLY = 0,
    MEMBERS_GROUP_FIRST = 2,
    UNDEFINED = -2147483648,
class ShapeFixedCodeValue(IntEnum):
    ALLOW_ROUTING_TO_SIDES_WITH_CONNECTION_POINTS = 64,
    IGNORE_CONNECTION_POINT = 32,
    NO_GLUE_TO_PERIMETER = 128,
    NO_MOVE_ALLOW_SHAPES_PLACED = 4,
    NO_MOVE_AND_NO_ALLOW_SHAPES_PLACED = 2,
    NO_MOVE_USING_LAY_OUT_SHAPES = 1,
    UNDEFINED = -2147483648,
class ShapePlaceFlipValue(IntEnum):
    FLIP_90_DEGREE_INCREMENT_BETWEEN_0_AND_270 = 4,
    FLIP_HORIZONTAL = 1,
    FLIP_VERTICAL = 2,
    NO_FLIP = 8,
    UNDEFINED = -2147483648,
    USE_PAGE_DEFAULT = 0,
class ShapePlaceStyleValue(IntEnum):
    PLACE_BOTTOM_TO_TOP = 4,
    PLACE_CIRCULAR = 6,
    PLACE_COMPACT_DOWN_LEFT = 14,
    PLACE_COMPACT_DOWN_RIGHT = 7,
    PLACE_COMPACT_LEFT_DOWN = 13,
    PLACE_COMPACT_LEFT_UP = 12,
    PLACE_COMPACT_RIGHT_DOWN = 8,
    PLACE_COMPACT_RIGHT_UP = 9,
    PLACE_COMPACT_UP_LEFT = 11,
    PLACE_COMPACT_UP_RIGHT = 10,
    PLACE_DEFAULT = 0,
    PLACE_HIERARCHY_BOTTOM_TO_CENTER = 20,
    PLACE_HIERARCHY_BOTTOM_TO_LEFT = 19,
    PLACE_HIERARCHY_BOTTOM_TO_RIGHT = 21,
    PLACE_HIERARCHY_LEFT_TO_RIGHT_BOTTOM = 24,
    PLACE_HIERARCHY_LEFT_TO_RIGHT_MIDDLE = 23,
    PLACE_HIERARCHY_LEFT_TO_RIGHT_TOP = 22,
    PLACE_HIERARCHY_RIGHT_TO_LEFT_BOTTOM = 27,
    PLACE_HIERARCHY_RIGHT_TO_LEFT_MIDDLE = 26,
    PLACE_HIERARCHY_RIGHT_TO_LEFT_TOP = 25,
    PLACE_HIERARCHY_TOP_TO_BOTTOM_CENTER = 17,
    PLACE_HIERARCHY_TOP_TO_BOTTOM_LEFT = 16,
    PLACE_HIERARCHY_TOP_TO_BOTTOM_RIGHT = 18,
    PLACE_PARENT_DEFAULT = 15,
    PLACE_RADIAL = 3,
    PLACE_RIGHT_TO_LEFT = 5,
    PLACE_TO_RIGHT = 2,
    PLACE_TOP_TO_BOTTOM = 1,
    UNDEFINED = 28,
class ShapePlowCodeValue(IntEnum):
    MOVE_SHAPE = 2,
    NOMOVE_SHAPE = 1,
    UNDEFINED = -2147483648,
    USE_PAGE_DEFAULT = 0,
class ShapeRouteStyleValue(IntEnum):
    CENTER_TO_CENTER = 16,
    FLOWCHART_BOTTOM_TO_TOP = 12,
    FLOWCHART_LEFT_TO_RIGHT = 6,
    FLOWCHART_RIGHT_TO_LEFT = 13,
    FLOWCHART_TOP_TO_BOTTOM = 5,
    NETWORK = 9,
    ORGANIZATION_CHART_BOTTOM_TO_TOP = 10,
    ORGANIZATION_CHART_LEFT_TO_RIGHT = 4,
    ORGANIZATION_CHART_RIGHT_TO_LEFT = 11,
    ORGANIZATION_CHART_TOP_TO_BOTTOM = 3,
    PAGE_DEFAULT = 0,
    RIGHT_ANGLE = 1,
    SIMPLE_BOTTOM_TO_TOP = 19,
    SIMPLE_HORIZONTAL_VERTICAL = 21,
    SIMPLE_LEFT_TO_RIGHT = 18,
    SIMPLE_RIGHT_TO_LEFT = 20,
    SIMPLE_TOP_TO_BOTTOM = 17,
    SIMPLE_VERTICAL_HORIZONTAL = 22,
    STRAIGHT = 2,
    TREE_BOTTOM_TO_TOP = 14,
    TREE_LEFT_TO_RIGHT = 8,
    TREE_RIGHT_TO_LEFT = 15,
    TREE_TOP_TO_BOTTOM = 7,
    UNDEFINED = -2147483648,
class ShapeShdwShowValue(IntEnum):
    ALWAYS_SHOW = 2,
    HAS_GEOM_SHOW = 0,
    TOP_LEVEL_SHOW = 1,
    UNDEFINED = -2147483648,
class ShapeShdwTypeValue(IntEnum):
    INNER = 3,
    OBLIQUE = 2,
    SIMPLE = 1,
    UNDEFINED = -2147483648,
    USE_PAGE = 0,
class ShdwTypeValue(IntEnum):
    OBLIQUE = 1,
    SIMPLE = 0,
    UNDEFINED = -2147483648,
class ShowDropButtonType(IntEnum):
    ALWAYS = 2,
    FOCUS = 1,
    NEVER = 0,
class SmoothingMode(IntEnum):
    ANTI_ALIAS = 4,
    DEFAULT = 0,
    HIGH_QUALITY = 2,
    HIGH_SPEED = 1,
    INVALID = -1,
    NONE = 3,
class SnapExtensions(IntEnum):
    ALIGNMENT_BOX_EXTENSION = 1,
    CENTER_AXES = 2,
    CURVE_EXTENSION = 64,
    CURVE_TANGENT = 4,
    ELLIPSE_CENTER = 2048,
    ENDPOINT = 8,
    ENDPOINT_HORIZONTAL = 512,
    ENDPOINT_PERPENDICULAR = 128,
    ENDPOINT_VERTICAL = 1024,
    ISOMETRIC_ANGLES = 4096,
    LINEAR_EXTENSION = 32,
    MIDPOINT = 16,
    MIDPOINT_PERPENDICULAR = 256,
    NONE = 0,
    UNDEFINED = -2147483648,
class SnapExtensionsValue(IntEnum):
    SNAP_TO_ALIGNMENT_BOX_EXTENSION = 1,
    SNAP_TO_CENTER_AXIS_EXTENSION = 2,
    SNAP_TO_CURVE_EXTENSION = 64,
    SNAP_TO_CURVE_TANGENT_EXTENSION = 4,
    SNAP_TO_ELLIPSE_CENTER_EXTENSION = 2048,
    SNAP_TO_END_POINT_EXTENSION = 8,
    SNAP_TO_END_POINT_HORIZONTAL_EXTENSION = 512,
    SNAP_TO_END_POINT_PERPENDICULAR_EXTENSION = 128,
    SNAP_TO_END_POINT_VERTICAL_EXTENSION = 1024,
    SNAP_TO_ISOMETRIC_ANGLES_EXTENSION = 4096,
    SNAP_TO_LINEAR_EXTENSION = 32,
    SNAP_TO_MID_POINT_EXTENSION = 16,
    SNAP_TO_MID_POINT_PERPENDICULAR_EXTENSION = 256,
    SNAP_TO_NOTHING = 0,
    UNDEFINED = -2147483648,
class SnapSettings(IntEnum):
    ALIGNMENT_BOX = 512,
    CONNECTION_POINTS = 32,
    DISABLED = 32768,
    EXTENSIONS = 1024,
    GEOMETRY = 256,
    GRID = 2,
    GUIDES = 4,
    HANDLES = 8,
    INTERSECTIONS = 65536,
    NONE = 0,
    RULER_SUBDIVISIONS = 1,
    UNDEFINED = -2147483648,
    VERTICES = 16,
class SnapSettingsValue(IntEnum):
    SNAP_DISABLED = 32768,
    SNAP_TO_ALIGNMENT_BOX = 512,
    SNAP_TO_CONNECTION_POINTS = 32,
    SNAP_TO_GRID = 2,
    SNAP_TO_GUIDES = 4,
    SNAP_TO_INTERSECTIONS = 65536,
    SNAP_TO_NOTHING = 0,
    SNAP_TO_RULER_SUBDIVISIONS = 1,
    SNAP_TO_SELECTION_HANDLES = 8,
    SNAP_TO_SHAPE_EXTENSIONS_OPTIONS = 1024,
    SNAP_TO_THE_VISIBLE_EDGES_OF_SHAPES = 256,
    SNAP_TO_VERTICES = 16,
    UNDEFINED = -2147483648,
class StyleValue(IntEnum):
    BOLD = 1,
    ITALIC = 2,
    SMALL_CAPS = 8,
    UNDEFINED = -2147483648,
    UNDERLINE = 4,
class TextDirectionValue(IntEnum):
    HORIZONTAL = 0,
    UNDEFINED = -2147483648,
    VERTICAL = 1,
class TiffCompression(IntEnum):
    CCITT_3 = 3,
    CCITT_4 = 4,
    LZW = 5,
    NONE = 1,
    RLE = 2,
class ToPartValue(IntEnum):
    CONNECTION_POINT = 100,
    GUIDE_INTERSECTION = 4,
    GUIDE_X = 1,
    GUIDE_Y = 2,
    NONE = 0,
    TO_ANGLE = 7,
    UNDEFINED = -2147483648,
    WHOLE_SHAPE = 3,
class TypeConnectionValue(IntEnum):
    INWARD = 0,
    INWARD_OUTWARD = 2,
    OUTWARD = 1,
    UNDEFINED = -2147483648,
class TypeFieldValue(IntEnum):
    CURRENCY = 7,
    DATE_TIME = 5,
    DURATION = 6,
    NUMBER = 2,
    STRING = 0,
    UNDEFINED = -2147483648,
class TypePropValue(IntEnum):
    BOOLEAN = 3,
    CURRENCY = 7,
    DATE_TIME = 5,
    DURATION = 6,
    FIXED_LIST = 1,
    NUMBER = 2,
    STRING = 0,
    UNDEFINED = -2147483648,
    VARIABLE_LIST = 4,
class TypeValue(IntEnum):
    FOREIGN = 3,
    GROUP = 0,
    GUIDE = 2,
    SHAPE = 1,
    UNDEFINED = -2147483648,
class UIVisibilityValue(IntEnum):
    HIDDEN = 1,
    UNDEFINED = -2147483648,
    VISIBLE = 0,
class VbaModuleType(IntEnum):
    CLASS = 2,
    DESIGNER = 3,
    DOCUMENT = 1,
    PROCEDURAL = 0,
class VbaProjectReferenceType(IntEnum):
    CONTROL = 1,
    PROJECT = 2,
    REGISTERED = 0,
class VerticalAlignValue(IntEnum):
    BOTTOM = 2,
    MIDDLE = 1,
    TOP = 0,
    UNDEFINED = -2147483648,
class VisRuleTargetsValue(IntEnum):
    UNDEFINED = -2147483648,
    VIS_RULE_TARGET_DOCUMENT = 2,
    VIS_RULE_TARGET_PAGE = 1,
    VIS_RULE_TARGET_SHAPE = 0,
class WalkPreferenceValue(IntEnum):
    SIDE_TO_SIDE_CONNECTIONS = 0,
    SIDE_TO_TOP_OR_SIDE_TO_BOTTOM_CONNECTIONS = 2,
    TOP_TO_BOTTOM_CONNECTIONS = 3,
    TOP_TO_SIDE_OR_BOTTOM_TO_SIDE_CONNECTIONS = 1,
    UNDEFINED = -2147483648,
class WarningType(IntEnum):
    FONT_SUBSTITUTION = 0,
    UNSUPPORTED_IMAGE_TYPE = 1,
class WindowStateValue(IntEnum):
    ACTIVE = 67108864,
    ANCHOR_BOTTOM = 256,
    ANCHOR_LEFT = 32,
    ANCHOR_MERGED = 1024,
    ANCHOR_RIGHT = 128,
    ANCHOR_TOP = 64,
    DOCKED_BOTTOM = 8,
    DOCKED_LEFT = 1,
    DOCKED_RIGHT = 4,
    DOCKED_TOP = 2,
    DOUBLEING = 16,
    MAXIMIZED = 1073741824,
    MINIMIZED = 536870912,
    RESTORED = 268435456,
    UNDEFINED = -2147483648,
class WindowTypeValue(IntEnum):
    DRAWING = 1,
    ICON = 4,
    SHEET = 3,
    STENCIL = 2,
    UNDEFINED = -2147483648,
class XJustifyValue(IntEnum):
    CENTERED = 1,
    LEFT_JUSTIFIED = 0,
    RIGHT_JUSTIFIED = 2,
    UNDEFINED = -2147483648,
class YJustifyValue(IntEnum):
    BOTTOM_JUSTIFIED = 2,
    CENTERED = 1,
    TOP_JUSTIFIED = 0,
    UNDEFINED = -2147483648,
class Zip64Option(IntEnum):
    ALWAYS = 2,
    AS_NECESSARY = 1,
    DEFAULT = 0,
    NEVER = 0,
class ZipEntryTimestamp(IntEnum):
    DOS = 1,
    INFO_ZIP_1 = 8,
    NONE = 0,
    UNIX = 4,
    WINDOWS = 2,

from com.aspose.diagram import Act
from com.aspose.diagram import Alignment
from com.aspose.diagram import ArcTo
from com.aspose.diagram import ArrowSize
from com.aspose.diagram import AutoSpaceOptions
from com.aspose.diagram import BevelLightingType
from com.aspose.diagram import BevelMaterialType
from com.aspose.diagram import BevelType
from com.aspose.diagram import BoolValue
from com.aspose.diagram import Bullet
from com.aspose.diagram import Calendar
from com.aspose.diagram import Case
from com.aspose.diagram import Char
from com.aspose.diagram import Color
from com.aspose.diagram import ColorEntry
from com.aspose.diagram import ColorValue
from com.aspose.diagram import CompoundType
from com.aspose.diagram import ConFixedCode
from com.aspose.diagram import ConLineJumpCode
from com.aspose.diagram import ConLineJumpDirX
from com.aspose.diagram import ConLineJumpDirY
from com.aspose.diagram import ConLineJumpStyle
from com.aspose.diagram import ConLineRouteExt
from com.aspose.diagram import Connect
from com.aspose.diagram import Connection
from com.aspose.diagram import ConnectionABCD
from com.aspose.diagram import Control
from com.aspose.diagram import ConType
from com.aspose.diagram import Cp
from com.aspose.diagram import CustomProp
from com.aspose.diagram import CustomPropCollection
from com.aspose.diagram import CustomValue
from com.aspose.diagram import DataColumn
from com.aspose.diagram import DataConnection
from com.aspose.diagram import DataRecordSet
from com.aspose.diagram import DateTime
from com.aspose.diagram import DateValue
from com.aspose.diagram import Diagram
from com.aspose.diagram import DiagramException
from com.aspose.diagram import DiagramSaveOptions
from com.aspose.diagram import DigitalSignature
from com.aspose.diagram import DigitalSignatureCollection
from com.aspose.diagram import DisplayMode
from com.aspose.diagram import DisplayModeSmartTagDef
from com.aspose.diagram import DoubleValue
from com.aspose.diagram import DrawingResizeType
from com.aspose.diagram import DrawingScaleType
from com.aspose.diagram import DrawingSizeType
from com.aspose.diagram import DynFeedback
from com.aspose.diagram import Ellipse
from com.aspose.diagram import EllipticalArcTo
from com.aspose.diagram import EventItem
from com.aspose.diagram import EventItemCollection
from com.aspose.diagram import Field
from com.aspose.diagram import FileFontSource
from com.aspose.diagram import FileFormatInfo
from com.aspose.diagram import FileFormatUtil
from com.aspose.diagram import Fld
from com.aspose.diagram import FloatPointNumCollection
from com.aspose.diagram import FolderFontSource
from com.aspose.diagram import Font
from com.aspose.diagram import FontCollection
from com.aspose.diagram import FontConfigs
from com.aspose.diagram import Geom
from com.aspose.diagram import GlueType
from com.aspose.diagram import GradientStop
from com.aspose.diagram import GraphicsPathConverter
from com.aspose.diagram import GridDensity
from com.aspose.diagram import HorzAlign
from com.aspose.diagram import HTMLSaveOptions
from com.aspose.diagram import Hyperlink
from com.aspose.diagram import ImageAttributes
from com.aspose.diagram import ImageSaveOptions
from com.aspose.diagram import IndividualFontConfigs
from com.aspose.diagram import InfiniteLine
from com.aspose.diagram import InterruptMonitor
from com.aspose.diagram import IntValue
from com.aspose.diagram import Issue
from com.aspose.diagram import IssueTarget
from com.aspose.diagram import Layer
from com.aspose.diagram import LayoutOptions
from com.aspose.diagram import License
from com.aspose.diagram import LineAdjustFrom
from com.aspose.diagram import LineAdjustTo
from com.aspose.diagram import LineJumpCode
from com.aspose.diagram import LineJumpStyle
from com.aspose.diagram import LineRouteExt
from com.aspose.diagram import LineTo
from com.aspose.diagram import LoadFilter
from com.aspose.diagram import LoadOptions
from com.aspose.diagram import LocalizeFont
from com.aspose.diagram import Margin
from com.aspose.diagram import Master
from com.aspose.diagram import MasterShortcut
from com.aspose.diagram import MemoryFontSource
from com.aspose.diagram import Metered
from com.aspose.diagram import MilestoneHelper
from com.aspose.diagram import MoveTo
from com.aspose.diagram import NullableInt64
from com.aspose.diagram import NURBSTo
from com.aspose.diagram import ObjectKind
from com.aspose.diagram import ObjType
from com.aspose.diagram import OutputFormat
from com.aspose.diagram import Page
from com.aspose.diagram import PageLineJumpDirX
from com.aspose.diagram import PageLineJumpDirY
from com.aspose.diagram import PageSize
from com.aspose.diagram import Para
from com.aspose.diagram import PdfEncryptionDetails
from com.aspose.diagram import PdfSaveOptions
from com.aspose.diagram import PlaceDepth
from com.aspose.diagram import PlaceFlip
from com.aspose.diagram import PlaceStyle
from com.aspose.diagram import PolylineTo
from com.aspose.diagram import Pos
from com.aspose.diagram import Pp
from com.aspose.diagram import PreviewScope
from com.aspose.diagram import PrintPageOrientation
from com.aspose.diagram import PrintSaveOptions
from com.aspose.diagram import Prop
from com.aspose.diagram import RelationShape
from com.aspose.diagram import RelationShapeCollection
from com.aspose.diagram import RelCubBezTo
from com.aspose.diagram import RelEllipticalArcTo
from com.aspose.diagram import RelLineTo
from com.aspose.diagram import RelMoveTo
from com.aspose.diagram import RelQuadBezTo
from com.aspose.diagram import ResizeMode
from com.aspose.diagram import Reviewer
from com.aspose.diagram import RotationType
from com.aspose.diagram import RouteStyle
from com.aspose.diagram import Row
from com.aspose.diagram import Rule
from com.aspose.diagram import RuleInfo
from com.aspose.diagram import RulerDensity
from com.aspose.diagram import RuleSet
from com.aspose.diagram import RuleValue
from com.aspose.diagram import Scratch
from com.aspose.diagram import SelectMode
from com.aspose.diagram import Sha1Hasher
from com.aspose.diagram import Shape
from com.aspose.diagram import ShapeFixedCode
from com.aspose.diagram import ShapePlaceFlip
from com.aspose.diagram import ShapePlaceStyle
from com.aspose.diagram import ShapePlowCode
from com.aspose.diagram import ShapeRouteStyle
from com.aspose.diagram import ShapeShdwShow
from com.aspose.diagram import ShapeShdwType
from com.aspose.diagram import ShdwType
from com.aspose.diagram import SmartTagDef
from com.aspose.diagram import SolutionXML
from com.aspose.diagram import SplineKnot
from com.aspose.diagram import SplineStart
from com.aspose.diagram import Str2Value
from com.aspose.diagram import StrValue
from com.aspose.diagram import Style
from com.aspose.diagram import StyleSheet
from com.aspose.diagram import SVGSaveOptions
from com.aspose.diagram import Text
from com.aspose.diagram import TextDirection
from com.aspose.diagram import TimeLineHelper
from com.aspose.diagram import Tp
from com.aspose.diagram import Txt
from com.aspose.diagram import TxtSaveOptions
from com.aspose.diagram import TypeConnection
from com.aspose.diagram import TypeField
from com.aspose.diagram import TypeProp
from com.aspose.diagram import UIVisibility
from com.aspose.diagram import UnitFormulaErr
from com.aspose.diagram import UnitFormulaErrV
from com.aspose.diagram import User
from com.aspose.diagram import ValidationProperties
from com.aspose.diagram import VerticalAlign
from com.aspose.diagram import WalkPreference
from com.aspose.diagram import WarningInfo
from com.aspose.diagram import Window
from com.aspose.diagram import X509Certificate2
from com.aspose.diagram import XAMLSaveOptions
from com.aspose.diagram import XJustify
from com.aspose.diagram import XPSSaveOptions
from com.aspose.diagram import YJustify

from com.aspose.diagram import Encoding
from com.aspose.diagram import ImageFormat
from com.aspose.diagram import SaveOptions


@JImplementationFor("com.aspose.diagram.License")
class _License(object):

    @JOverride(sticky=False)
    def setLicense(self, arg):
        if arg == None:
            raise Exception("an argument is required")
        elif arg.__class__.__name__ != 'bytes' and arg.__class__.__name__ != 'str':
            raise TypeError("a bytes-like or string object is required")
        elif len(arg) <= 0:
            raise ValueError("no content")
        
        if arg.__class__.__name__ == 'str':
            self._setLicense(arg)
            return

        if arg.__class__.__name__ == 'bytes':
            sb = StreamBuffer()
            sb.write(arg)
            self._setLicense(sb.toInputStream())
        return

@JImplementationFor("com.aspose.diagram.Diagram")
class _Diagram(object):

    @staticmethod
    def createDiagramFromBytes(byte_array, **kwargs):
        sb = StreamBuffer()
        sb.write(byte_array)
        loadOptions = kwargs.get("loadOptions")
        if loadOptions == None:
            return Diagram(sb.toInputStream())
        else:
            return Diagram(sb.toInputStream(), loadOptions)
    
    def saveToBytes(self, arg):
        sb = StreamBuffer()
        self.save(sb, arg)
        buf = sb.toByteArray()
        if buf != None and buf.length > 0:
            return array("b", buf).tobytes()
        else:
            return b''

@JImplementationFor("com.aspose.diagram.FileFormatUtil")
class _FileFormatUtil(object):

    @staticmethod
    def detectFileFormatFromBytes(file_bytes):
        sb = StreamBuffer()
        sb.write(file_bytes)
        return FileFormatUtil.detectFileFormat(sb.toInputStream())

from com.aspose.diagram import Shape
@JImplementationFor("com.aspose.diagram.Shape")
class _Shape(object):

    def toImageBytes(self, options):
        sb = StreamBuffer()
        self.toImage(sb, options)
        buf = sb.toByteArray()
        return array("b", buf).tobytes()

    def toPdfBytes(self, *args):
        sb = StreamBuffer()
        self.toPdf(sb)
        buf = sb.toByteArray()
        return array("b", buf).tobytes()
