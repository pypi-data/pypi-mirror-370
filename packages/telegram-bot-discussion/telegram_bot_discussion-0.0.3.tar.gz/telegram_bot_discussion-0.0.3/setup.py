from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="telegram-bot-discussion",
    version="0.0.3",
    author="BorisPlus",
    description="Telegram Bot framework based on native Python-library for the Telegram Bot API.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["python-telegram-bot>=22.0"],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="python Telegram-bot framework",
    # project_urls={"Documentation": "link"},
    python_requires=">=3.9",
)
