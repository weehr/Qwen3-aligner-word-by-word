"""语种定义：区分字词之间有无空格的语言。

Qwen3-ForcedAligner 的文本处理逻辑：
- 中文/日文/韩文由模型自带的处理器分词；
- 其他语言按空格分词，空格语言之外的文字需要手动插入字间空格，
  否则整段文字会被当成一个 token。
"""

# 字词之间没有空格分隔的语言
NO_SPACE_LANGUAGES = {
    "Chinese",
    "Japanese",
    "Thai",
    "Lao",
    "Khmer",
    "Burmese",
    "Yi",
    "Balinese",
    "Javanese",
    "Naxi",
    "Cherokee",
    "Tai Nua",
}

# 字词之间有空格分隔的语言
SPACE_LANGUAGES = {
    "English",
    "German",
    "Dutch",
    "Swedish",
    "Danish",
    "Norwegian",
    "Icelandic",
    "Afrikaans",
    "French",
    "Spanish",
    "Portuguese",
    "Italian",
    "Romanian",
    "Catalan",
    "Russian",
    "Ukrainian",
    "Belarusian",
    "Polish",
    "Czech",
    "Croatian",
    "Serbian",
    "Lithuanian",
    "Latvian",
    "Welsh",
    "Irish",
    "Greek",
    "Persian",
    "Kurdish",
    "Hindi",
    "Urdu",
    "Bengali",
    "Tamil",
    "Kannada",
    "Finnish",
    "Hungarian",
    "Estonian",
    "Turkish",
    "Uyghur",
    "Kazakh",
    "Mongolian",
    "Arabic",
    "Hebrew",
    "Indonesian",
    "Vietnamese",
    "Georgian",
    "Korean",
    "Swahili",
}

# 显示名称 -> 模型使用的语言名称
LANGUAGE_LABELS = {
    "汉语 (Chinese)": "Chinese",
    "日语 (Japanese)": "Japanese",
    "泰语 (Thai)": "Thai",
    "老挝语 (Lao)": "Lao",
    "高棉语/柬埔寨语 (Khmer)": "Khmer",
    "缅甸语 (Burmese)": "Burmese",
    "彝语/诺苏彝语 (Yi)": "Yi",
    "巴厘语 (Balinese)": "Balinese",
    "爪哇语 (Javanese)": "Javanese",
    "纳西语 (Naxi)": "Naxi",
    "切罗基语 (Cherokee)": "Cherokee",
    "傣那语 (Tai Nua)": "Tai Nua",
    "英语 (English)": "English",
    "德语 (German)": "German",
    "荷兰语 (Dutch)": "Dutch",
    "瑞典语 (Swedish)": "Swedish",
    "丹麦语 (Danish)": "Danish",
    "挪威语 (Norwegian)": "Norwegian",
    "冰岛语 (Icelandic)": "Icelandic",
    "阿非利坎语 (Afrikaans)": "Afrikaans",
    "法语 (French)": "French",
    "西班牙语 (Spanish)": "Spanish",
    "葡萄牙语 (Portuguese)": "Portuguese",
    "意大利语 (Italian)": "Italian",
    "罗马尼亚语 (Romanian)": "Romanian",
    "加泰罗尼亚语 (Catalan)": "Catalan",
    "俄语 (Russian)": "Russian",
    "乌克兰语 (Ukrainian)": "Ukrainian",
    "白俄罗斯语 (Belarusian)": "Belarusian",
    "波兰语 (Polish)": "Polish",
    "捷克语 (Czech)": "Czech",
    "克罗地亚语 (Croatian)": "Croatian",
    "塞尔维亚语 (Serbian)": "Serbian",
    "立陶宛语 (Lithuanian)": "Lithuanian",
    "拉脱维亚语 (Latvian)": "Latvian",
    "威尔士语 (Welsh)": "Welsh",
    "爱尔兰语 (Irish)": "Irish",
    "现代希腊语 (Greek)": "Greek",
    "波斯语 (Persian)": "Persian",
    "库尔德语 (Kurdish)": "Kurdish",
    "印地语 (Hindi)": "Hindi",
    "乌尔都语 (Urdu)": "Urdu",
    "孟加拉语 (Bengali)": "Bengali",
    "泰米尔语 (Tamil)": "Tamil",
    "卡纳达语 (Kannada)": "Kannada",
    "芬兰语 (Finnish)": "Finnish",
    "匈牙利语 (Hungarian)": "Hungarian",
    "爱沙尼亚语 (Estonian)": "Estonian",
    "土耳其语 (Turkish)": "Turkish",
    "维吾尔语 (Uyghur)": "Uyghur",
    "哈萨克语 (Kazakh)": "Kazakh",
    "蒙古语 (Mongolian)": "Mongolian",
    "阿拉伯语 (Arabic)": "Arabic",
    "希伯来语 (Hebrew)": "Hebrew",
    "印尼语/马来语 (Indonesian/Malay)": "Indonesian",
    "越南语 (Vietnamese)": "Vietnamese",
    "格鲁吉亚语 (Georgian)": "Georgian",
    "韩语/朝鲜语 (Korean)": "Korean",
    "斯瓦希里语 (Swahili)": "Swahili",
}

LANGUAGE_CHOICES = list(LANGUAGE_LABELS.keys())

# 模型直接按字/词统计（而不是按空格分词）的语言
CHAR_MATCH_LANGUAGES = NO_SPACE_LANGUAGES | {"Korean"}

# 模型自带分词器、可以直接拼接的语言
MODEL_TOKENS_LANGUAGES = {"Chinese", "Japanese", "Korean"}


def is_no_space(language: str) -> bool:
    return language in NO_SPACE_LANGUAGES


def join_segments(language: str, segments: list[str]) -> str:
    """把分句重新拼成送入模型的完整文本。"""
    if language in MODEL_TOKENS_LANGUAGES:
        return "".join(segments)
    if language in NO_SPACE_LANGUAGES:
        # 泰语、老挝语等没有空格，逐字插入空格，让模型按字对齐。
        text = "".join(segments)
        return " ".join(ch for ch in text if not ch.isspace())
    return " ".join(segments)
