from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="flvmeta-timestamp-analyzer",
    version="1.0.2",
    author="CoderWGB",
    author_email="864562082@qq.com",
    description="FLV音视频时间戳分析工具，可通过MCP协议调用",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Soar-Coding-Life/flvmeta-timestamp-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flv-timestamp-analyzer=flv_timestamp_analyzer:main",
        ],
    },
    package_data={
        "": ["mcp.config.json", ".mcp.servers.json"],
    },
    include_package_data=True,
)