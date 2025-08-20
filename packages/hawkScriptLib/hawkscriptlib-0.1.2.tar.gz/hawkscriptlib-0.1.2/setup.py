from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hawkScriptLib",  # PyPI上的包名（必须唯一）
    version="0.1.2",            # 初始版本
    author="Johnny",
    author_email="13429113807@163.com",
    description="This library is used for communication between Hawk script and hz team's GUI PLC driver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],  # 依赖包列表
    extras_require={
        "dev": ["pytest>=6.0", "twine>=4.0.2", "setuptools>=42.0.0"]
    },
)









