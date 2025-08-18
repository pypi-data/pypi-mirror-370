from pathlib import Path
from typing import List, Optional
from nonebot import get_plugin_config, require
import shutil

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from pydantic import BaseModel

# 插件目录（开发时的资源位置）
PLUGIN_DIR = Path(__file__).parent

# 使用 localstore 管理资源目录
DATA_DIR = store.get_plugin_data_dir() / "arcaea_sticker"
RESOURCE_DIR = DATA_DIR / "img"
FONT_DIR = DATA_DIR / "fonts"

# 初始化资源文件
def init_plugin_resources():
    """初始化插件资源文件"""
    # 创建必要的目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    FONT_DIR.mkdir(parents=True, exist_ok=True)

    # 复制开发目录下的资源文件到数据目录
    dev_resource_dir = PLUGIN_DIR / "img"
    dev_font_dir = PLUGIN_DIR / "fonts"

    if dev_resource_dir.exists():
        for file in dev_resource_dir.glob("*"):
            if not (RESOURCE_DIR / file.name).exists():
                shutil.copy2(file, RESOURCE_DIR)

    if dev_font_dir.exists():
        for file in dev_font_dir.glob("*"):
            if not (FONT_DIR / file.name).exists():
                shutil.copy2(file, FONT_DIR)

# 在模块加载时初始化资源
init_plugin_resources()

# 角色ID映射表
CHARACTER_ID_MAP = {
    "luna": "12",
    "aichan": "1",
    "ayu": "2",
    "eto": "3",
    "hikari": "4",
    "hikari2": "5",
    "ilith": "6",
    "insight": "7",
    "kanae": "8",
    "kou": "9",
    "lagrange": "10",
    "lethe": "11",
    "maya": "13",
    "nami": "14",
    "nonoka": "15",
    "saya": "16",
    "shirabe": "17",
    "shirahime": "18",
    "tairitsu": "19",
    "tairitsu2": "20",
    "tairitsu3": "21",
    "vita": "22",
    "ai酱": "1",
    "彩梦": "2",
    "爱托": "3",
    "光": "4",
    "光光": "4",
    "光2": "5",
    "光光2": "5",
    "依利丝": "6",
    "洞烛": "7",
    "群愿": "8",
    "红": "9",
    "红红": "9",
    "拉格兰": "10",
    "忘却": "11",
    "露娜": "12",
    "摩耶": "13",
    "奈美": "14",
    "野乃香": "15",
    "咲弥": "16",
    "白姬": "18",
    "对立": "19",
    "病女": "20",
    "病女对立": "20",
    "对立2": "20",
    "对立3": "21",
    "风暴对立": "21",
    "猫对立": "21",
    "维塔": "22",
}

# 角色颜色配置
CHARACTER_COLORS = {
    "ayu": {"fill": "#3BEADF", "stroke": "#30bbb2"},      # 彩梦：青色系
    "eto": {"fill": "#79cfe8", "stroke": "#0b8eb7"},      # 爱托：蓝色系
    "hikari": {"fill": "#ffe7b5", "stroke": "#ef7d04"},   # 光：橙色系
    "hikari2": {"fill": "#ffe7b5", "stroke": "#ef7d04"},  # 光2：同上
    "ilith": {"fill": "#f58194", "stroke": "#c61632"},    # 依利丝：红色系
    "kou": {"fill": "#ffd5d5", "stroke": "#f04f87"},      # 红：粉色系
    "lagrange": {"fill": "#bbd7fa", "stroke": "#4c8cdd"}, # 拉格兰：蓝色系
    "luna": {"fill": "#c09edd", "stroke": "#7743a3"},     # 露娜：紫色系
    "maya": {"fill": "#E8B088", "stroke": "#C17F59"},     # 摩耶：橙褐色系
    "nami": {"fill": "#f9c2cb", "stroke": "#f62f51"},     # 奈美：粉色系
    "shirahime": {"fill": "#c3d5ff", "stroke": "#657ae7"},# 白姬：淡蓝色系
    "shirabe": {"fill": "#e5616d", "stroke": "#974149"},  # shirabe：红色系
    "tairitsu": {"fill": "#80e8d5", "stroke": "#329f8c"}, # 对立：青色系
    "tairitsu2": {"fill": "#80e8d5", "stroke": "#329f8c"},# 对立2：同上
    "tairitsu3": {"fill": "#80e8d5", "stroke": "#329f8c"},# 对立3：同上
    "vita": {"fill": "#f58194", "stroke": "#c81c38"},     # 维塔：红色系
    "kanae": {"fill": "#fbd0ad", "stroke": "#FFB87F"},    # 群愿：橙色系
    "saya": {"fill": "#80e8d5", "stroke": "#329f8c"},     # 咲弥：青色系
    "lethe": {"fill": "#F6D3C2", "stroke": "#E3BAA7"},    # 忘却：米色系
    "insight": {"fill": "#C9CBEA", "stroke": "#a8a9c3"},  # 洞烛：淡紫色系
    "aichan": {"fill": "#CDB4E8", "stroke": "#a28fb6"},   # ai酱：紫色系
    "nonoka": {"fill": "#eee1af", "stroke": "#beb48c"},   # 野乃香：黄色系
}

# 默认颜色
DEFAULT_COLORS = {
    "fill": "#ffffff",
    "stroke": "#ffffff"
}

class Config(BaseModel):
    """插件配置"""
    arcaea_reply: bool = True  # 是否回复消息

# 获取配置
plugin_config = get_plugin_config(Config)