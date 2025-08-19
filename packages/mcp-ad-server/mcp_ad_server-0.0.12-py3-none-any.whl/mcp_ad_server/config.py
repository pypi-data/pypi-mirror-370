"""
配置文件 - MCP服务器配置
"""

import os
from pathlib import Path

# 加载.env文件
try:
    from dotenv import load_dotenv

    # 从项目根目录加载.env文件
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    # 如果没有安装python-dotenv，继续使用系统环境变量
    pass


class Config:
    """MCP服务器配置类"""

    # 基础配置
    SERVER_NAME = "mcp-ad-server"

    # 版本信息
    try:
        from . import __api_client_version__, __version__

        SERVER_VERSION = __version__
        API_CLIENT_VERSION = __api_client_version__
    except ImportError:
        SERVER_VERSION = "0.0.0"
        API_CLIENT_VERSION = "0.0.0"

    # API配置
    BI_API_BASE_URL = "https://bi.dartou.com/testapi"
    BI_API_VERSION = "0.2.07"
    DEFAULT_APP = "正统三国"

    # 认证配置 - 从环境变量读取
    BI_API_TOKEN = os.getenv("BI_API_TOKEN", "")

    # 获取项目根目录（src/mcp_ad_server/config.py -> 项目根目录）
    BASE_DIR = Path(__file__).parent.parent.parent

    # 数据目录配置 - 支持打包后的环境
    @classmethod
    def get_data_dir(cls):
        """获取数据目录，支持打包和开发环境"""
        # 首先尝试从环境变量获取
        data_dir_env = os.getenv("MCP_AD_DATA_DIR")
        if data_dir_env:
            return Path(data_dir_env)

        # 包内数据目录：优先使用包内的data目录
        package_data_dir = Path(__file__).parent / "data"
        if package_data_dir.exists():
            return package_data_dir

        # 开发环境：使用项目根目录的data目录
        dev_data_dir = cls.BASE_DIR / "data"
        if dev_data_dir.exists():
            return dev_data_dir

        # 打包环境：使用importlib.resources查找包内数据
        try:
            import importlib.resources as pkg_resources

            # 检查包内是否有data目录
            try:
                data_package = pkg_resources.files("mcp_ad_server") / "data"
                if data_package.is_dir():
                    return Path(str(data_package))
            except (AttributeError, FileNotFoundError):
                pass
        except ImportError:
            pass

        # 如果都不存在，返回包内路径（即使不存在）
        return package_data_dir

    # 限制配置
    MAX_TIME_RANGE_DAYS = 30
    QUERY_TIMEOUT_SECONDS = 30

    # 调试与并发控制（占位，暂不考虑）
    BI_DEBUG = os.getenv("BI_DEBUG", "False").lower() == "true"
    QUERY_STAGGER_SECONDS = float(os.getenv("QUERY_STAGGER_SECONDS", "0.05"))

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # StreamableHTTP配置
    HTTP_HOST = os.getenv("HTTP_HOST", "127.0.0.1")
    HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
    STREAMABLE_HTTP_PATH = os.getenv("STREAMABLE_HTTP_PATH", "/mcp")
    STATELESS_HTTP = os.getenv("STATELESS_HTTP", "False").lower() == "true"
    JSON_RESPONSE = os.getenv("JSON_RESPONSE", "False").lower() == "true"

    # 支持的游戏应用（中文名称）
    SUPPORTED_APPIDS = [
        "正统三国",
        "银河战舰",
        "开心十三张",
        "哈局成语大师",
        "我的仙门",
        "一起斗消乐",
        "大头大菠萝",
        "大头十三水",
        "大头斗地主",
    ]

    # 游戏类型映射：棋牌游戏（BI）- 根据 GetAdCountList/supported_indicators.md
    CARD_GAME_APPIDS = {"48", "57", "62", "64"}

    # 游戏类型映射：非棋牌游戏（FX）- 根据 GetAdCountList/supported_indicators.md
    NON_CARD_GAME_APPIDS = {
        "59",
        "61",
        "65",
        "67",
        "68",
        "69",
        "72",
        "73",
        "74",
        "75",
        "78",
        "80",
        "81",
        "82",
    }

    # 支持的媒体渠道（中文显示名称）
    SUPPORTED_MEDIA = [
        "全选",
        "广点通",
        "今日头条",
        "百度",
        "百度搜索",
        "B站",
        "知乎",
        "UC",
        "抖小广告量",
        "视频号达人",
        "星图",
        "谷歌",
        "自然量",
    ]

    # 支持的投手列表（中文姓名）
    SUPPORTED_TOUSHOU = [
        "李霖林",
        "戴呈翔",
        "尹欣然",
        "施逸风",
        "郭耀月",
        "张鹏",
        "宗梦男",
        "fx2.0",  # 保持英文原样
    ]

    # 支持的广告状态（中文状态描述）
    SUPPORTED_AD_STATUS = [
        "已冻结",
        "暂停中",
        "已删除",
        "广告未到投放时间",
        "投放中",
        "账户余额不足",
        "广告达到日预算上限",
        "投放结束",
    ]

    # 支持的制作人列表 (素材查询)
    SUPPORTED_PRODUCERS = [
        "蔡睿韬",
        "王子鹏",
        "颜隆隆",
        "郑显洋",
        "李霖林",
        "张鹏",
        "谢雨",
        "占雪涵",
        "方晓聪",
        "刘伍攀",
        "张航",
        "刘锦",
        "翁国峻",
        "刘婷婷",
        "张泽祖",
        "AI",
        "戴呈翔",
        "其他",
    ]

    # 支持的创意人列表 (素材查询)
    SUPPORTED_CREATIVE_USERS = [
        "蔡睿韬",
        "陈朝晖",
        "王子鹏",
        "颜隆隆",
        "郑显洋",
        "李霖林",
        "张鹏",
        "谢雨",
        "周义骅",
        "占雪涵",
        "方晓聪",
        "陈朝辉",
        "刘伍攀",
        "张航",
        "郭耀月",
        "宗梦男",
        "刘锦",
        "翁国峻",
        "刘婷婷",
        "秦翎丰",
        "张泽祖",
        "戴呈翔",
        "AI",
        "其他",
    ]

    # 支持的素材类型
    SUPPORTED_MATERIAL_TYPES = ["图片", "视频"]

    # 支持的分组维度（中文显示名称）
    SUPPORTED_GROUP_KEYS = [
        "广告ID",
        "项目ID",
        "创意ID",
        "投手",
        "self_cid",  # 保持英文原样
        "媒体",
    ]

    # 参数值映射表 - 中文显示名称到API参数值的映射

    # 游戏应用映射（中文 -> 数字ID）
    APP_MAPPING = {
        "正统三国": "59",
        "银河战舰": "61",
        "开心十三张": "48",
        "哈局成语大师": "78",
        "我的仙门": "67",
        "一起斗消乐": "65",
        "大头大菠萝": "64",
        "大头十三水": "62",
        "大头斗地主": "57",
    }

    # 分组维度映射（中文 -> API字段）
    GROUP_KEY_MAPPING = {
        "广告ID": "vp_campaign_id",
        "项目ID": "vp_adgroup_id",
        "创意ID": "vp_originality_id",
        "投手": "vp_advert_pitcher_id",
        "self_cid": "dt_vp_fx_cid",  # 保持英文原样
        "媒体": "vp_advert_channame",
    }

    # 媒体渠道映射（中文 -> API代码）
    MEDIA_MAPPING = {
        "全选": "全选",
        "广点通": "gdt",
        "今日头条": "tt",
        "百度": "bd",
        "百度搜索": "bdss",
        "B站": "bz",
        "知乎": "zh",
        "UC": "uc",
        "抖小广告量": "dx",
        "视频号达人": "sphdr",
        "星图": "xt",
        "谷歌": "gg",
        "自然量": "nature",
    }

    # 投手映射（中文 -> API代码）
    MEDIA_BUYERS_MAPPING = {
        "李霖林": "lll",
        "戴呈翔": "dcx",
        "尹欣然": "yxr",
        "施逸风": "syf",
        "郭耀月": "gyy",
        "张鹏": "zp",
        "宗梦男": "zmn",
        "fx2.0": "fx2.0",  # 保持英文原样
    }

    # 广告状态映射（中文 -> API状态码）
    AD_STATUSES_MAPPING = {
        "已冻结": "ADGROUP_STATUS_FROZEN",
        "暂停中": "ADGROUP_STATUS_SUSPEND",
        "已删除": "ADGROUP_STATUS_DELETED",
        "广告未到投放时间": "ADGROUP_STATUS_NOT_IN_DELIVERY_TIME",
        "投放中": "ADGROUP_STATUS_ACTIVE",
        "账户余额不足": "ADGROUP_STATUS_ACCOUNT_BALANCE_NOT_ENOUGH",
        "广告达到日预算上限": "ADGROUP_STATUS_DAILY_BUDGET_REACHED",
        "投放结束": "ADGROUP_STATUS_STOP",
    }

    # 业务场景映射
    SCENARIO_MAPPING = {
        "投放启动": "1_投放启动决策指标组",
        "效果监控": "2_投放效果实时监控指标组",
        "短期评估": "3_短期价值评估指标组(首日-7日)",
        "深度分析": "4_深度价值与留存指标组",
        "数据对账": "5_平台数据对账指标组",
        "风险预警": "6_终止决策预警指标组",
        "财务核算": "7_财务核算指标组",
    }

    # 中文游戏名到游戏类型的映射（用于indicator_manager验证）
    @classmethod
    def get_type_by_app(cls, app_name: str) -> str:
        """根据中文游戏名或数字ID获取游戏类型（支持向后兼容）"""
        app_id = None

        # 检查是否是中文游戏名
        if app_name in cls.APP_MAPPING:
            app_id = cls.APP_MAPPING[app_name]
        # 检查是否是数字ID（向后兼容）
        elif app_name in cls.APP_MAPPING.values():
            app_id = app_name
        else:
            # 既不是中文名也不是有效的数字ID
            supported_apps = list(cls.APP_MAPPING.keys())
            raise ValueError(f"不支持的游戏: {app_name}，支持的游戏: {supported_apps}")

        # 根据英文ID判断游戏类型
        if app_id in cls.CARD_GAME_APPIDS:
            return "card_games"
        elif app_id in cls.NON_CARD_GAME_APPIDS:
            return "non_card_games"
        else:
            raise ValueError(f"游戏 {app_name} (ID: {app_id}) 未分配游戏类型")


# 在类外初始化数据目录
_config = Config()
DATA_DIR = _config.get_data_dir()
INDICATORS_DIR = DATA_DIR / "indicators"
GROUPS_DIR = DATA_DIR / "groups"
PROPMAP_DIR = DATA_DIR / "propmap"
GAMES_DIR = DATA_DIR / "games"

# 将路径添加到Config类
Config.DATA_DIR = DATA_DIR
Config.INDICATORS_DIR = INDICATORS_DIR
Config.GROUPS_DIR = GROUPS_DIR
Config.PROPMAP_DIR = PROPMAP_DIR
Config.GAMES_DIR = GAMES_DIR
