import pathlib
import sys
import importlib.resources as pkg_resources
from pathlib import Path

def deploy_cheats():
    package_name = "my_arsenal_addons"
    resource_dir = "cheats"

    try:
        # ✅ 获取 Arsenal 包的安装路径
        import arsenal
        arsenal_path = Path(arsenal.__file__).parent
        print(f"[+] 检测到 Arsenal 已安装，路径为: {arsenal_path}")

        # ✅ 拼接目标目录：arsenal/my_custom/
        target_dir = arsenal_path / "data/cheats/my_custom"

        # ✅ 如果目录不存在，则创建它（包括父目录）
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"[+] 将 cheats 文件部署到: {target_dir}")

    except ImportError:
        print("[!] 错误：未检测到已安装的 Arsenal 包")
        print("[!] 请先通过以下命令安装 Arsenal：")
        print("    pip3 install arsenal")
        sys.exit(1)

    # ✅ 自动获取包内 cheats/ 目录下的所有 .md 文件名
    try:
        md_files = pkg_resources.contents(f"{package_name}.{resource_dir}")
    except Exception as e:
        print(f"[!] 错误：无法读取包内 {resource_dir} 目录。错误信息: {e}")
        print("[!] 请确认你的 setup.py 中已正确配置 package_data 包含 cheats/*.md")
        sys.exit(1)

    # ✅ 只保留 .md 文件，排除目录项
    md_files = [f for f in md_files if f.endswith('.md') and not f.endswith('/')]

    if not md_files:
        print("[!] 错误：未找到任何 .md 文件在包内的 cheats/ 目录")
        sys.exit(1)

    print(f"[+] 找到 {len(md_files)} 个 cheats 文件: {', '.join(md_files)}")

    # ✅ 遍历每个 .md 文件，读取并拷贝到目标目录
    for md_filename in md_files:
        try:
            # ✅ 从包内读取 .md 文件内容
            content = pkg_resources.read_text(f"{package_name}.{resource_dir}", md_filename)
            # ✅ 拼接目标路径：arsenal/my_custom/fscan.md
            dest_path = target_dir / md_filename
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 已部署: {md_filename} --> {dest_path}")

        except Exception as e:
            print(f"❌ 部署失败 {md_filename}: {e}")
    print("\n🎉 所有自定义 cheats 已部署完成！请重启 Arsenal 查看效果。")