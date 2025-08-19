from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axon-api",
    version="0.9.0",
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
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    keywords="wsgi framework streaming multipart http-range zero-dependency",
    license="MIT",

)
