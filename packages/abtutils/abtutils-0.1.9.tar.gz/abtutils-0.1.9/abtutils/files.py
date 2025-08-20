import os
import json
from typing import Union, List, Dict, Any


def read_json_file(filename):
    # 获取当前文件所在目录的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接JSON文件的完整路径
    file_path = os.path.join(current_dir, filename)

    try:
        # 打开并读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            # 解析JSON数据
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return None
    except json.JSONDecodeError:
        print(f"错误：{filename} 不是有效的JSON文件")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None


def _ensure_directory_exists(file_path: str) -> None:
    """确保文件所在的目录存在，如果不存在则创建"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def save_text_data(content: Union[str, List[str]], dir_path: str, filename: str, ext: str = "txt") -> tuple[bool, str]:
    """
    保存文本数据到指定文件路径

    参数:
        content: 要保存的文本内容，可以是字符串或字符串列表
        dir_path: 保存文件的目录路径
        filename: 文件名（不含后缀）
        ext: 文件后缀名，默认为"txt"

    返回:
        一个元组，第一个元素是保存是否成功的布尔值，第二个元素是状态消息
    """
    # 验证输入类型
    if not isinstance(content, (str, list)):
        return False, "内容必须是字符串或字符串列表"

    if isinstance(content, list) and not all(isinstance(item, str) for item in content):
        return False, "列表内容必须全部是字符串"

    # 处理文件名和完整路径
    full_filename = f"{filename}.{ext}" if ext else filename
    file_path = os.path.join(dir_path, full_filename)

    try:
        # 确保目录存在
        _ensure_directory_exists(file_path)

        # 如果内容是列表，将其转换为换行分隔的字符串
        if isinstance(content, list):
            content = "\n".join(content)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        return True, f"文件已成功保存至: {file_path}"

    except Exception as e:
        return False, f"保存失败: {str(e)}"


def save_json_data(data: Union[Dict[Any, Any], List[Any]], dir_path: str, filename: str, ext: str = "json") -> tuple[
    bool, str]:
    """
    保存JSON数据到指定文件路径

    参数:
        data: 要保存的JSON数据（字典或列表）
        dir_path: 保存文件的目录路径
        filename: 文件名（不含后缀）
        ext: 文件后缀名，默认为"json"

    返回:
        一个元组，第一个元素是保存是否成功的布尔值，第二个元素是状态消息
    """
    # 验证输入类型
    if not isinstance(data, (dict, list)):
        return False, "JSON数据必须是字典或列表"

    # 处理文件名和完整路径
    full_filename = f"{filename}.{ext}" if ext else filename
    file_path = os.path.join(dir_path, full_filename)

    try:
        # 确保目录存在
        _ensure_directory_exists(file_path)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return True, f"文件已成功保存至: {file_path}"

    except Exception as e:
        return False, f"保存失败: {str(e)}"
