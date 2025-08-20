#!/usr/bin/env python3
"""
Forge AI Code 安装配置
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    """读取文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def get_requirements():
    """获取依赖列表"""
    content = read_file('requirements.txt')
    if content:
        return [line.strip() for line in content.split('\n') 
                if line.strip() and not line.startswith('#')]
    return ['colorama>=0.4.4', 'requests>=2.25.1']

setup(
    name="forge-ai-code",
    version="1.1.0",
    author="Forge AI Team",
    author_email="support@forgeai.dev",
    description="智能AI编程助手 - 通过自然语言对话进行编程开发",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/forge-ai/forge-ai-code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "forge-ai-code=forge_ai_code.main:main",
            "fac=forge_ai_code.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "forge_ai_code": ["*.md", "*.txt", "*.json"],
    },
    zip_safe=False,
)
