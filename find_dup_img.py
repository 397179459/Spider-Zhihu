import os
import hashlib

# 定义图片目录
image_dir = r'D:\个人资料\wlPersonFiles\wallpic'

# 计算文件的SHA256哈希值
def calculate_hash(file_path):
    with open(file_path, 'rb') as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

# 创建一个字典用于存放哈希值和对应的文件路径
hashes = {}

i = 1
# 遍历图片目录中的所有文件
for filename in os.listdir(image_dir):
    # print(i)
    # 获取文件的完整路径
    file_path = os.path.join(image_dir, filename)
    # 如果是文件（而不是目录）
    if os.path.isfile(file_path):
        # 计算文件的哈希值
        file_hash = calculate_hash(file_path)
        # 如果这个哈希值已经在字典中
        if file_hash in hashes:
            print(f"Duplicate: {file_path} and {hashes[file_hash]}")
        else:
            hashes[file_hash] = file_path
    i += 1
