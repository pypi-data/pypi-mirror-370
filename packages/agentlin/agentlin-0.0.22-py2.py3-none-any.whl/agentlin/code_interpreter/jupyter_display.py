import json
from typing_extensions import Any, Union, Optional, Dict
from loguru import logger
import pandas as pd
import numpy as np

from agentlin.code_interpreter.types import MIME_TABLE_V1, MIME_TABLE_V2
from agentlin.code_interpreter.data_to_table_json import (
    TABLE_TYPE,
    data_to_dataframe,
    dataframe_to_markdown,
    dataframe_to_table_json,
    query_data_to_table_json,
)

# Try to import IPython components
try:
    from IPython.display import display
    from IPython.core.display import DisplayObject
    IPYTHON_AVAILABLE = True
except ImportError:
    # Create dummy classes for non-IPython environments
    class DisplayObject:
        def __init__(self, *args, **kwargs):
            pass

    def display(obj):
        """Fallback display function for non-IPython environments"""
        if hasattr(obj, '_repr_mimebundle_'):
            bundle = obj._repr_mimebundle_()
            if 'text/plain' in bundle:
                print(bundle['text/plain'])
            else:
                print(str(obj))
        else:
            print(str(obj))

    IPYTHON_AVAILABLE = False

# Try to import polars if available
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False


def _generate_fallback_text_to_mimebundle(data: Any, mimebundle: dict) -> None:
    """
    Generate fallback text representation

    Args:
        data: Original data object

    Returns:
        str: Text representation
    """
    repr_func_list = [
        ("_repr_html_", "text/html"),
        ("_repr_pretty_", "text/plain"),
        ("_repr_text_", "text/plain"),
        ("_repr_json_", "application/json"),
        ("_repr_markdown_", "text/markdown"),
        ("_repr_svg_", "image/svg+xml"),
        ("_repr_latex_", "text/latex"),
        ("_repr_javascript_", "application/javascript"),
        ("_repr_png_", "image/png"),
        ("_repr_jpeg_", "image/jpeg"),
        ("_repr_gif_", "image/gif"),
    ]
    for func, mime_type in repr_func_list:
        if mime_type not in mimebundle and hasattr(data, func):
            try:
                value = getattr(data, func)()
                if value:
                    mimebundle[mime_type] = value
            except Exception:
                continue
    if not mimebundle:
        # If no specific representation found, use str representation
        if isinstance(data, DisplayObject):
            mimebundle["text/plain"] = str(data)
        else:
            # Fallback to string representation for non-DisplayObject types
            if hasattr(data, '__str__'):
                mimebundle["text/plain"] = data.__str__()
            else:
                # If no __str__ method, use repr
                mimebundle["text/plain"] = repr(data)


def create_mimebundle(data: TABLE_TYPE, include=None, exclude=None) -> Dict[str, Any]:
    """
    Create MIME bundle for any supported data type

    Args:
        data: The data object to convert

    Returns:
        Dict: MIME bundle with custom table format
    """
    mimebundle = {}
    logger.info("Creating MIME bundle for data")
    try:
        # Convert data to table JSON format
        if not isinstance(data, pd.DataFrame):
            data = data_to_dataframe(data)
        query_data = None
        if hasattr(data, '_query_data_') and data._query_data_:
            logger.info("Data has query data, converting to table JSON")
            query_data = data._query_data_()
        if query_data:
            table_json = query_data_to_table_json(data, query_data)
            logger.info(f"Query data converted to table JSON: {table_json}")
            if table_json:
                logger.info("Creating MIME bundle for query data")
                mimebundle[MIME_TABLE_V1] = table_json
                text = dataframe_to_markdown(data, table_json=table_json, query_data=query_data)
                if query_data and "text" not in query_data:
                    query_data["text"] = text
                mimebundle["text/plain"] = text
                return mimebundle
        if MIME_TABLE_V1 not in mimebundle:
            logger.info("Converting DataFrame to table JSON")
            table_json = dataframe_to_table_json(data)
            logger.info(f"DataFrame converted to table JSON: {table_json}")
            if table_json:
                logger.info(f"Creating MIME bundle for DataFrame")
                mimebundle[MIME_TABLE_V2] = table_json
                text = dataframe_to_markdown(data, table_json=table_json, query_data=query_data)
                mimebundle["text/plain"] = text
                if query_data and "text" not in query_data:
                    query_data["text"] = text
                return mimebundle
    except Exception as e:
        # Fallback to plain text representation if conversion fails
        logger.error(f"Failed to convert data to table JSON: {e}")
    logger.info("Generating fallback text representation")
    _generate_fallback_text_to_mimebundle(data, mimebundle)
    return mimebundle


