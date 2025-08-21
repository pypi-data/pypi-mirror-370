from typing_extensions import Literal, Union
import datetime

import pandas as pd


# 初始化中美节假日（可缓存）懒加载
us_holidays = None # US(categories=US.supported_categories)
cn_holidays = None # CN(categories=CN.supported_categories)


def format_datetime_with_holiday(
    dt: Union[datetime.datetime, str, pd.Series],
    language: Literal["zh", "en"] = "zh",
    with_time: bool = True,
    with_weekday: bool = True,
    with_holiday: bool = True,
) -> Union[str, pd.Series]:
    """
    格式化时间为中文日期+英文星期几，附带中美节假日信息。
    支持 datetime, str, pandas.Series 批处理。
    """
    language_dict = {
        "zh": {
            "weekday": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
            "holiday": "假期",
            "date_format": "%Y年%m月%d日",
            "time_format": "%H:%M:%S",
        },
        "en": {
            "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "holiday": "Holiday",
            "date_format": "%Y-%m-%d",
            "time_format": "%H:%M:%S",
        },
    }

    def _format_one(d: Union[datetime.datetime, str]) -> str:
        if isinstance(d, str):
            d = pd.to_datetime(d)

        formatted = d.strftime(language_dict[language]["date_format"])
        if with_time:
            formatted += " " + d.strftime(language_dict[language]["time_format"])
        if with_weekday:
            weekday_index = d.weekday()
            formatted += " " + language_dict[language]["weekday"][weekday_index]
        if not with_holiday:
            return formatted
        # 检查节假日
        global us_holidays, cn_holidays
        if not us_holidays or not cn_holidays:
            try:
                from holidays.countries import US, CN
            except ImportError:
                raise ImportError("请安装 'holidays' 库以支持节假日查询。可以使用 'pip install holidays' 安装。")
            us_holidays = US(categories=US.supported_categories)
            cn_holidays = CN(categories=CN.supported_categories)
        tags = []
        if d in cn_holidays:
            tags.append(f"🇨🇳 {cn_holidays[d]}")
        if d in us_holidays:
            tags.append(f"🇺🇸 {us_holidays[d]}")

        if tags:
            holiday_str = language_dict[language]["holiday"]
            formatted += f" - {holiday_str}: " + ", ".join(tags)
        return formatted

    if isinstance(dt, pd.Series):
        return dt.apply(_format_one)
    else:
        return _format_one(dt)



def format_timedelta(
    delta: datetime.timedelta,
    language: Literal["zh", "en"] = "zh",
) -> str:
    """
    将 timedelta 格式化为精简的中文可读字符串，省略零值单位，四舍五入到秒

    Args:
        delta: 待格式化的时间间隔
        language: 语言选择，支持 "zh" 和 "en"

    Returns:
        精简的中文时间字符串（如 "1天3小时5分" 或 "45秒"）
    """
    language_dict = {
        "zh": {
            "days": "天",
            "hours": "小时",
            "minutes": "分",
            "seconds": "秒",
        },
        "en": {
            "days": "days",
            "hours": "hours",
            "minutes": "minutes",
            "seconds": "seconds",
        },
    }
    # 处理负数时间（转为正数）
    delta = abs(delta)

    # 分解时间单位（四舍五入到秒）
    days = delta.days
    total_seconds = int(delta.total_seconds() + 0.5)  # 四舍五入到秒
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 构建结果列表，跳过零值单位
    parts = []
    if days > 0:
        parts.append(f"{days}{language_dict[language]['days']}")
    if hours > 0:
        parts.append(f"{hours}{language_dict[language]['hours']}")
    if minutes > 0:
        parts.append(f"{minutes}{language_dict[language]['minutes']}")
    if seconds > 0:
        parts.append(f"{seconds}{language_dict[language]['seconds']}")

    # 处理全零情况（如 timedelta(0)）
    return "".join(parts) if parts else f"0{language_dict[language]['seconds']}"
