"""
AgentLin Core Module

This module provides the core functionality for the AgentLin framework,
including agent schemas, simulators, and type definitions.
"""

# Type definitions
from .types import ContentData, DialogData

# Core agent functionality
from .agent_schema import (
    # Main classes
    AgentCore,
    AgentState,

    # Data processing utilities
    temporal_dataframe_to_jsonlist,
    jsonlist_to_temporal_dataframe,
    dataframe_to_markdown,
    dataframe_to_json_str,

    # Text parsing utilities
    parse_actions,
    extract_action_block,
    extract_action,
    parse_text_with_apply,
    extract_apply_block,
    extract_apply,
    exist_apply,
    extract_tool_calls,
    extract_code,
    extract_code_block,
    extract_thought,
    extract_execution_result,
    extract_answer,
    remove_thoughts,
    remove_answer,
    remove_thoughts_in_messages,
    add_scale_bar_in_messages,
)

__all__ = [
    # Types
    "ContentData",
    "DialogData",

    # Core classes
    "AgentCore",
    "AgentState",

    # Data processing utilities
    "temporal_dataframe_to_jsonlist",
    "jsonlist_to_temporal_dataframe",
    "dataframe_to_markdown",
    "dataframe_to_json_str",

    # Text parsing utilities
    "parse_actions",
    "extract_action_block",
    "extract_action",
    "parse_text_with_apply",
    "extract_apply_block",
    "extract_apply",
    "exist_apply",
    "extract_tool_calls",
    "extract_code",
    "extract_code_block",
    "extract_thought",
    "extract_execution_result",
    "extract_answer",
    "remove_thoughts",
    "remove_answer",
    "remove_thoughts_in_messages",
    "add_scale_bar_in_messages",
]