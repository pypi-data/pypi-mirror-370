from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axon-api",
    version="0.2.1",
    author="B LLC",
    author_email="b-is-for-build@bellone.com",

    description="Zero-dependency WSGI framework with request batching, multipart streaming, and HTTP range support. "
                "Built for applications that require high performance without the bloat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/b-is-for-build/axon-api",
    project_urls={
        "Bug Reports": "https://github.com/b-is-for-build/axon-api/issues",
        "Source": "https://github.com/b-is-for-build/axon-api",
        "Documentation": "https://github.com/b-is-for-build/axon-api#readme",
    },    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    license="MIT",
)
