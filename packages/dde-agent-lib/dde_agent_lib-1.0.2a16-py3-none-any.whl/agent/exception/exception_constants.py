from pydantic import BaseModel



class ExceptionConstants(BaseModel):
    SUCCESS_CODE: str = "core.ok"
    SUCCESS_MSG: str = "success"

    """系统通用异常"""
    # 通用异常
    INNER_EXCEPTION: str = "100001"
    INNER_EXCEPTION_MSG: str = "Sorry, something went wrong"
    # FastAPI route校验异常
    ROUTE_VALIDATION_EXCEPTION: str = "100002"
    # FastAPI HTTP未知异常
    HTTP_SYSTEM_EXCEPTION: str = "100003"
    # 参数丢失
    PARAMETER_MISSING_EXCEPTION: str = "100004"
    PARAMETER_MISSING_EXCEPTION_MSG: str = "Parameter '{param}' is missing"
    # 参数校验失败
    PARAMETER_VERIFY_EXCEPTION: str = "100006"
    PARAMETER_VERIFY_EXCEPTION_MSG: str = "Parameter '{param}' is invalid"
    # fegin服务不健康
    SERVICE_NOT_HEALTHY: str = "100007"
    SERVICE_NOT_HEALTHY_MSG: str = "service [{service}] not healthy"
    # 限流相关异常
    TOO_MANY_CALLS_EXCEPTION: str = "100008"
    TOO_MANY_CALLS_MSG: str = "Please wait a moment and I will answer your question as soon as possible，because there are a lot of questions to deal with at the moment."

    INTERRUPTED_EXCEPTION: str = "100009"  # 用户在portal手动中断
    PLUGIN_THROW_EXCEPTION: str = "100010"  # plugin插件返回异常msg
    """业务自定义异常"""
    # --------------------------流式输出----------------------------------------
    # 流式输出结果包含中文
    CONTAINS_CHINESE_EXCEPTION: str = "110001"
    CONTAINS_CHINESE_EXCEPTION_MSG: str = "Sorry, there is no content can be displayed."  # sse result contains chinese_character
    # 文本检测异常
    TEXT_MODERATION_EXCEPTION: str = "110002"
    TEXT_MODERATION_VIOLENCE_MSG: str = "Sorry, the content involves violence"
    TEXT_MODERATION_CONTRABAND_MSG: str = "Sorry, the content involves contraband"
    TEXT_MODERATION_SEXUALITY_MSG: str = "Sorry, the content involves sexuality"
    TEXT_MODERATION_PROFANITY_MSG: str = "Sorry, the content involves profanity"
    TEXT_MODERATION_PULLINTRAFFIC_MSG: str = "Sorry, the content involves pullinTraffic"
    TEXT_MODERATION_REGIONAL_MSG: str = "Sorry, the content involves regional"
    TEXT_MODERATION_LABLES: list = ['violence', 'contraband', 'sexuality', 'profanity', 'pullinTraffic', 'regional']
    TEXT_MODERATION_DICT: dict = {"violence": TEXT_MODERATION_VIOLENCE_MSG,
                                  'contraband': TEXT_MODERATION_CONTRABAND_MSG,
                                  'sexuality': TEXT_MODERATION_SEXUALITY_MSG,
                                  'profanity': TEXT_MODERATION_PROFANITY_MSG,
                                  'pullinTraffic': TEXT_MODERATION_PULLINTRAFFIC_MSG,
                                  'regional': TEXT_MODERATION_REGIONAL_MSG}
    #大模型输入检测
    LLM_QUERY_MODERATION_LABELS: list = ['pornographic_adult', 'sexual_terms', 'sexual_suggestive', 'sexual_prompts',
                                         'political_figure', 'political_entity', 'political_n', 'political_p', 'political_prompts', 'political_a',
                                         'violent_extremists', 'violent_incidents', 'violent_weapons', 'violent_prompts',
                                         'contraband_drug', 'contraband_gambling', 'contraband_act', 'contraband_entity',
                                         'inappropriate_discrimination', 'inappropriate_ethics','customized',
                                         'inappropriate_profanity', 'inappropriate_oral', 'inappropriate_superstition', 'inappropriate_nonsense',
                                         'privacy_p', 'privacy_b',
                                         'religion_b', 'religion_t', 'religion_c', 'religion_i', 'religion_h',
                                         'pt_to_sites', 'pt_by_recruitment', 'pt_to_contact']
    LLM_QUERY_MODERATION_HIGH_LEVELS_LABELS: list = ['pornographic_adult', 'sexual_terms', 'sexual_suggestive', 'sexual_prompts',
                                         'political_figure', 'political_entity', 'political_n', 'political_p', 'political_prompts', 'political_a',
                                         'violent_extremists', 'violent_incidents', 'violent_weapons', 'violent_prompts',
                                         'contraband_drug', 'contraband_gambling', 'contraband_act', 'contraband_entity', 'inappropriate_discrimination','inappropriate_ethics','customized']
    LLM_QUERY_MODERATION_MID_LEVELS_LABELS: list = ['inappropriate_profanity', 'inappropriate_oral', 'inappropriate_superstition', 'inappropriate_nonsense',
                                         'privacy_p', 'privacy_b',
                                         'religion_b', 'religion_t', 'religion_c', 'religion_i', 'religion_h',
                                         'pt_to_sites', 'pt_by_recruitment', 'pt_to_contact']


    # --------------------------图片转表格----------------------------------------
    MATHPIX_PICTURE2TEXT_EXCEPTION: str = "120001"
    MATHPIX_PICTURE2TEXT_EXCEPTION_MSG: str = "mathpix picture to text exception"

    XML2MD_EXCEPTION: str = "120002"
    XML2MD_EXCEPTION_MSG: str = "fail to convert xml to md"

    GET_PIC_FAIL_EXCEPTION: str = "120003"
    GET_PIC_FAIL_EXCEPTION_MSG: str = "get pic fail exception"

    ZJALGO_PICTURE2TEXT_EXCEPTION: str = "120004"
    ZJALGO_PICTURE2TEXT_EXCEPTION_MSG: str = "zjalgo picture to text exception"

    # --------------------------文档解析----------------------------------------
    DOCUMENT_STRUCTURE_EXCEPTION: str = "130001"
    DOCUMENT_STRUCTURE_EXCEPTION_MSG: str = "document structure exception"

    DOCUMENT_EXTRACTION_EXCEPTION: str = "130002"
    DOCUMENT_EXTRACTION_EXCEPTION_MSG: str = "document extraction exception"

    # --------------------------数据可视化----------------------------------------
    DATA_VISUALIZATION_LINE_CHART_EXCEPTION: str = "140001"
    DATA_VISUALIZATION_LINE_CHART_EXCEPTION_MSG: str = "data visualization line chart exception"

    DATA_VISUALIZATION_BAR_CHART_EXCEPTION: str = "140002"
    DATA_VISUALIZATION_BAR_CHART_EXCEPTION_MSG: str = "data visualization bar chart exception"

    DATA_VISUALIZATION_MAP_SCATTER_PLOT_EXCEPTION: str = "140003"
    DATA_VISUALIZATION_MAP_SCATTER_PLOT_EXCEPTION_MSG: str = "data visualization map scatter plot exception"

    DATA_VISUALIZATION_STACKED_COLUMN_CHART_EXCEPTION: str = "140004"
    DATA_VISUALIZATION_STACKED_COLUMN_CHART_EXCEPTION_MSG: str = "data visualization stacked column chart exception"

    DATA_VISUALIZATION_LINE_CHART_WITH_CONFERENCE_INTERVAL_EXCEPTION: str = "140005"
    DATA_VISUALIZATION_LINE_CHART_WITH_CONFERENCE_INTERVAL_EXCEPTION_MSG: str = "data visualization line chart with conference interval exception"

    DATA_VISUALIZATION_HISTOGRAM_EXCEPTION: str = "140006"
    DATA_VISUALIZATION_HISTOGRAM_EXCEPTION_MSG: str = "data visualization histogram exception"

    DATA_VISUALIZATION_STEREOGRAPHIC_PROJECTION_EXCEPTION: str = "140007"
    DATA_VISUALIZATION_STEREOGRAPHIC_PROJECTION_EXCEPTION_MSG: str = "data visualization stereographic projection exception"



exception_constants = ExceptionConstants()
