"""pquant 命令行工具。

该模块提供 `pquant new` 命令，用于在当前目录生成示例策略文件。
"""

import argparse
import shutil
from pathlib import Path
from importlib.resources import files, as_file


def create_from_template(dest_name: str, force: bool = False) -> Path:
    """复制模板策略文件。

    Args:
        dest_name: 目标文件名或相对路径。如果未提供 ``.py`` 后缀会自动补上。
        force: 当目标文件已存在时是否强制覆盖。

    Returns:
        Path: 生成的策略文件路径。
    """
    # 1) 解析目标路径（支持 "subdir/xxx" 或 "xxx.py"）
    dest = Path(dest_name)
    if dest.suffix != ".py":
        dest = dest.with_suffix(".py")
    dest_path = Path.cwd() / dest
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # 2) 存在性检查
    if dest_path.exists() and not force:
        raise FileExistsError(
            f"生成失败，{dest_path} 已存在"
        )

    # 3) 找到包内的模板文件（兼容 zip/egg 安装方式）
    #   - 如果你把模板放在子包 pquant/templates/strategy.py，也可以用：
    #     files('pquant.templates').joinpath('strategy.py')
    template_res = files("pquant").joinpath("template.py")

    # 4) 以“真实文件”上下文拿到路径并复制
    with as_file(template_res) as src:
        if force and dest_path.exists():
            dest_path.unlink()
        shutil.copy(src, dest_path)

    return dest_path


def main(argv: list[str] | None = None) -> int:
    """命令行入口。

    Args:
        argv: 可选的参数列表，默认读取 ``sys.argv``。

    Returns:
        int: 进程退出码。
    """
    parser = argparse.ArgumentParser(
        prog="pquant",
        description="pquant 命令行工具：生成模板策略文件",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="在当前目录生成模板策略文件")
    p_new.add_argument("name", help="文件名或相对路径（可省略 .py）")

    args = parser.parse_args(argv)

    if args.command == "new":
        try:
            dest = create_from_template(args.name)
            print(f"已生成: {dest.relative_to(Path.cwd())}")
            return 0
        except FileExistsError as e:
            print(e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
