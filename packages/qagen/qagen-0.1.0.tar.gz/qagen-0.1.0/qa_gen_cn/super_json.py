import json
import re
from typing import Any, List, Union

class SuperJSON(json.JSONDecoder):
    """
    超级JSON处理类，继承自标准库json模块，扩展loads方法：
    1. 能自动提取并解析字符串中所有合法的json子串。
    2. 能自动补全缺失的右侧大括号。
    3. 其余方法与标准json模块一致。
    """
    @classmethod
    def loads(cls, s: str, *args, **kwargs) -> Union[Any, List[Any]]:
        """
        扩展的loads方法：
        - 自动提取并解析字符串中的所有json子串。
        - 自动补全缺失的右侧大括号。
        - 如果只找到一个json对象，直接返回；多个则返回列表。
        """
        # 预清洗：去除噪声与常见格式问题
        s = cls._sanitize_llm_output(s)
        json_objs = []
        # 用栈算法提取最大外层JSON对象
        start = s.find('{')
        while start != -1:
            stack = []
            for i in range(start, len(s)):
                if s[i] == '{':
                    stack.append('{')
                elif s[i] == '}':
                    if stack:
                        stack.pop()
                    if not stack:
                        # 找到配对的最大JSON对象
                        json_str = s[start:i+1]
                        try:
                            obj = json.loads(json_str, *args, **kwargs)
                            json_objs.append(obj)
                        except json.JSONDecodeError:
                            # 尝试补全右侧大括号
                            fixed = cls._fix_braces(json_str)
                            try:
                                obj = json.loads(fixed, *args, **kwargs)
                                json_objs.append(obj)
                            except Exception:
                                pass
                        # 继续查找下一个
                        start = s.find('{', i+1)
                        break
            else:
                # 没有找到配对的右括号
                break
        if not json_objs:
            # 如果没找到json子串，尝试整体修复后解析
            try:
                fixed = cls._fix_braces(s)
                return json.loads(fixed, *args, **kwargs)
            except Exception:
                raise json.JSONDecodeError("无法解析为JSON", s, 0)
        if len(json_objs) == 1:
            return json_objs[0]
        return json_objs

    @staticmethod
    def _fix_braces(s: str) -> str:
        """
        检查并补全右侧大括号
        """
        left = s.count('{')
        right = s.count('}')
        if left > right:
            s = s + ('}' * (left - right))
        return s

    @staticmethod
    def _sanitize_llm_output(s: str) -> str:
        """
        对模型输出进行轻量清洗：
        - 移除 <think>...</think> 段落
        - 规范化智能引号为标准引号
        - 修正常见键名多引号错误，如 ""question": -> "question":
        - 移除对象/数组结尾处的多余逗号
        """
        # 移除 <think>... </think>
        s = re.sub(r"<think>[\s\S]*?</think>", "", s, flags=re.IGNORECASE)
        # 规范化引号
        s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        # 修正键名前的重复引号
        s = re.sub(r'""(\w+)"\s*:', r'"\1":', s)
        # 移除结尾处的多余逗号: ,}\n or ,]\n
        s = re.sub(r',\s*([}\]])', r'\1', s)
        return s

    # 其余方法直接继承json模块
    @classmethod
    def dumps(cls, obj, *args, **kwargs):
        return json.dumps(obj, *args, **kwargs)

    @classmethod
    def dump(cls, obj, fp, *args, **kwargs):
        return json.dump(obj, fp, *args, **kwargs)

    @classmethod
    def load(cls, fp, *args, **kwargs):
        return json.load(fp, *args, **kwargs) 


# 便捷函数，方便使用
def extract_json(s: str, *args, **kwargs) -> Any:
    """
    从字符串中提取JSON对象
    
    Args:
        s: 可能包含JSON的字符串
        
    Returns:
        提取的JSON对象
        
    Raises:
        json.JSONDecodeError: 如果无法从字符串中提取有效的JSON
    """
    return SuperJSON.loads(s, *args, **kwargs)

