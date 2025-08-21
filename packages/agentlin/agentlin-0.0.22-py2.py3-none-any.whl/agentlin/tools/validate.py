import json
from jsonschema import validate, ValidationError
from jsonschema import Draft202012Validator
from typing_extensions import Any, Dict



def validate_params(inputSchema: Dict[str, Any], options: Dict[str, Any]):
    validate(instance=options, schema=inputSchema)


def validate_tree_data(options: Dict[str, Any]) -> bool:
    """
    Validates the tree data to ensure node names are unique.

    Args:
        options: The tree data to validate.

    Returns:
        bool: True if the tree data is valid, False otherwise.

    Raises:
        ValidationError: If a node name is not unique.
    """
    names = set()

    def check_uniqueness(current_node: Dict[str, Any]) -> None:
        if current_node is None:
            return

        if current_node.get("name") is None:
            raise ValidationError("Invalid parameters: node name is missing.")

        if current_node["name"] in names:
            raise ValidationError(f"Invalid parameters: node name '{current_node['name']}' is not unique.")
        names.add(current_node["name"])

        if current_node.get("children"):
            for child in current_node["children"]:
                check_uniqueness(child)

    # 检查根节点
    if options.get("name") is None:
        raise ValidationError("Invalid parameters: root node name is missing.")

    check_uniqueness(options)
    return True


def validate_node_edge_data(data: Dict[str, Any]) -> bool:
    """
    Validates node and edge data.

    Args:
        data: A dictionary containing "nodes" and "edges" keys.
            - "nodes" is a list of dictionaries, each with a "name" key.
            - "edges" is a list of dictionaries, each with "source" and "target" keys.

    Returns:
        bool: True if the data is valid.

    Raises:
        ValidationError: If any of the validation checks fail.
    """
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Extract node names
    node_names = {node["name"] for node in nodes}

    # 1. Check for unique node names
    unique_node_names = set()
    for node in nodes:
        if "name" not in node:
            raise ValidationError("Invalid parameters: node name is missing.")
        if node["name"] in unique_node_names:
            raise ValidationError(f"Invalid parameters: nodes name '{node['name']}' is not unique.")
        unique_node_names.add(node["name"])

    # 2. Check if edge sources and targets exist in nodes
    for edge in edges:
        if "source" not in edge or "target" not in edge:
            raise ValidationError("Invalid parameters: edge source or target is missing.")
        if edge["source"] not in node_names:
            raise ValidationError(f"Invalid parameters: source '{edge['source']}' does not exist in nodes.")
        if edge["target"] not in node_names:
            raise ValidationError(f"Invalid parameters: target '{edge['target']}' does not exist in nodes.")

    # 3. Check if edge source-target pairs are unique
    edge_pairs = set()
    for edge in edges:
        pair = f"{edge['source']}-{edge['target']}"
        if pair in edge_pairs:
            raise ValidationError(f"Invalid parameters: edge pair '{pair}' is not unique.")
        edge_pairs.add(pair)

    return True


def validate_function_call_arguments(parameters_schema: Dict[str, Any], arguments_str: str) -> Dict[str, Any]:
    """
    验证 OpenAI function calling 返回的 arguments 是否符合 parameters schema。

    Args:
        parameters_schema: tools[x]["function"]["parameters"] 中的 JSON Schema dict
        arguments_str: 模型返回的 arguments（字符串形式）

    Returns:
        验证通过后的 Python dict
        None 为不通过
    """
    # 1. 解析 JSON
    try:
        arguments = json.loads(arguments_str)
    except json.JSONDecodeError as e:
        return None

    # 2. Schema 验证
    validator = Draft202012Validator(parameters_schema)
    errors = sorted(validator.iter_errors(arguments), key=lambda e: e.path)

    if errors:
        return None

    return arguments
