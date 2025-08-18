# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="typegpt-moderation",
    version="1.0.1",
    author="typegpt",
    author_email="contact@typegpt.net",
    description="A client library for the TypeGPT Multimodal Moderation API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires='>=3.7',
    install_requires=[
        "httpx>=0.20.0",
        "pydantic>=2.0",
    ],
)