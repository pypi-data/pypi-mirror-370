from collections import OrderedDict
from typing import Optional
from agentlin.code_interpreter.types import Block
from agentlin.core.types import ContentData, ToolResult
import json


class ReferencableItem:
    def __init__(
        self,
        message_content: list[ContentData],
        block_list: list[Block],
        hash: str,
    ):
        self.message_content = message_content
        self.block_list = block_list
        self.hash = hash


def hash_block_list(block_list: list[Block]) -> str:
    """
    Generate a hash for the given block list.
    This is a placeholder implementation; replace with actual hashing logic.
    """
    return str(hash(json.dumps(block_list)))  # Simple hash based on tuple representation


class ReferenceManager:
    def __init__(self):
        self.number2reference: dict[int, ReferencableItem] = {}
        self.hash_id_to_reference_number: dict[str, int] = {}
        self.reference_number = 0

    def process_tool_result(self, tool_result: ToolResult) -> ToolResult:
        """
        Process a ToolResult and return the reference number if applicable.
        If the ToolResult contains message_content or block_list, it will be processed.

        Args:
            tool_result (ToolResult): The ToolResult to process.
        Returns:
            ToolResult: The processed ToolResult with reference numbers assigned.
        """
        if not tool_result.message_content or not tool_result.block_list:
            return tool_result
        message_content = tool_result.message_content
        block_list = tool_result.block_list

        # 按照匹配 id 进行分组
        id_to_referencable_result = OrderedDict()  # 一定要持插入顺序
        # {
        #     "message_content": [],
        #     "block_list": [],
        #     "message_content_start_idx": None,
        #     "message_content_end_idx": None,
        # }
        for i, content in enumerate(message_content):
            if "id" in content:
                reference_id = content["id"]
                if reference_id not in id_to_referencable_result:
                    id_to_referencable_result[reference_id] = {
                        "message_content": [],
                        "block_list": [],
                        "message_content_start_idx": i,
                        "message_content_end_idx": None,
                    }
                # [start_idx, end_idx) so it always holds that: start_idx < end_idx
                id_to_referencable_result[reference_id]["message_content"].append(content)
                if i + 1 == len(message_content):
                    id_to_referencable_result[reference_id]["message_content_end_idx"] = i + 1
                elif i + 1 < len(message_content) and ("id" not in message_content[i + 1] or message_content[i + 1]["id"] != reference_id):
                    id_to_referencable_result[reference_id]["message_content_end_idx"] = i + 1
        for i, block in enumerate(block_list):
            if "id" in block:
                reference_id = block["id"]  # 这个id和message_content中的id对应
                id_to_referencable_result[reference_id]["block_list"].append(block)

        # print(id_to_referencable_result)
        # print(len(id_to_referencable_result))

        # 每个 id 生成一个 ReferencableItem 及其对应的 reference number
        # 匹配 id 是临时的，后面拿到 reference number 后会覆盖掉匹配 id
        id_to_number_start_end = {}
        for id, result in id_to_referencable_result.items():
            reference_number = self.assign_reference_number(result["message_content"], result["block_list"])
            for block in result["block_list"]:
                block["id"] = reference_number  # block 的 id 直接替换为 reference number
            # 在 message_content 中的内容前后插入 reference number
            message_content_start_idx = result["message_content_start_idx"]
            message_content_end_idx = result["message_content_end_idx"]
            assert message_content_start_idx is not None and message_content_end_idx is not None
            id_to_number_start_end[id] = (reference_number, message_content_start_idx, message_content_end_idx)
            # 如果在这里直接修改 message_content，会导致后续的索引计算出错
            # 所以在最后统一处理

        # print(id_to_number_start_end)

        # 处理 message_content 中的内容
        # 在每个 referencable result 前后插入 <referencable-result> 和 </referencable-result>，供模型使用
        new_message_content = []
        for i, content in enumerate(message_content):
            if "id" in content:
                reference_id = content["id"]
                reference_number, start_idx, end_idx = id_to_number_start_end[reference_id]
                if i == start_idx:
                    new_message_content.append(
                        {
                            "type": "text",
                            "text": f"<referencable-result>\nID: {reference_number}\n",
                            "id": reference_number,
                            "additional": True,
                        }
                    )
                content["id"] = reference_number  # 替换为 reference number
                new_message_content.append(content)
                if i + 1 == end_idx:
                    new_message_content.append(
                        {
                            "type": "text",
                            "text": f"</referencable-result>",
                            "id": reference_number,
                            "additional": True,
                        }
                    )
            else:
                new_message_content.append(content)

        return ToolResult(
            message_content=new_message_content,
            block_list=block_list,
            key=tool_result.key,
        )

    def assign_reference_number(self, message_content: list[ContentData], block_list: list[Block]) -> int:
        hash_id = hash_block_list(block_list)
        if hash_id in self.hash_id_to_reference_number:
            reference_number = self.hash_id_to_reference_number[hash_id]
            return reference_number
        item = ReferencableItem(
            message_content=message_content,
            block_list=block_list,
            hash=hash_id,
        )
        return self.add_reference(item)

    def add_reference(self, item: ReferencableItem) -> int:
        self.reference_number += 1
        self.number2reference[self.reference_number] = item
        self.hash_id_to_reference_number[item.hash] = self.reference_number
        return self.reference_number

    def get_reference(self, reference_id: int) -> Optional[ReferencableItem]:
        return self.number2reference.get(reference_id)

    def clear(self):
        self.number2reference.clear()
        self.hash_id_to_reference_number.clear()
        self.reference_number = 0

    def remove_by_hash(self, hash_id: str):
        reference_number = self.hash_id_to_reference_number.pop(hash_id, None)
        if reference_number is not None:
            return self.number2reference.pop(reference_number, None)
        return False

    def exist(self, reference_number: int) -> bool:
        return reference_number in self.number2reference

    def exist_by_hash(self, hash_id: str) -> bool:
        return hash_id in self.hash_id_to_reference_number


if __name__ == "__main__":
    # Example usage
    manager = ReferenceManager()
    tool_results = [
        ToolResult(
            message_content=[
                {"type": "text", "text": "This is a test message.", "id": 1},
                {"type": "text", "text": "Another message.", "id": 2},
            ],
            block_list=[
                {"type": "code", "code": "print('Hello World')", "id": 1},
                {"type": "image", "url": "http://example.com/image.png", "id": 2},
            ],
        ),
        ToolResult(
            message_content=[
                {"type": "text", "text": "This is another test message.", "id": 1},
                {"type": "text", "text": "Yet another message.", "id": 2},
            ],
            block_list=[
                {"type": "code", "code": "print('Hello Again')", "id": 1},
                {"type": "image", "url": "http://example.com/image2.png", "id": 2},
            ],
        ),
    ]
    result = ToolResult(
        message_content=[{"type": "text", "text": "This is a standalone message."}],
        block_list=[],
    )
    for item in tool_results:
        processed_result = manager.process_tool_result(item)
        result.extend_result(processed_result)
    from agentlin.core.agent_schema import content_to_text
    import json

    print("Processed Tool Result:")
    print(content_to_text(result.message_content))
    print("Block List:")
    print(json.dumps(result.block_list, indent=2))
