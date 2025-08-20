import json
import logging
import os
from collections import OrderedDict, defaultdict

import requests


def get_notes(path: str = '', format: str = 'application/json', server: str = 'http://192.168.1.23:27123') -> str:
    """使用Local REST API插件；取回单个note或文件夹下note名列表

    Args:
        path (str, optional): 如果给定的是文件夹（需要以`/`结尾）则返回的是文件夹下所有note名列表；如果给定的是note文件名，则返回note内容. Defaults to ''.
        format: 默认是`application/json`。可以修改成`application/vnd.olrapi.note+json`
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        str: _description_
    """
    headers = {
        'accept': format,
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
    }

    response = requests.get(f'{server}/vault/{path}', headers=headers)
    return response.text


def get_note_frontmatter(note_content: str):
    """解析笔记的frontmatter"""
    import yaml

    frontmatter = {}
    if note_content.startswith("---\n"):
        try:
            frontmatter = yaml.safe_load(note_content.split("---\n")[1])
        except yaml.YAMLError as e:
            print(f"解析frontmatter失败: {e}")
    return frontmatter


def insert_content_to_note(
        path: str,
        content: str,
        heading_place: str,
        content_insert_position: str = 'beginning',
        server: str = 'http://192.168.1.23:27123'
):
    """在指定位置（heading区分）插入内容，heading是必须的，如果没有heading的note，不能使用此方法

    Args:
        path (str): _description_
        heading_place (str): 如果是多级heading → `level_1_heading::level_2_heading`
        content_insert_position (str): ['beginning', 'end']
        content (str, optional): 
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        _type_: _description_
    """
    headers = {
        'accept': '*/*',
        'Heading': heading_place,
        'Content-Insertion-Position': content_insert_position,
        'Heading-Boundary': '::',
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
        'Content-Type': 'text/markdown',
    }

    response = requests.patch(f'{server}/vault/{path}', headers=headers, data=content)
    return response


def update_note(
        path: str,
        content: str,
        server: str = 'http://192.168.1.23:27123'
):
    """更新内容到给定的note文件上，如果给定的note文件名不存在，则新建note，如果存在则**清空内容更新**

    Args:
        path (str): _description_
        content (str): _description_
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        _type_: _description_
    """
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
        'Content-Type': 'text/markdown',
    }

    response = requests.put(f'{server}/vault/{path}', headers=headers, data=content)
    return response


def delete_note(
        path: str,
        server: str = 'http://192.168.1.23:27123'
):
    """删除给定的note文件

    Args:
        path (str): _description_
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        _type_: _description_
    """
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
    }

    response = requests.put(f'{server}/vault/{path}', headers=headers)
    return response


def append_content_to_note(
        path: str,
        content: str,
        server: str = 'http://192.168.1.23:27123'
):
    """将给定内容附加到给定的note文件末尾，如果给定的note文件名不存在，则新建note

    Args:
        path (str): _description_
        content (str): _description_
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        _type_: _description_
    """
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
        'Content-Type': 'text/markdown',
    }

    response = requests.post(f'{server}/vault/{path}', headers=headers, data=content)
    return response


def search_note_name_by_dql(
        query: str,
        server: str = 'http://192.168.1.23:27123'
):
    """通过DQL语句查询note列表

    Args:
        query (str): 类似在OB中使用dataview查询TABLE(不能使用LIST)
        server (_type_, optional): _description_. Defaults to 'http://192.168.1.23:27123'.

    Returns:
        _type_: _description_
    """
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer 0db9f1c1d4ad38c2d3d03377ba7513bb90613191db72ed2fd1af5f47be32d8f7',
        'Content-Type': 'application/vnd.olrapi.dataview.dql+txt',
    }

    response = requests.post(f'{server}/search/', headers=headers, data=query)
    return response


