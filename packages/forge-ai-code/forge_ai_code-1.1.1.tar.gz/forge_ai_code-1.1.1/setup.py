from setuptools import setup, find_packages

setup(
    name="forge-ai-code",
    version="1.1.1",
    author="Forge AI Team",
    author_email="support@forgeai.dev",
    description="智能AI编程助手",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['colorama>=0.4.4', 'requests>=2.25.1'],
    entry_points={
        "console_scripts": [
            "forge-ai-code=forge_ai_code.main:main",
            "fac=forge_ai_code.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
