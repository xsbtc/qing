import re
import json

def parse_txt_to_json(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # 1. 核心修复：先彻底切掉底部的模版区域，只保留上方的数据部分
    main_content = full_content.split('====')[0]

    # 2. 按照编号（如 0001：）切分作品
    # 正则：匹配四位数字+冒号开头的行
    entries = re.split(r'\n(?=\d{4}[：:])', main_content)
    
    books = []

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
            
        book = {}
        
        # 提取编号 (ID)
        id_match = re.search(r'^(\d{4})', entry)
        if id_match:
            book['id'] = id_match.group(1)
        else:
            continue

        # 提取基础字段 (使用更宽容的正则，支持中文冒号和英文冒号)
        book['name'] = re.search(r'名称[：:](.*)', entry)
        book['author'] = re.search(r'作者[：:](.*)', entry)
        book['volumes_count'] = re.search(r'卷数[：:](.*)', entry)
        book['type'] = re.search(r'类型[：:](.*)', entry)
        book['category'] = re.search(r'类别[：:](.*)', entry)
        book['full_url'] = re.search(r'下载地址[：:]\n(https?://\S+)', entry)

        # 清洗基础字段数据
        for key in ['name', 'author', 'volumes_count', 'type', 'category', 'full_url']:
            if book[key]:
                book[key] = book[key].group(1).strip()
            else:
                book[key] = ""

        # 3. 提取分卷下载地址
        volumes = []
        if "分卷下载地址" in entry:
            # 兼容多种写法，截取分卷部分
            parts = re.split(r'分卷下载地址\(.*?\)[：:]|分卷下载地址[：:]', entry)
            if len(parts) > 1:
                volume_part = parts[1].strip()
                volume_lines = [line.strip() for line in volume_part.split('\n') if line.strip()]
                
                current_names = []
                for line in volume_lines:
                    if line.startswith('http'):
                        vol_name = " ".join(current_names) if current_names else "全集/分卷"
                        volumes.append({
                            "name": vol_name,
                            "url": line
                        })
                        current_names = []
                    else:
                        current_names.append(line)
        
        book['volumes'] = volumes
        books.append(book)

    # 4. 写入 JSON 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)
    
    print(f"成功！已处理 {len(books)} 本小说，第12本已包含在内。数据保存至 {output_path}")

if __name__ == "__main__":
    # 请确保文件名与您的本地文件名一致
    parse_txt_to_json('轻小说存储地址2.txt', 'data.json')
