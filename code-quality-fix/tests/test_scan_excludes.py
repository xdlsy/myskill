"""扫描器排除参数构造的回归测试。

驱动 bug：bandit 不读 .gitignore，曾把本 skill 自己的备份目录
(.tmp/code-quality-fix/backups/...) 也扫进去，导致每轮扫描的问题数膨胀。
这些测试锁定 _repeated_excludes / _bandit_exclude_arg 的输出格式。
"""
import scan  # conftest 已把 scripts/ 加入 sys.path


def test_excluded_dirs_covers_noise_and_scratch():
    # 关键：必须覆盖 .tmp（本 skill 暂存目录）与常见构建/依赖目录。
    assert ".tmp" in scan.EXCLUDED_DIRS
    assert ".git" in scan.EXCLUDED_DIRS
    assert "target" in scan.EXCLUDED_DIRS
    assert "node_modules" in scan.EXCLUDED_DIRS


def test_repeated_excludes_one_flag_per_dir():
    out = scan._repeated_excludes("--extend-exclude")
    assert out == ["--extend-exclude", ".git",
                   "--extend-exclude", "node_modules",
                   "--extend-exclude", "vendor",
                   "--extend-exclude", ".tmp",
                   "--extend-exclude", "target"]


def test_bandit_exclude_is_single_x_with_glob_per_dir():
    out = scan._bandit_exclude_arg()
    # bandit -x 接逗号分隔 glob；*/<dir>/* 匹配任意层级的该目录。
    assert out[0] == "-x"
    assert out[1].count(",") == len(scan.EXCLUDED_DIRS) - 1
    assert "*/.tmp/*" in out[1]
    assert "*/target/*" in out[1]
