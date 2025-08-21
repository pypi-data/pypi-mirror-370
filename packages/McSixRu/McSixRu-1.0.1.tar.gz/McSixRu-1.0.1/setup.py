from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="McSixRu",
    version="1.0.1",
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    author="Your Name",
    author_email="mcsixhelps@gmail.com",
    description="AI library for Russian users with OpenRouter integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="ai, chat, openrouter, russian",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)