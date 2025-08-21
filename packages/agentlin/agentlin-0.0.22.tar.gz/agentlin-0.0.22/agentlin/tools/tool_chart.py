import httpx

from agentlin.code_interpreter.chart_schema import *


DEFAULT_CHART_URL = "https://antv-studio.alipay.com/api/gpt-vis"

async def generate_chart_url(options: Dict[str, Any]) -> str:
    try:
        payload = {
            **options,
            "source": "dify-plugin-visualization",
        }
        headers = {
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(DEFAULT_CHART_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                raise ValueError(data.get("errorMessage", "Unknown error"))
            return data.get("resultObj", "")
    except httpx.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        raise
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

# 通用图表生成函数 - 实际实现
async def generate_chart(
    chart_type: ChartType,
    **options,
):
    """
    通用图表生成函数，根据chart_type参数生成不同类型的图表

    Args:
        chart_type: 图表类型，支持多种图表格式
        **options: 图表配置参数，根据不同图表类型有不同的参数要求

    Returns:
        生成的图表数据
    """
    # return await generate_chart_from_client(client, chart_type, **options)
    return await generate_chart_from_antv(chart_type, **options)


async def generate_chart_from_antv(
    chart_type: ChartType,
    **options,
):
    options["type"] = chart_type
    return await generate_chart_url(options)


from fastmcp import Client
async def generate_chart_from_client(
    client: Client,
    chart_type: ChartType,
    **options,
):
    """
    通用图表生成函数，根据chart_type参数生成不同类型的图表

    Args:
        chart_type: 图表类型，支持多种图表格式
        **options: 图表配置参数，根据不同图表类型有不同的参数要求

    Returns:
        生成的图表数据
    """
    # 图表类型到工具名称的映射
    CHART_TYPE_TO_TOOL = {
        "area": "generate_area_chart",
        "bar": "generate_bar_chart",
        "boxplot": "generate_boxplot_chart",
        "column": "generate_column_chart",
        "district_map": "generate_district_map",
        "dual_axes": "generate_dual_axes_chart",
        "fishbone": "generate_fishbone_diagram",
        "flow": "generate_flow_diagram",
        "funnel": "generate_funnel_chart",
        "histogram": "generate_histogram_chart",
        "line": "generate_line_chart",
        "liquid": "generate_liquid_chart",
        "mind_map": "generate_mind_map",
        "network": "generate_network_graph",
        "organization": "generate_organization_chart",
        "path_map": "generate_path_map",
        "pie": "generate_pie_chart",
        "pin_map": "generate_pin_map",
        "radar": "generate_radar_chart",
        "sankey": "generate_sankey_chart",
        "scatter": "generate_scatter_chart",
        "treemap": "generate_treemap_chart",
        "venn": "generate_venn_chart",
        "violin": "generate_violin_chart",
        "word_cloud": "generate_word_cloud_chart",
    }

    # 验证chart_type有效性
    if chart_type not in CHART_TYPE_TO_TOOL:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    # 获取对应的工具名称
    tool_name = CHART_TYPE_TO_TOOL[chart_type]

    # 创建客户端并调用工具
    async with client:
        return await client.call_tool(tool_name, options)
