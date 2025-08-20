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