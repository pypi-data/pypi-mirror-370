from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="antonnia-events",
    version="1.0.5",
    author="Antonnia",
    author_email="support@antonnia.com",
    description="Python SDK for Antonnia Events and Webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antonnia/antonnia-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.7.0,<3.0.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
        "antonnia-conversations>=2.0.3"
    ],
    package_data={
        "antonnia.events": ["py.typed"],
    },
)