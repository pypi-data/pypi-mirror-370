from agent.exception.exception_constants import exception_constants


class ParameterMissingException(Exception):
    def __init__(self, code: str = exception_constants.PARAMETER_MISSING_EXCEPTION,
                 message: str = exception_constants.PARAMETER_MISSING_EXCEPTION_MSG):
        self.code = code
        self.message = message


class ParameterVerifyException(Exception):
    def __init__(self, code: str = exception_constants.PARAMETER_VERIFY_EXCEPTION,
                 message: str = exception_constants.PARAMETER_VERIFY_EXCEPTION_MSG):
        self.code = code
        self.message = message


class TextModerationException(Exception):
    def __init__(self, code: str = exception_constants.TEXT_MODERATION_EXCEPTION,
                 message: str = exception_constants.TEXT_MODERATION_VIOLENCE_MSG):
        self.code = code
        self.message = message


class ContainsChineseException(Exception):
    def __init__(self, code: str = exception_constants.CONTAINS_CHINESE_EXCEPTION,
                 message: str = exception_constants.CONTAINS_CHINESE_EXCEPTION_MSG):
        self.code = code
        self.message = message


class CommonException(Exception):
    def __init__(self, code: str = exception_constants.INNER_EXCEPTION,
                 message: str = exception_constants.INNER_EXCEPTION_MSG):
        self.code = code
        self.message = message

class MathpixPicture2TextException(Exception):
    def __init__(self, code: str = exception_constants.MATHPIX_PICTURE2TEXT_EXCEPTION,
                 message: str = exception_constants.MATHPIX_PICTURE2TEXT_EXCEPTION_MSG):
        self.code = code
        self.message = message


class Xml2MdException(Exception):
    def __init__(self, code: str = exception_constants.XML2MD_EXCEPTION,
                 message: str = exception_constants.XML2MD_EXCEPTION_MSG):
        self.code = code
        self.message = message

class GET_PIC_FAIL_EXCEPTION(Exception):
    def __init__(self, code: str = exception_constants.GET_PIC_FAIL_EXCEPTION,
                 message: str = exception_constants.GET_PIC_FAIL_EXCEPTION_MSG):
        self.code = code
        self.message = message

class ZJALGO_PICTURE2TEXT_EXCEPTION(Exception):
    def __init__(self, code: str = exception_constants.ZJALGO_PICTURE2TEXT_EXCEPTION,
                 message: str = exception_constants.ZJALGO_PICTURE2TEXT_EXCEPTION_MSG):
        self.code = code
        self.message = message

class ProcessHistoryException(Exception):
    def __init__(self, code: str = exception_constants.DOCUMENT_EXTRACTION_EXCEPTION,
                 message: str = exception_constants.DOCUMENT_EXTRACTION_EXCEPTION_MSG):
        self.code = code
        self.message = message
class DocumentExtractionException(Exception):
    def __init__(self, code: str = exception_constants.DOCUMENT_EXTRACTION_EXCEPTION,
                 message: str = exception_constants.DOCUMENT_EXTRACTION_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DocumentStructureException(Exception):
    def __init__(self, code: str = exception_constants.DOCUMENT_STRUCTURE_EXCEPTION,
                 message: str = exception_constants.DOCUMENT_STRUCTURE_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationLineChartException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_LINE_CHART_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_LINE_CHART_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationBarChartException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_BAR_CHART_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_BAR_CHART_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationMapScatterPlotException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_MAP_SCATTER_PLOT_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_MAP_SCATTER_PLOT_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationStackedColumnChartException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_STACKED_COLUMN_CHART_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_STACKED_COLUMN_CHART_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationLineChartWithConferenceIntervalException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_LINE_CHART_WITH_CONFERENCE_INTERVAL_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_LINE_CHART_WITH_CONFERENCE_INTERVAL_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationHistogramException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_HISTOGRAM_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_HISTOGRAM_EXCEPTION_MSG):
        self.code = code
        self.message = message


class DataVisualizationStereographicProjectionException(Exception):
    def __init__(self, code: str = exception_constants.DATA_VISUALIZATION_STEREOGRAPHIC_PROJECTION_EXCEPTION,
                 message: str = exception_constants.DATA_VISUALIZATION_STEREOGRAPHIC_PROJECTION_EXCEPTION_MSG):
        self.code = code
        self.message = message
