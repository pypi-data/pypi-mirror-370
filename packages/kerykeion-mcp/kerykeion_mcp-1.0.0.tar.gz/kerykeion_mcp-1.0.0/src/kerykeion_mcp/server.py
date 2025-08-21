#!/usr/bin/env python3
"""
Kerykeion MCP 服务器模块

处理 MCP 协议请求，提供占星计算服务
"""

import json
import sys
import os
import tempfile
from typing import Dict, Any

from .core import (
    create_astrological_subject,
    get_natal_aspects,
    get_synastry_aspects,
    create_composite_chart,
    get_current_time,
)


def setup_environment():
    """设置环境变量，避免缓存问题"""
    try:
        # 创建一个临时目录用于缓存
        temp_cache_dir = tempfile.mkdtemp(prefix="kerykeion_cache_")

        # 设置多个可能的缓存环境变量
        os.environ['KERYKEION_CACHE_DIR'] = temp_cache_dir
        os.environ['XDG_CACHE_HOME'] = temp_cache_dir
        os.environ['TMPDIR'] = temp_cache_dir
        os.environ['TMP'] = temp_cache_dir
        os.environ['TEMP'] = temp_cache_dir
        os.environ['HOME'] = temp_cache_dir  # 某些库可能使用HOME/.cache

        # 创建.cache子目录，因为某些库可能期望这个结构
        cache_subdir = os.path.join(temp_cache_dir, '.cache')
        os.makedirs(cache_subdir, exist_ok=True)

        # 设置Python的缓存目录
        os.environ['PYTHONUSERBASE'] = temp_cache_dir

    except Exception as e:
        # 如果无法创建临时目录，继续执行但可能会遇到缓存问题
        pass


def handle_initialize(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理初始化请求"""
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "kerykeion-mcp-server",
                "version": "1.0.0",
                "description": "Kerykeion 占星计算服务器 - 基于 Kerykeion 库"
            }
        }
    }


def handle_tools_list(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具列表请求"""
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "获取当前系统时间，返回详细的时间信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "create_astrological_subject",
                    "description": "创建占星主体对象并返回完整的占星数据，包含行星和宫位信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "姓名"
                            },
                            "year": {
                                "type": "integer",
                                "description": "出生年份"
                            },
                            "month": {
                                "type": "integer",
                                "description": "出生月份 (1-12)"
                            },
                            "day": {
                                "type": "integer",
                                "description": "出生日期 (1-31)"
                            },
                            "hour": {
                                "type": "integer",
                                "description": "出生小时 (0-23)"
                            },
                            "minute": {
                                "type": "integer",
                                "description": "出生分钟 (0-59)"
                            },
                            "city": {
                                "type": "string",
                                "description": "出生城市"
                            },
                            "nation": {
                                "type": "string",
                                "description": "国家代码 (如: US, GB, CN)"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "经度（可选，提供则不使用城市查询）"
                            },
                            "latitude": {
                                "type": "number",
                                "description": "纬度（可选，提供则不使用城市查询）"
                            },
                            "tz_str": {
                                "type": "string",
                                "description": "时区字符串（可选，如: Europe/Rome, America/New_York）"
                            },
                            "zodiac_type": {
                                "type": "string",
                                "description": "黄道类型",
                                "enum": ["Tropical", "Sidereal"]
                            },
                            "sidereal_mode": {
                                "type": "string",
                                "description": "恒星模式（当 zodiac_type 为 Sidereal 时使用）"
                            }
                        },
                        "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                    }
                },
                {
                    "name": "get_natal_aspects",
                    "description": "获取本命相位信息，分析个人星盘中行星之间的角度关系",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "姓名"},
                            "year": {"type": "integer", "description": "出生年份"},
                            "month": {"type": "integer", "description": "出生月份 (1-12)"},
                            "day": {"type": "integer", "description": "出生日期 (1-31)"},
                            "hour": {"type": "integer", "description": "出生小时 (0-23)"},
                            "minute": {"type": "integer", "description": "出生分钟 (0-59)"},
                            "city": {"type": "string", "description": "出生城市"},
                            "nation": {"type": "string", "description": "国家代码"},
                            "longitude": {"type": "number", "description": "经度（可选）"},
                            "latitude": {"type": "number", "description": "纬度（可选）"},
                            "tz_str": {"type": "string", "description": "时区字符串（可选）"}
                        },
                        "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                    }
                },
                {
                    "name": "get_synastry_aspects",
                    "description": "获取合盘相位信息，分析两个人星盘之间的相位关系",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "person1_data": {
                                "type": "object",
                                "description": "第一个人的出生信息",
                                "properties": {
                                    "name": {"type": "string"},
                                    "year": {"type": "integer"},
                                    "month": {"type": "integer"},
                                    "day": {"type": "integer"},
                                    "hour": {"type": "integer"},
                                    "minute": {"type": "integer"},
                                    "city": {"type": "string"},
                                    "nation": {"type": "string"},
                                    "longitude": {"type": "number"},
                                    "latitude": {"type": "number"},
                                    "tz_str": {"type": "string"}
                                },
                                "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                            },
                            "person2_data": {
                                "type": "object",
                                "description": "第二个人的出生信息",
                                "properties": {
                                    "name": {"type": "string"},
                                    "year": {"type": "integer"},
                                    "month": {"type": "integer"},
                                    "day": {"type": "integer"},
                                    "hour": {"type": "integer"},
                                    "minute": {"type": "integer"},
                                    "city": {"type": "string"},
                                    "nation": {"type": "string"},
                                    "longitude": {"type": "number"},
                                    "latitude": {"type": "number"},
                                    "tz_str": {"type": "string"}
                                },
                                "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                            }
                        },
                        "required": ["person1_data", "person2_data"]
                    }
                },
                {
                    "name": "create_composite_chart",
                    "description": "创建组合盘（中点合成盘），用于分析两个人的关系",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "person1_data": {
                                "type": "object",
                                "description": "第一个人的出生信息",
                                "properties": {
                                    "name": {"type": "string"},
                                    "year": {"type": "integer"},
                                    "month": {"type": "integer"},
                                    "day": {"type": "integer"},
                                    "hour": {"type": "integer"},
                                    "minute": {"type": "integer"},
                                    "city": {"type": "string"},
                                    "nation": {"type": "string"},
                                    "longitude": {"type": "number"},
                                    "latitude": {"type": "number"},
                                    "tz_str": {"type": "string"}
                                },
                                "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                            },
                            "person2_data": {
                                "type": "object",
                                "description": "第二个人的出生信息",
                                "properties": {
                                    "name": {"type": "string"},
                                    "year": {"type": "integer"},
                                    "month": {"type": "integer"},
                                    "day": {"type": "integer"},
                                    "hour": {"type": "integer"},
                                    "minute": {"type": "integer"},
                                    "city": {"type": "string"},
                                    "nation": {"type": "string"},
                                    "longitude": {"type": "number"},
                                    "latitude": {"type": "number"},
                                    "tz_str": {"type": "string"}
                                },
                                "required": ["name", "year", "month", "day", "hour", "minute", "city", "nation"]
                            }
                        },
                        "required": ["person1_data", "person2_data"]
                    }
                }
            ]
        }
    }


