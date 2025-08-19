from setuptools import setup, find_packages

setup(
    name="my-arsenal-addons",
    version="0.1.0",
    packages=find_packages(),  # 包含 my_arsenal_addons/

    # 项目元数据
    description="一键部署自定义 cheatsheets 到 Arsenal 工具的自定义命令目录",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourname/my-arsenal-addons",  # 可选

    # 声明包含非 Python 文件（如 cheats/*.md）
    include_package_data=True,
    package_data={
        "my_arsenal_addons": ["cheats/*.md"], # 表示打包my_arsenal_addons/cheats/*.md 文件路径
    },

    # 或使用 MANIFEST.in 作为补充（推荐同时提供）
    install_requires=[],  # 本例无额外依赖

    # 注册命令行工具
    entry_points={
        'console_scripts': [
            'install-arsenal-addons=my_arsenal_addons.custom_cheats:deploy_cheats',
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)