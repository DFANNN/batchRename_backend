"""
    flask:flask框架，用于创建Web应用
    request：flask提供的模块，用于处理http请求
    jsonify:flask提供的模块，用于返回json响应
    flask_cors:用于处理cors问题的库
    psutil:
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psutil

# 创建一个flask应用实例
app = Flask(__name__)
# 启用cors跨域
CORS(app)


# 定义批量重命名函数
def batch_rename(path, old_substring, new_substring):

    # os.path.isdir:判断当前路径是否是一个目录，存在：True; 不存在：False
    if not os.path.isdir(path):
        return {"error": f"{path}  当前路径错误或不存在！"}

    # 返回path指定文件夹包含的文件名字的列表
    files = os.listdir(path)
    # 存储返回名字信息
    renamed_files = []

    for file in files:
        if old_substring in file:
            # 新的文件名字
            new_file_name = file.replace(old_substring, new_substring)
            # 旧文件名字的路径
            # os.path.join: 把目录和文件名合成一个路径
            old_name_path = os.path.join(path, file)
            new_name_path = os.path.join(path, new_file_name)

            try:
                os.rename(old_name_path, new_name_path)
                renamed_files.append({"old_name": file, "new_name": new_file_name})
            except Exception as e:
                return {"error": f"重命名失败 {file}: {e}"}
        else:
            return {"error": f"未找到包含 {old_substring} 的文件"}
    # 返回修改之后的信息
    return {"renamed_files": renamed_files}


# 重命名接口
@app.route("/rename-files", methods=["POST"])
def rename_files():
    data = request.json
    path = data.get("path")
    old_substring = data.get("old_substring")
    new_substring = data.get("new_substring")

    result = batch_rename(path, old_substring, new_substring)
    if "error" in result:
        res = {"code": 500, "data": None, "msg": result["error"]}
    else:
        res = {"code": 0, "data": result, "msg": "成功"}

    return jsonify(res)


# 获取本地磁盘接口
@app.route("/get-disk", methods=["GET"])
def get_disk():
    disks = psutil.disk_partitions()
    drives = [
        {"name": partition.device, "path": partition.device, "type": 1}
        for partition in disks
    ]

    res = {"code": 0, "data": drives, "msg": "成功"}
    return jsonify(res)


# 获取磁盘下的文件
def get_disk_file(path):
    try:
        # 获取指定路径下的所有文件和文件夹
        items = os.listdir(path)
        res = []
        for item in items:
            if os.path.isdir(os.path.join(path, item)):
                res.append({"name": item, "path": os.path.join(path, item), "type": 1})

        return res
    except Exception as e:
        return {"error": e}


@app.route("/current-disk-file", methods=["POST"])
def current_disk_file():
    data = request.json
    path = data.get("path")
    result = get_disk_file(path)
    res = {"code": 0, "data": result, "msg": "成功"}

    return jsonify(res)


# 根据路径返回当前文件夹下的文件
def read_path_files(path):
    files = os.listdir(path)
    return files


@app.route("/path_files", methods=["POST"])
def path_files():
    data = request.json
    path = data.get("path")
    result = read_path_files(path)
    res = {"code": 0, "data": result, "msg": "成功"}

    return jsonify(res)


# 在最后添加文件
def insertion_text_last(name, insertion):
    # 找到最后一个分隔符
    name_index = name.rfind(".")

    if name_index == -1:
        return insertion + insertion

    return name[:name_index] + insertion + name[name_index:]


# 修改文件名（插入文本的方式）
def rename_insertion(path, rule_type, text: str):
    if not os.path.isdir(path):
        return {"error": f"{path}  当前路径错误或不存在！"}

    # 存储返回名字信息
    renamed_files = []

    files = os.listdir(path)
    for file in files:

        if rule_type == "1":
            new_file_name = text + file
        else:
            new_file_name = insertion_text_last(file, text)

        old_name_path = os.path.join(path, file)
        new_name_path = os.path.join(path, new_file_name)

        try:
            os.rename(old_name_path, new_name_path)
            renamed_files.append({"old_name": file, "new_name": new_file_name})
        except Exception as e:
            return {"error": f"重命名失败{file}: {e}"}

    return {"renamed_files": renamed_files}


@app.route("/batch-rename-insertion", methods=["POST"])
def batch_rename_insertion():
    data = request.json
    path = data.get("path")
    rule_type = data.get("type")
    text = data.get("text")

    result = rename_insertion(path, rule_type, text)
    if "error" in result:
        res = {"code": 500, "data": None, "msg": result["error"]}
    else:
        res = {"code": 0, "data": result, "msg": "成功"}

    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=False)