def remove_frontmatter_property(folder_path: str, property_name: str):
    """给定的文件夹中所有后缀为.md的文件，删除frontmatter信息中给定的property

    Args:
        folder_path (str): _description_
        property_name (str): _description_
    """
    import yaml

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r+') as f:
                content = f.read()
                try:
                    _, frontmatter, body = content.split("---\n", 2)
                    frontmatter_dict = yaml.safe_load(frontmatter)
                    frontmatter_dict.pop(property_name)
                    updated_frontmatter = yaml.dump(frontmatter_dict, sort_keys=False,
                                                    default_flow_style=False, allow_unicode=True)
                    f.seek(0)
                    f.write("---\n{}\n---\n{}".format(updated_frontmatter, body))
                except yaml.YAMLError as exc:
                    logging.error(f"Error parsing YAML in {filename}: {exc}")
                except ValueError:
                    logging.error(f"File {filename} does not appear to have a frontmatter.")


def add_frontmatter_property(
        folder_path: str, before_property: str, property_name: str, default_value: str = ""):
    """给定的文件夹中所有后缀为.md的文件，在frontmatter信息中的before_property属性之前插入新属性

    Args:
        folder_path (str): _description_
        before_property (str): _description_
        property_name (str): _description_
        default_value (str, optional): _description_. Defaults to "".
    """
    import yaml

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r+') as f:
                content = f.read()
                try:
                    _, frontmatter, body = content.split("---\n", 2)
                    frontmatter_dict = yaml.safe_load(frontmatter)
                    # 将字典转换为 OrderedDict
                    ordered_dict = OrderedDict(frontmatter_dict)
                    # 创建一个新的 OrderedDict，并将 "Related" 插入到指定位置
                    new_ordered_dict = OrderedDict()
                    for key, value in ordered_dict.items():
                        if key == before_property:
                            new_ordered_dict[property_name] = default_value
                        new_ordered_dict[key] = value
                    updated_frontmatter = yaml.dump(
                        dict(new_ordered_dict),
                        sort_keys=False, default_flow_style=False, allow_unicode=True)
                    f.seek(0)
                    f.write("---\n{}\n---\n{}".format(updated_frontmatter, body))
                except yaml.YAMLError as exc:
                    logging.error(f"Error parsing YAML in {filename}: {exc}")
                except ValueError:
                    logging.error(f"File {filename} does not appear to have a frontmatter.")


def append_tag_frontmatter_property(folder_path: str, tag: str) -> None:
    import yaml

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r+') as f:
                content = f.read()
                try:
                    _, frontmatter, body = content.split("---\n", 2)
                    frontmatter_dict = yaml.safe_load(frontmatter)
                    tag_list = frontmatter_dict['tags']
                    if not tag_list:
                        tag_list = []
                    tag_list.append(tag)
                    frontmatter_dict['tags'] = tag_list
                    updated_frontmatter = yaml.dump(frontmatter_dict, sort_keys=False,
                                                    default_flow_style=False, allow_unicode=True)
                    f.seek(0)
                    f.write("---\n{}\n---\n{}".format(updated_frontmatter, body))
                except yaml.YAMLError as exc:
                    logging.error(f"Error parsing YAML in {filename}: {exc}")
                except ValueError:
                    logging.error(f"File {filename} does not appear to have a frontmatter.")


def print_note_tree(folder: str, root_note: str):
    """打印给定文件夹下的笔记树

    Args:
        folder (str): 文件夹路径
        root_note (str): 根笔记名
    """

    def print_tree(tree, node, level=0):
        """递归打印树状结构"""
        print("    " * level + "- [[" + node + "]]")
        for child in tree.get(node, []):
            print_tree(tree, child, level + 1)

    notes = json.loads(get_notes(f"{folder}/"))["files"]
    tree = defaultdict(list)

    # 首先构建父子关系
    for note in notes:
        content = get_notes(f"{folder}/{note}")
        frontmatter = get_note_frontmatter(content)
        parent = frontmatter.get("parent", "")
        if parent:
            parent_note = parent.strip("[]").split("|")[0]
            tree[parent_note].append(note.split('.md')[0])

    print_tree(tree, root_note)
