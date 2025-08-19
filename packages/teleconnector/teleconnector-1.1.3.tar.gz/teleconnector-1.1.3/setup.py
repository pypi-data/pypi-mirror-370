from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="teleconnector",
    version="1.1.3",
    author="MrFidal",
    author_email="mrfidal@proton.me",
    description="Advanced Telegram Bot API Connector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebreach/teleconnector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.6",
    install_requires=["requests>=2.25.0"],
    keywords=[
        "telegram",
        "bot",
        "api",
        "messaging",
        "chat",
        "telegram-bot",
        "telegram-api",
        "file-transfer"
    ],
    project_urls={
        "Bug Reports": "https://github.com/bytebreach/teleconnector/issues",
        "Source": "https://github.com/bytebreach/teleconnector",
    },
)