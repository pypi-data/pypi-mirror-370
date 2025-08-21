from setuptools import setup, find_packages
import os


# README 파일 읽기
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "ABLE Labs 로봇 제어 API 패키지"


setup(
    name="ablelabs",
    version="0.4.3",
    description="ABLE Labs API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="sypark",
    author_email="sy.park@ablelabsinc.com",
    url="https://github.com/ABLE-Labs/ABLE-API",
    install_requires=[
        "et-xmlfile>=1.1.0",
        "future>=1.0.0",
        "iso8601>=2.1.0",
        "loguru>=0.7.2",
        "openpyxl>=3.1.5",
        "pyserial>=3.5",
        "PyYAML>=6.0.1",
        "httpx>=0.28.1",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
)
