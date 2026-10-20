# -*- coding: utf-8 -*-
"""部署 Questioner 到用户日常刷题目录 D:/Program Files/Questioner。

同步规则（与项目约定一致）：
- 代码与题库可覆盖：index.html / serve.py / README.md / manual.md / LICENSE / vendor/ / question/
- userdata/ 不覆盖（保留用户进度、错题、收藏）

用法：python _work/deploy_questioner.py
"""
import os
import shutil
import sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = r"D:/Program Files/Questioner"

# 顶层需同步的项（其余一律不动，避免误删）
SYNC_ITEMS = [
    "index.html",
    "serve.py",
    "README.md",
    "manual.md",
    "LICENSE",
    "vendor",
    "question",
]
# 永不触碰
PROTECTED = {"userdata", ".git", "_work"}


def mirror_dir(src, dst):
    """递归镜像目录：复制新增/变更文件，删除目标中多余文件。"""
    os.makedirs(dst, exist_ok=True)
    src_names = set(os.listdir(src))
    for name in src_names:
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.isdir(s):
            mirror_dir(s, d)
        else:
            shutil.copy2(s, d)
    # 删除 dst 中 src 不存在的文件
    for name in os.listdir(dst):
        if name in PROTECTED:
            continue
        d = os.path.join(dst, name)
        s = os.path.join(src, name)
        if not os.path.exists(s):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)


def main():
    if not os.path.isdir(SRC):
        print("源目录不存在:", SRC)
        sys.exit(1)
    os.makedirs(DST, exist_ok=True)
    for item in SYNC_ITEMS:
        s = os.path.join(SRC, item)
        d = os.path.join(DST, item)
        if not os.path.exists(s):
            print("跳过（源缺失）:", item)
            continue
        if os.path.isdir(s):
            mirror_dir(s, d)
        else:
            shutil.copy2(s, d)
        print("已同步:", item)
    print("部署完成 ->", DST)
    print("（已保留 userdata/ 不变）")


if __name__ == "__main__":
    main()
