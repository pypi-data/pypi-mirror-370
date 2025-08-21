from typing_extensions import List, Dict, Optional, Any, Literal, Union, TypedDict, overload


# 基础类型定义
ThemeType = Literal["default", "academy"]
NumberType = Union[int, float]
ChartType = Literal[
    "area",
    "bar",
    "boxplot",
    "column",
    "district_map",
    "dual_axes",
    "fishbone",
    "flow",
    "funnel",
    "histogram",
    "line",
    "liquid",
    "mind_map",
    "network",
    "organization",
    "path_map",
    "pie",
    "pin_map",
    "radar",
    "sankey",
    "scatter",
    "treemap",
    "venn",
    "violin",
    "word_cloud",
]


# 图表数据类型定义
class AreaChartData(TypedDict):
    time: str
    value: NumberType
    group: Optional[str]


class BarChartData(TypedDict):
    category: str
    value: NumberType
    group: Optional[str]


class BoxplotChartData(TypedDict):
    category: str
    value: NumberType
    group: Optional[str]


class ColumnChartData(TypedDict):
    category: str
    value: NumberType
    group: Optional[str]


class DistrictMapData(TypedDict):
    name: str
    style: Optional[Dict[str, str]]
    colors: Optional[List[str]]
    dataType: Optional[Literal["number", "enum"]]
    dataLabel: Optional[str]
    dataValue: Optional[str]
    dataValueUnit: Optional[str]
    showAllSubdistricts: bool
    subdistricts: Optional[List[Dict[str, Union[str, Dict[str, str]]]]]


class DualAxesChartSeries(TypedDict):
    type: Literal["column", "line"]
    data: List[NumberType]
    axisYTitle: str


class FishboneDiagramData(TypedDict):
    name: str
    children: List[Dict[str, Union[str, List[Any]]]]


class FlowDiagramData(TypedDict):
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]


class FunnelChartData(TypedDict):
    category: str
    value: NumberType


class HistogramChartData(TypedDict):
    data: List[NumberType]
    binNumber: Optional[NumberType]


class LineChartData(TypedDict):
    time: str
    value: NumberType
    group: Optional[str]


class LiquidChartData(TypedDict):
    percent: NumberType
    shape: Literal["circle", "rect", "pin", "triangle"]


class MindMapData(TypedDict):
    name: str
    children: List[Dict[str, Union[str, List[Any]]]]


class NetworkGraphData(TypedDict):
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]


class OrganizationChartData(TypedDict):
    name: str
    description: Optional[str]
    children: List[Dict[str, Union[str, List[Any]]]]


class PathMapData(TypedDict):
    data: List[str]


class PieChartData(TypedDict):
    category: str
    value: NumberType


class PinMapData(TypedDict):
    title: str
    data: List[str]
    markerPopup: Optional[Dict[str, Union[str, NumberType]]]


class RadarChartData(TypedDict):
    name: str
    value: NumberType
    group: Optional[str]


class SankeyChartData(TypedDict):
    source: str
    target: str
    value: NumberType


class ScatterChartData(TypedDict):
    x: NumberType
    y: NumberType


class TreemapChartData(TypedDict):
    name: str
    value: NumberType
    children: Optional[List[Dict[str, Union[str, NumberType, List[Any]]]]]


class VennChartData(TypedDict):
    label: str
    value: NumberType
    sets: List[str]


class ViolinChartData(TypedDict):
    category: str
    value: NumberType
    group: Optional[str]


class WordCloudChartData(TypedDict):
    text: str
    value: NumberType


# 通用图表生成函数 - 函数重载定义
@overload
async def generate_chart(
    chart_type: Literal["area"],
    *,
    data: List[AreaChartData],
    stack: bool = False,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["bar"],
    *,
    data: List[BarChartData],
    group: bool = False,
    stack: bool = True,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["boxplot"],
    *,
    data: List[BoxplotChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["column"],
    *,
    data: List[ColumnChartData],
    group: bool = True,
    stack: bool = False,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["district_map"],
    *,
    title: str,
    data: DistrictMapData,
    width: NumberType = 1600,
    height: NumberType = 1000,
): ...


@overload
async def generate_chart(
    chart_type: Literal["dual_axes"],
    *,
    categories: List[str],
    series: List[DualAxesChartSeries],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["fishbone"],
    *,
    data: FishboneDiagramData,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
): ...


@overload
async def generate_chart(
    chart_type: Literal["flow"],
    *,
    data: FlowDiagramData,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
): ...


@overload
async def generate_chart(
    chart_type: Literal["funnel"],
    *,
    data: List[FunnelChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["histogram"],
    *,
    data: List[NumberType],
    binNumber: Optional[NumberType] = None,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["line"],
    *,
    data: List[LineChartData],
    stack: bool = False,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["liquid"],
    *,
    percent: NumberType,
    shape: Literal["circle", "rect", "pin", "triangle"] = "circle",
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["mind_map"],
    *,
    data: MindMapData,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
): ...


@overload
async def generate_chart(
    chart_type: Literal["network"],
    *,
    data: NetworkGraphData,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
): ...


@overload
async def generate_chart(
    chart_type: Literal["organization"],
    *,
    data: OrganizationChartData,
    orient: Literal["horizontal", "vertical"] = "vertical",
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
): ...


@overload
async def generate_chart(
    chart_type: Literal["path_map"],
    *,
    title: str,
    data: List[PathMapData],
    width: NumberType = 1600,
    height: NumberType = 1000,
): ...


@overload
async def generate_chart(
    chart_type: Literal["pie"],
    *,
    data: List[PieChartData],
    innerRadius: NumberType = 0,
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["pin_map"],
    *,
    title: str,
    data: List[str],
    markerPopup: Optional[Dict[str, Union[str, NumberType]]] = None,
    width: NumberType = 1600,
    height: NumberType = 1000,
): ...


@overload
async def generate_chart(
    chart_type: Literal["radar"],
    *,
    data: List[RadarChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["sankey"],
    *,
    data: List[SankeyChartData],
    nodeAlign: Literal["left", "right", "justify", "center"] = "center",
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["scatter"],
    *,
    data: List[ScatterChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["treemap"],
    *,
    data: List[TreemapChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["venn"],
    *,
    data: List[VennChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["violin"],
    *,
    data: List[ViolinChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
    axisXTitle: str = "",
    axisYTitle: str = "",
): ...


@overload
async def generate_chart(
    chart_type: Literal["word_cloud"],
    *,
    data: List[WordCloudChartData],
    theme: ThemeType = "default",
    width: NumberType = 600,
    height: NumberType = 400,
    title: str = "",
): ...
