from setuptools import setup, find_packages

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tako-sdk",
    version="0.1.31",
    author="Tako",
    author_email="support@trytako.com",
    description="A Python SDK for interacting with the Tako API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.8.2",
        "pytest>=7.4.3",
        "requests>=2.32.3",
        "httpx>=0.25.1",
        "pytest-asyncio>=0.21.1"
    ],
    license="MIT",
) 
