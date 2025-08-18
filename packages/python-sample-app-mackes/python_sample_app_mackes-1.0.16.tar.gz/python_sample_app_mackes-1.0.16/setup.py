from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="python-sample-app-mackes",
    version="1.0.16",
    description="A sample Python application with CLI entry point",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    url="https://github.com/mackes/python-sample-app",
    packages=["python_sample_app"],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sample-app=python_sample_app.main:main",
        ],
    },
)
