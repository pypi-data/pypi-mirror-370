import os
import sys
from pathlib import Path


def load_path():
    """
    向上查找 [config.py or pyproject.toml] 所在目录，并将其添加到 sys.path 中。
    """
    current_dir = Path(sys.modules.get("__main__").__file__).resolve().parent
    root_dir = None
    for parent in [current_dir, *current_dir.parents]:
        if (parent / "config.py").exists() or (parent / "pyproject.toml").exists():
            root_dir = parent
            break
    if root_dir is not None:
        root_path = str(root_dir)
        if sys.path[0] != root_path:
            sys.path.insert(0, root_path)
            print(f"[load_path] 添加路径到 sys.path: {root_path}")
    else:
        print("[load_path] 未找到 config.py 或 pyproject.toml，未修改 sys.path。")



def load_env(filepath='.env'):
    """
    从指定路径读取 .env 文件，并将变量加载到 os.environ 中。
    :param filepath: .env 文件路径，默认为当前目录下的 .env
    """
    if not os.path.isfile(filepath):
        return

    with open(filepath, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"\' ')