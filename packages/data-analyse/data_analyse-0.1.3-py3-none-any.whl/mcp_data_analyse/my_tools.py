import os
import sys

import pandas as pd
from typing import Dict, Any,List, Optional
import asyncio
import matplotlib.pyplot as plt
from mcp.types import TextContent
import json

async def data_overview(data_path: str) -> list[TextContent]:
    """
    获取数据文件的大概情况，包括表头信息、字段类型和数据条数等

    参数:
        data_path (str): 数据文件路径，支持.csv|.xlsx|.xls格式

    返回:
        Dict[str, Any]: 包含数据概况的字典，结构如下:
            {
                "file_path": str,         # 文件路径
                "file_type": str,         # 文件类型(csv/excel)
                "headers": List[str],     # 表头列表
                "dtypes": Dict[str, str], # 字段类型映射
                "row_count": int,         # 数据条数
                "column_count": int,      # 字段数量
                "sample_data": List[Dict] # 前5条样例数据(可选)
            }
    """
    try:
        # 读取数据文件
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
            file_type = 'csv'
        elif data_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data_path)
            file_type = 'excel'
        else:
            return [TextContent(type="text", text="不支持的文件格式，仅支持.csv/.xlsx/.xls")]

        # 获取数据概况
        overview = {
            "file_path": data_path,
            "file_type": file_type,
            "headers": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "sample_data": df.head().to_dict('records')  # 前5条数据作为样例
        }

        return [TextContent(type="text", text=json.dumps(overview))]

    except Exception as e:
        res= {
            "error": str(e),
            "message": f"处理文件{data_path}时出错"
        }
        return [TextContent(type="text", text=json.dumps(res))]

async def visualize_data(
        data_path: str,
        index: List[str],
        values: List[str],
        aggfunc: str = "sum",
        output_dir: str = "./output"
) -> list[TextContent]:
    """
    通过数据透视的方式可视化数据

    参数说明:
        data_path: 数据文件路径（支持.csv|.xlsx|.xls格式）
        index: 数据透视的索引列名列表（1-2维度）
        values: 需要聚合的数值列名列表
        aggfunc: 聚合函数（sum/mean/count/max/min/median/std/var，默认sum）
        output_dir: 图表保存目录（默认./output）
    """
    # ---------------------- 1. 读取数据 ----------------------
    # 检查文件格式并读取数据
    file_ext = os.path.splitext(data_path)[1].lower()
    if file_ext == ".csv":
        df = pd.read_csv(data_path)
    elif file_ext in [".xlsx", ".xls"]:
        df = pd.read_excel(data_path)
    else:
        return [TextContent(type="text",text=f"不支持的文件格式: {file_ext}，仅支持.csv|.xlsx|.xls")]

    # 检查索引和数值列是否存在
    missing_index = [col for col in index if col not in df.columns]
    missing_values = [col for col in values if col not in df.columns]
    if missing_index:
        return [TextContent(type="text", text=f"数据中不存在索引列: {missing_index}")]
    if missing_values:
        return [TextContent(type="text", text=f"数据中不存在数值列: {missing_values}")]

        # 检查索引维度（1-2维）
    if len(index) not in [1, 2]:
        return [TextContent(type="text", text=f"索引列数量必须为1或2，当前为{len(index)}")]

        # ---------------------- 2. 生成数据透视表 ----------------------
    # 定义聚合函数映射（pandas支持的聚合方法）
    aggfunc_map = {
        "sum": "sum",
        "mean": "mean",
        "count": "count",
        "max": "max",
        "min": "min",
        "median": "median",
        "std": "std",
        "var": "var"
    }
    if aggfunc not in aggfunc_map:
        return [TextContent(type="text", text=f"不支持的聚合函数: {aggfunc}，可选值: {list(aggfunc_map.keys())}")]

    # 生成透视表
    pivot_table = pd.pivot_table(
        data=df,
        index=index,
        values=values,
        aggfunc=aggfunc_map[aggfunc],
        fill_value=0  # 缺失值填充为0
    )

    # ---------------------- 3. 创建输出目录 ----------------------
    os.makedirs(output_dir, exist_ok=True)  # 若目录不存在则创建

    # ---------------------- 4. 可视化并保存图表 ----------------------
    # 设置中文字体（避免中文乱码）
    plt.rcParams["font.family"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 根据索引维度选择可视化方式
    if len(index) == 1:  # 1维索引：柱状图
        for value_col in values:
            plt.figure(figsize=(10, 6))
            pivot_table[value_col].plot(kind="bar", color="skyblue", edgecolor="black")

            # 添加标题和标签
            plt.title(f"{aggfunc}({value_col})  by {index[0]}", fontsize=15)
            plt.xlabel(index[0], fontsize=12)
            plt.ylabel(f"{aggfunc}({value_col})", fontsize=12)
            plt.xticks(rotation=45, ha="right")  # x轴标签旋转45度
            plt.tight_layout()  # 自动调整布局

            # 保存图表
            save_path = os.path.join(output_dir, f"{value_col}_by_{index[0]}_{aggfunc}.png")
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"图表保存成功: {save_path}")

    else:  # 2维索引：热力图（矩阵形式）
        for value_col in values:
            plt.figure(figsize=(12, 8))
            # 提取当前数值列的透视表（行：index[0]，列：index[1]）
            heatmap_data = pivot_table[value_col].unstack().fillna(0)
            # 绘制热力图
            im = plt.imshow(heatmap_data, cmap="YlGnBu")

            # 添加标签和标题
            plt.title(f"{aggfunc}({value_col})  by {index[0]} & {index[1]}", fontsize=15)
            plt.xlabel(index[1], fontsize=12)
            plt.ylabel(index[0], fontsize=12)

            # 设置坐标轴刻度（显示索引名称）
            plt.xticks(ticks=range(len(heatmap_data.columns)), labels=heatmap_data.columns, rotation=45, ha="right")
            plt.yticks(ticks=range(len(heatmap_data.index)), labels=heatmap_data.index)

            # 添加颜色条和数值标签
            plt.colorbar(im, label=f"{aggfunc}({value_col})")
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    plt.text(j, i, f"{heatmap_data.iloc[i, j]:.2f}",
                             ha="center", va="center", color="black")

            plt.tight_layout()
            # 保存图表
            save_path = os.path.join(output_dir, f"{value_col}_by_{index[0]}_{index[1]}_{aggfunc}.png")
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"图表保存成功: {save_path}")
    return [TextContent(type="text", text=f"所有图表已保存至目录: {os.path.abspath(output_dir)}")]

