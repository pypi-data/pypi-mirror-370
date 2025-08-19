import json
import os
from collections import defaultdict

def split_openapi_file(input_file: str):
    # 读取原始 OpenAPI 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        api_doc = json.load(f)
    
    # 按路径前缀分组
    path_groups = defaultdict(dict)
    
    for path, methods in api_doc['paths'].items():
        # 获取第一级路径作为分组
        group = path.split('/')[1]
        path_groups[group][path] = methods
    
    # 基础模板
    base_doc = {
        "openapi": api_doc["openapi"],
        "info": api_doc["info"],
        "servers": api_doc["servers"],
        "components": api_doc["components"]
    }
    
    # 为每个分组创建单独的文件
    for group, paths in path_groups.items():
        group_doc = base_doc.copy()
        group_doc["paths"] = paths
        
        # 创建目录
        dir_path = f"src/mteam/{group}"
        os.makedirs(dir_path, exist_ok=True)
        
        # 写入文件
        output_file = f"{dir_path}/api.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(group_doc, f, indent=2, ensure_ascii=False)
        
        print(f"Created {output_file}")

if __name__ == "__main__":
    split_openapi_file("常规接口_OpenAPI.json") 