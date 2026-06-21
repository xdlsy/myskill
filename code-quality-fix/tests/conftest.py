import json
import os
import sys

# 让 scripts/ 可被导入，这样任意 cwd 下都能 `from cqf import ...`
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS_DIR))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    """从 tests/fixtures/ 加载 fixture 文件并返回解析后的内容。

    JSON fixture 返回解析后的对象；XML/文本 fixture 返回原始字符串。
    """
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if name.endswith(".json"):
        return json.loads(text)
    return text