async  def data_summary(data_path)->list[TextContent]:
    """
    获取数据的汇总分析情况，包括描述性统计量（平均值、中位数、方差等）

    参数:
        data_path (str): 数据文件路径，支持 .csv|.xlsx|.xls 格式

    返回:
        dict: 包含数据基本信息和描述性统计的字典
    """
    # 检查文件是否存在
    if not os.path.exists(data_path):
        return [TextContent(type="text", text=f"文件不存在: {data_path}")]

        # 获取文件扩展名
    file_ext = os.path.splitext(data_path)[1].lower()

    # 根据文件类型读取数据
    try:
        if file_ext == '.csv':
            df = pd.read_csv(data_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(data_path)
        else:
            return [TextContent(type="text", text=f"不支持的文件格式: {file_ext}，仅支持 .csv|.xlsx|.xls")]

    except Exception as e:
        return [TextContent(type="text", text=f"读取文件失败: {str(e)}")]

        # 生成基本信息
    basic_info = {
        "样本量": len(df),
        "特征数": len(df.columns),
        "数值型特征": df.select_dtypes(include=['number']).columns.tolist(),
        "分类型特征": df.select_dtypes(include=['object', 'category']).columns.tolist(),
        "缺失值统计": df.isnull().sum().to_dict()
    }

    # 生成描述性统计（仅数值型特征）
    numeric_df = df.select_dtypes(include=['number'])
    if numeric_df.empty:
        stats = {}
    else:
        # 计算扩展统计量（默认统计量 + 偏度、峰度）
        stats_df = numeric_df.describe(percentiles=[0.25, 0.5, 0.75], include='all').T
        stats_df['方差'] = numeric_df.var()
        stats_df['偏度'] = numeric_df.skew()
        stats_df['峰度'] = numeric_df.kurt()
        stats = stats_df.round(4).to_dict('index')

        # 整合结果
    result = {
        "基本信息": basic_info,
        "数值型特征统计": stats
    }

    return  [TextContent(type="text", text=json.dumps(result))]


# # ------------------------------
# # 示例用法
# # ------------------------------
# if __name__ == "__main__":
#     try:
#         # 替换为实际数据文件路径
#         summary = data_summary("example_data.csv")
#
#         # 打印基本信息
#         print("===== 数据基本信息 =====")
#         for key, value in summary["基本信息"].items():
#             print(f"{key}: {value}")
#
#             # 打印数值型特征统计
#         print("\n===== 数值型特征统计 =====")
#         for col, stats in summary["数值型特征统计"].items():
#             print(f"\n【{col}】")
#             for stat_name, value in stats.items():
#                 print(f"  {stat_name}: {value}")
#     except Exception as e:
#         print(f"错误: {str(e)}")


if __name__ == "__main__":

    async def main():
        # res = await  data_overview("./sales.xlsx")
        # print(res)

        # result = await data_summary("./sales.xlsx")
        # print(result)

        res = await visualize_data("./sales.xlsx",['客户城市'],values=['销售量','销售额'])
        print(res)

    asyncio.run(main())