def handle_tools_call(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具调用请求"""
    params = request.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if tool_name == "get_current_time":
            result = get_current_time()
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False
                }
            }

        elif tool_name == "create_astrological_subject":
            result = create_astrological_subject(
                arguments.get("name"),
                arguments.get("year"),
                arguments.get("month"),
                arguments.get("day"),
                arguments.get("hour"),
                arguments.get("minute"),
                arguments.get("city"),
                arguments.get("nation"),
                arguments.get("longitude"),
                arguments.get("latitude"),
                arguments.get("tz_str"),
                arguments.get("zodiac_type", "Tropical"),
                arguments.get("sidereal_mode", "LAHIRI")
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False
                }
            }

        elif tool_name == "get_natal_aspects":
            result = get_natal_aspects(
                arguments.get("name"),
                arguments.get("year"),
                arguments.get("month"),
                arguments.get("day"),
                arguments.get("hour"),
                arguments.get("minute"),
                arguments.get("city"),
                arguments.get("nation"),
                arguments.get("longitude"),
                arguments.get("latitude"),
                arguments.get("tz_str")
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False
                }
            }

        elif tool_name == "get_synastry_aspects":
            result = get_synastry_aspects(
                arguments.get("person1_data"),
                arguments.get("person2_data")
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False
                }
            }

        elif tool_name == "create_composite_chart":
            result = create_composite_chart(
                arguments.get("person1_data"),
                arguments.get("person2_data")
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{"type": "text", "text": f"未知工具: {tool_name}"}],
                    "isError": True
                }
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [{"type": "text", "text": f"工具调用错误: {str(e)}"}],
                "isError": True
            }
        }


def main():
    """主函数 - 处理 MCP 请求"""
    # 设置环境
    setup_environment()

    # 读取标准输入
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")

            if method == "initialize":
                response = handle_initialize(request)
            elif method == "tools/list":
                response = handle_tools_list(request)
            elif method == "tools/call":
                response = handle_tools_call(request)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            # 输出响应
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()

        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }, ensure_ascii=False))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }, ensure_ascii=False))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
