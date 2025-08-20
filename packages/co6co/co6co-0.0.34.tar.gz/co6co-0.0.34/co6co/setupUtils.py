from os import path
from setuptools.command.sdist import sdist
from setuptools import find_packages
from typing import Iterable


def _getPacksAndPackName(setup_folder: str, exclude: Iterable[str] = ["*tests*"], include: Iterable[str] = ["*"]):
    """
    获取包名和包目录.
    """
    packages = find_packages(setup_folder, exclude=exclude, include=include)
    packageName = packages[0]
    return packageName, packages


def package_name(setupFilePath: str, exclude: Iterable[str] = ["*tests*"], include: Iterable[str] = ["*"]):
    """
    获取包名.
    示例:
        from setupUtils import package_name
        packageName,packages = package_name(__file__)

    @param setupFilePath: setup.py文件路径.
        在setup.py 文件中传入 “__file__” 即可.
    """
    setup_folder = path.abspath(path.dirname(setupFilePath))
    packageName, packages = _getPacksAndPackName(setup_folder, exclude, include)
    packageName = packageName.replace("_", '.', 1)
    print(f"packageName: {packageName}\n", "packages: \n", "\n".join(packages))
    return packageName, packages


def get_classifiers():
    """
    获取分类器.
    """
    classifiers = [
        "Development Status :: 5 - Production/Stable",  # 处于稳定生产阶段
        "Intended Audience :: Developers",  # 标用户是开发者
        "License :: OSI Approved :: MIT License",  # 采用 MIT 许可证
        "Programming Language :: Python :: 3",  # 项目支持 Python 3
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",  # 可以在任意操作系统上运行
    ]
    return classifiers


def get_version(setupFilePath: str,  versionInFileName: str = "__init__.py"):
    """
    获取版本信息.
    示例:
        from setupUtils import get_version
        packages = find_packages()
        packageName = packages[0]
        __version__ = get_version(packageName, __file__)

    @param packageName: 要查询版本包.
        packages = find_packages()
        packageName = packages[0]
    @param setupFilePath: setup.py文件路径.
        在setup.py 文件中传入 “__file__” 即可.
    @param versionInFileName: 版本信息所在文件名.
        默认是 __init__.py
    Returns version, packageName.
    """
    setup_folder = path.abspath(path.dirname(setupFilePath))
    packageName, _ = _getPacksAndPackName(setup_folder)
    version_file = path.join(setup_folder, packageName, versionInFileName)
    with open(version_file, "rb") as f:
        source_code = f.read()
    exec_code = compile(source_code, version_file, "exec")
    scope = {}
    exec(exec_code, scope)
    version: str = scope.get("__version__", None)
    if version:
        return version
    raise RuntimeError("Unable to find version string.")


def readme_content(setupFilePath: str, readmeFileName: str = "README.md"):
    """
    获取README.md内容.

    @param setupFilePath: setup.py文件路径.
        在setup.py 文件中传入 “__file__” 即可.
    @param readmeFileName: README.md文件名.
        默认是 README.md
    """
    currentDir = path.abspath(path.dirname(setupFilePath))
    long_description = None
    with open(path.join(currentDir, readmeFileName), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


class CustomSdist(sdist):
    """
    自定义打包命令.
    用于解决打包后的文件名中包含 “.” 变为 "_" 的问题.
    """

    def get_archive_files(self):
        # 获取原始的文件名列表
        files = super().get_archive_files()
        new_files = []
        for file in files:
            # 替换文件名中的 _ 为 .
            new_file = file.replace(self.distribution.get_name().replace('.', '_'), self.distribution.get_name())
            new_files.append(new_file)
        return new_files
