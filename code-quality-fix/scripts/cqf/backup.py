"""修复阶段的文件级快照，用于回滚。

备份存放在 {backup_root}/{backup_id}/ 下，镜像项目目录树。
backup_id 是调用方（scan.py / SKILL.md）提供的时间戳字符串。
"""

import os
import shutil


def _snapshot_dir(backup_root, backup_id):
    return os.path.join(backup_root, backup_id)


def backup_files(file_paths, backup_root, backup_id, project_root=None):
    """把每个文件拷到 {backup_root}/{backup_id}/{相对 project_root 的路径}。

    给出 project_root 时，路径相对它镜像，使 restore_backup(project_root=...)
    能写回原位置。project_root 为 None 时退化为按完整路径镜像（去掉前导分隔符）。
    返回 backup_id。
    """
    snap = _snapshot_dir(backup_root, backup_id)
    for path in file_paths:
        if not os.path.isfile(path):
            continue
        if project_root:
            rel = os.path.relpath(os.path.abspath(path), os.path.abspath(project_root))
        else:
            rel = path.lstrip(os.sep)
        dest = os.path.join(snap, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(path, dest)
    return backup_id


def list_backed_up_files(backup_root, backup_id):
    """返回快照中镜像的相对路径列表。"""
    snap = _snapshot_dir(backup_root, backup_id)
    result = []
    if not os.path.isdir(snap):
        return result
    for dirpath, _dirs, files in os.walk(snap):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, snap)
            result.append(rel)
    return result


def restore_backup(backup_root, backup_id, project_root=None):
    """把每个快照文件拷回其原始路径。

    若给出 project_root，相对镜像路径拼到其下；否则镜像路径（可能为绝对）原样使用。
    """
    for rel in list_backed_up_files(backup_root, backup_id):
        src = os.path.join(_snapshot_dir(backup_root, backup_id), rel)
        if project_root and not os.path.isabs(rel):
            dest = os.path.join(project_root, rel)
        else:
            dest = rel
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        shutil.copy2(src, dest)
