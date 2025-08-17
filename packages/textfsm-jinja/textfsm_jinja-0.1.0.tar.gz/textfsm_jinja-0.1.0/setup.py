from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textfsm-jinja",
    version="0.1.0",
    author="duanfu",
    author_email="duanfu456@163.com",
    description="一个基于TextFSM和Jinja2的文本解析和渲染库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/duanfu456/textfsm-jinja",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "textfsm",
        "Jinja2",
    ],
    entry_points={
        'console_scripts': [
            'textfsm-jinja=textfsm_jinja.cli:main',
        ],
        'gui_scripts': [
            'textfsm-jinja-gui=textfsm_jinja.gui:main',
        ],
    },
)