class TableDisplay:
    """
    Custom display object for rendering tables in Jupyter notebooks
    using the custom MIME type 'application/vnd.aime.table.v1+json'
    """

    def __init__(self, data: Any):
        """
        Initialize TableDisplay with data

        Args:
            data: Any data type supported by data_to_table_json
        """
        self.data = data
        # Don't call super().__init__() to avoid inheritance issues

    def _repr_mimebundle_(self, include=None, exclude=None) -> Dict[str, Any]:
        """
        Return MIME bundle for Jupyter display

        Returns:
            Dict containing the custom MIME type and table JSON data
        """
        return create_mimebundle(self.data, include, exclude)


def display_table(data: Any) -> None:
    """
    Display data as a table in Jupyter notebook using custom MIME type

    Args:
        data: Any data type supported by data_to_table_json
    """
    display(TableDisplay(data))


class TableRenderer:
    """
    Custom renderer that replaces default _repr_ methods for supported data types
    """

    def __init__(self):
        self.original_reprs = {}
        self.installed = False

    def install(self):
        """
        Install custom _repr_ methods for all supported data types
        """
        if self.installed:
            return

        # Store original _repr_ methods
        self.original_reprs = {}

        # Replace pandas DataFrame _repr_mimebundle_
        if hasattr(pd.DataFrame, '_repr_mimebundle_'):
            self.original_reprs['pd.DataFrame._repr_mimebundle_'] = pd.DataFrame._repr_mimebundle_
        pd.DataFrame._repr_mimebundle_ = create_mimebundle

        # Replace pandas Series _repr_mimebundle_
        if hasattr(pd.Series, '_repr_mimebundle_'):
            self.original_reprs['pd.Series._repr_mimebundle_'] = pd.Series._repr_mimebundle_
        pd.Series._repr_mimebundle_ = create_mimebundle

        # Note: Cannot replace numpy ndarray _repr_mimebundle_ because it's immutable
        # Users need to use TableDisplay() manually for numpy arrays

        # Replace polars DataFrame and Series if available
        if POLARS_AVAILABLE and pl is not None:
            if hasattr(pl.DataFrame, '_repr_mimebundle_'):
                self.original_reprs['pl.DataFrame._repr_mimebundle_'] = pl.DataFrame._repr_mimebundle_
            pl.DataFrame._repr_mimebundle_ = create_mimebundle

            if hasattr(pl.Series, '_repr_mimebundle_'):
                self.original_reprs['pl.Series._repr_mimebundle_'] = pl.Series._repr_mimebundle_
            pl.Series._repr_mimebundle_ = create_mimebundle

        self.installed = True

    def uninstall(self):
        """
        Restore original _repr_ methods
        """
        if not self.installed:
            return

        # Restore pandas DataFrame
        if 'pd.DataFrame._repr_mimebundle_' in self.original_reprs:
            pd.DataFrame._repr_mimebundle_ = self.original_reprs['pd.DataFrame._repr_mimebundle_']
        elif hasattr(pd.DataFrame, '_repr_mimebundle_'):
            delattr(pd.DataFrame, '_repr_mimebundle_')

        # Restore pandas Series
        if 'pd.Series._repr_mimebundle_' in self.original_reprs:
            pd.Series._repr_mimebundle_ = self.original_reprs['pd.Series._repr_mimebundle_']
        elif hasattr(pd.Series, '_repr_mimebundle_'):
            delattr(pd.Series, '_repr_mimebundle_')

        # Note: numpy ndarray _repr_mimebundle_ cannot be modified, so no restoration needed

        # Restore polars types if available
        if POLARS_AVAILABLE and pl is not None:
            if 'pl.DataFrame._repr_mimebundle_' in self.original_reprs:
                pl.DataFrame._repr_mimebundle_ = self.original_reprs['pl.DataFrame._repr_mimebundle_']
            elif hasattr(pl.DataFrame, '_repr_mimebundle_'):
                delattr(pl.DataFrame, '_repr_mimebundle_')

            if 'pl.Series._repr_mimebundle_' in self.original_reprs:
                pl.Series._repr_mimebundle_ = self.original_reprs['pl.Series._repr_mimebundle_']
            elif hasattr(pl.Series, '_repr_mimebundle_'):
                delattr(pl.Series, '_repr_mimebundle_')

        self.installed = False


# Global renderer instance
_renderer = TableRenderer()


def enable_table_display():
    """
    Enable custom table display for supported data types in Jupyter

    Note: numpy arrays cannot be automatically replaced due to immutability.
    Use display_table() or TableDisplay() manually for numpy arrays.
    """
    _renderer.install()
    print("Custom table display enabled for:")
    print("- pandas DataFrame and Series")
    print("- list of dictionaries")
    if POLARS_AVAILABLE:
        print("- polars DataFrame and Series")
    print("Note: For numpy arrays, use display_table() manually")


def disable_table_display():
    """
    Disable custom table display and restore original representations
    """
    _renderer.uninstall()
    print("Custom table display disabled. Original representations restored.")


def is_table_display_enabled() -> bool:
    """
    Check if custom table display is currently enabled

    Returns:
        bool: True if enabled, False otherwise
    """
    return _renderer.installed

