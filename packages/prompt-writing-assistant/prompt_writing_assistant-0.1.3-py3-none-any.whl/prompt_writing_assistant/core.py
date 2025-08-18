'''
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-08-07 17:53:03
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-08-07 18:00:48
FilePath: /prompt_writing_assistant/src/prompt_writing_assistant/core.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

system_prompt = """
你是一个资深AI提示词工程师，具备卓越的Prompt设计与优化能力。
我将为你提供一段现有System Prompt。你的核心任务是基于这段Prompt进行修改，以实现我提出的特定目标和功能需求。
请你绝对严格地遵循以下原则：
 极端最小化修改原则（核心）：
 在满足所有功能需求的前提下，只进行我明确要求的修改。
 即使你认为有更“优化”、“清晰”或“简洁”的表达方式，只要我没有明确要求，也绝不允许进行任何未经指令的修改。
 目的就是尽可能地保留原有Prompt的字符和结构不变，除非我的功能要求必须改变。
 例如，如果我只要求你修改一个词，你就不应该修改整句话的结构。
 严格遵循我的指令：
 你必须精确地执行我提出的所有具体任务和要求。
 绝不允许自行添加任何超出指令范围的说明、角色扮演、约束条件或任何非我指令要求的内容。
 保持原有Prompt的风格和语调：
 尽可能地与现有Prompt的语言风格、正式程度和语调保持一致。
 不要改变不相关的句子或其表达方式。
 只提供修改后的Prompt：
 直接输出修改后的完整System Prompt文本。
 不要包含任何解释、说明或额外对话。
 在你开始之前，请务必确认你已理解并能绝对严格地遵守这些原则。任何未经明确指令的改动都将视为未能完成任务。

现有System Prompt:
{source_code}

功能需求:
{function_requirement}
"""

from llmada.core import BianXieAdapter

class EditPrompt:
    def __init__(self,py_path):
        self.py_path = py_path
        self.bx = BianXieAdapter()
        model_name = "gemini-2.5-flash-preview-05-20-nothinking"
        self.bx.model_pool.append(model_name)
        self.bx.set_model(model_name=model_name)

    def edit(self,function_requirement:str):
        # 最小改动代码原则
        with open(self.py_path,'r') as f:
            code = f.read()
        prompt = system_prompt.format(source_code=code,function_requirement=function_requirement)

        response = self.bx.product(prompt)
        with open(self.py_path,'w') as f:
            f.write(response)
        print(f"已保存到{self.py_path}")

    def get_prompt(self):
        with open(self.py_path,'r') as f:
            return f.read()