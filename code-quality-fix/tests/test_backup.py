import os
import tempfile

from cqf.backup import backup_files, restore_backup, list_backed_up_files


def test_backup_copies_files_under_timestamp():
    root = tempfile.mkdtemp()
    src = os.path.join(root, "proj", "a.go")
    os.makedirs(os.path.dirname(src))
    with open(src, "w") as f:
        f.write("original")
    backup_root = os.path.join(root, "backups")

    bid = backup_files([src], backup_root, backup_id="20260614-120000", project_root=root)
    assert bid == "20260614-120000"
    backed = list_backed_up_files(backup_root, bid)
    assert os.path.join("proj", "a.go") in backed

    # 改动源文件后还原。
    with open(src, "w") as f:
        f.write("mutated")
    restore_backup(backup_root, bid, project_root=root)
    with open(src) as f:
        assert f.read() == "original"


def test_restore_is_idempotent_on_clean():
    root = tempfile.mkdtemp()
    backup_root = os.path.join(root, "backups")
    backup_files([], backup_root, backup_id="empty")
    # 还原空备份不应报错。
    restore_backup(backup_root, "empty", project_root=os.path.join(root, "proj"))
