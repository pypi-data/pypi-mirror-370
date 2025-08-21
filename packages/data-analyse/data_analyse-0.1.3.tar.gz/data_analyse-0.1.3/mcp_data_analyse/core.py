# 数据分析助手
"""
  使用mcp实现进行数据分析助手

  mcp的使用方式:
    类型: stdio
"""

from mcp.server import Server
from mcp import stdio_server
from mcp.types import Tool, TextContent

from .my_tools import data_overview,visualize_data,data_summary

class MyStdioServer(Server):

    def __init__(self, servername):
        super().__init__(servername)
        self._token = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

app = MyStdioServer("data_analyse")

# 定义工具调用
@app.call_tool()
async def call_tools(tool_name, arguments:dict)->list[TextContent]:

    if tool_name == "data_overview":
        return await data_overview(arguments['data_path'])

    """
    data_path: str,
    index: List[str],
    values: List[str],
    aggfunc: str = "sum",
    output_dir: str = "./output"
    """
    if tool_name == "visualize_data":
        return await visualize_data(arguments['data_path'], arguments['index'],arguments['values'],arguments.get('aggfunc',"sum"),arguments.get('output_dir',"./output"))

    if tool_name == "data_summary":
        return await data_summary(arguments['data_path'])

    return [TextContent(text=f"Not support tool {tool_name}",type="text")]

# 定义工具(会列出支持的所有工具)
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="data_overview",
            description="获取数据的大概情况，例如表头信息、表头对应的字段类型、数据条数等",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持.csv|.xlsx|.xls格式"
                    }
                },
                "required": ["data_path"]
            }
        ),
        Tool(
            name="visualize_data",
            description="通过数据透视的方式可视化数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持.csv|.xlsx|.xls格式"
                    },
                    "index": {
                        "type": "array",
                        "description": "数据透视的索引列名列表，支持1-2纬度，如['城市','季度']",
                        "items": {
                            "type": "string"
                        }
                    },
                    "values": {
                        "type": "array",
                        "description": "需要聚合的数值列名列表，如['销量','销售额']",
                        "items": {
                            "type": "string"
                        }
                    },
                    "aggfunc": {
                        "type": "string",
                        "description": "聚合函数，支持sum | mean | count | max | min | median | std | var，默认是sum"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "聚合图表的保存目录，默认./output"
                    }
                },
                "required": ["data_path", "index", "values"]
            }
        ),
        Tool(
            name="data_summary",
            description="获取数据的汇总分析情况，例如整体数据的平均值、中位数、方差等等",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持.csv|.xlsx|.xls格式"
                    }
                },
                "required": ["data_path"]
            }
        ),
    ]

async def mcp_stdio_server():
    # 异步启动mcp服务
    async def arun():
        async with  stdio_server() as stream:
            await  app.run(stream[0], stream[1], app.create_initialization_options())

    await arun()


