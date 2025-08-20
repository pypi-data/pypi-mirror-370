import json
import os


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


def save_text_data(content, filename, ext="txt"):
    """
    保存文本数据到文件

    参数:
        content: 要保存的文本内容，可以是字符串或字符串列表
        filename: 文件名（不含后缀）
        ext: 文件后缀，默认为"txt"
    """
    # 处理文件名和后缀
    full_filename = f"{filename}.{ext}" if ext else filename

    try:
        # 如果内容是列表，将其转换为换行分隔的字符串
        if isinstance(content, list):
            content = "\n".join(content)

        with open(full_filename, "w", encoding="utf-8") as file:
            file.write(content)
        return True, f"文件已成功保存至: {full_filename}"
    except Exception as e:
        return False, f"保存失败: {str(e)}"


def save_json_data(data, filename, ext="json"):
    """
    保存JSON数据到文件

    参数:
        data: 要保存的JSON数据（字典或列表）
        filename: 文件名（不含后缀）
        ext: 文件后缀，默认为"json"
    """
    # 处理文件名和后缀
    full_filename = f"{filename}.{ext}" if ext else filename

    try:
        with open(full_filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True, f"文件已成功保存至: {full_filename}"
    except Exception as e:
        return False, f"保存失败: {str(e)}"