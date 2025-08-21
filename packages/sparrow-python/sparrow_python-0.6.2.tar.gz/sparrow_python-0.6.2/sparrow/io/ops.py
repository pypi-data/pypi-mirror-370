from sparrow.path import rel_to_abs, ls
import pickle
from typing import Union, List, Dict
import shutil
import os
import yaml
import orjson


def rm(*file_pattern: str, rel=False):
    """Remove files or directories.
    Example:
    --------
        >>> rm("*.jpg", "*.png")
        >>> rm("*.jpg", "*.png", rel=True)
    """
    path_list = ls(".", *file_pattern, relp=rel, concat="extend")
    for file in path_list:
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file, ignore_errors=True)


def save(filename, data):
    import pickle

    with open(filename, "wb") as fw:
        pickle.dump(data, fw)


def load(filename):
    import pickle

    with open(filename, "rb") as fi:
        file = pickle.load(fi)
    return file


def json_load(filepath: str, rel=False, mode="rb"):
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        return orjson.loads(f.read())


def json_dump(
    data: Union[List, Dict], filepath: str, rel=False, indent_2=False, mode="wb"
):
    orjson_option = 0
    if indent_2:
        orjson_option = orjson.OPT_INDENT_2
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        f.write(orjson.dumps(data, option=orjson_option))


def jsonl_load(filepath: str, rel=False, mode="rb"):
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        return [orjson.loads(line.strip()) for line in f.readlines() if line.strip()]


def jsonl_dump(data: List[Dict], filepath: str, rel=False, mode="wb"):
    abs_path = rel_to_abs(filepath, parents=1) if rel else filepath
    with open(abs_path, mode=mode) as f:
        for item in data:
            f.write(orjson.dumps(item) + b"\n")


# 自定义多行字符串的显示方式，去除行尾空格
def str_presenter(dumper, data):
    """ """
    # 去除每一行的行尾空格
    data = "\n".join([line.rstrip() for line in data.splitlines()])
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# 添加自定义表示器
yaml.add_representer(str, str_presenter)


def yaml_dump(filepath, data, rel_path=False, mode="w"):
    """Yaml dump"""
    abs_path = rel_to_abs(filepath, parents=1) if rel_path else filepath

    with open(abs_path, mode=mode, encoding="utf-8") as fw:
        yaml.dump(
            data,
            fw,
            allow_unicode=True,
            indent=4,
            sort_keys=False,
            default_flow_style=False,
        )


def yaml_load(filepath, rel_path=False, mode="r"):
    import yaml

    abs_path = rel_to_abs(filepath, parents=1) if rel_path else filepath
    with open(abs_path, mode=mode, encoding="utf-8") as stream:
        content = yaml.safe_load(stream)
    return content


def split_file(file_path, chunk_size=1024 * 1024 * 1024):
    """将大文件分割成多个块。

    Args:
        file_path (str): 原始文件的路径。
        chunk_size (int): 每个块的大小（字节）。
    """
    with open(file_path, "rb") as f:
        chunk_number = 0
        while True:
            chunk = f.read(int(chunk_size))
            if not chunk:
                break
            with open(f"{file_path}_part_{chunk_number:03}", "wb") as chunk_file:
                chunk_file.write(chunk)
            chunk_number += 1


def join_files(input_prefix, input_dir, output_path=None):
    """将分割后的文件块拼接回一个文件。

    Args:
        input_prefix (str): 分割文件的前缀。
        output_path (str): 拼接后的文件路径。
    """
    import glob

    if output_path is None:
        output_path = os.path.join(input_dir, input_prefix)

    parts = sorted(glob.glob(f"{input_prefix}_part_*", root_dir=input_dir))
    with open(output_path, "wb") as output_file:
        for part in parts:
            with open(os.path.join(input_dir, part), "rb") as part_file:
                output_file.write(part_file.read())


def find_free_port():
    """Find a free port to use for the server."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
