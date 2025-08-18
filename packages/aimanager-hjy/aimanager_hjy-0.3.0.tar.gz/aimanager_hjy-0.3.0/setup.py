from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aimanager_hjy",
    version="0.3.0",
    author="hjy",
    author_email="hjy@example.com",
    description="AI服务管理包 - 统一的AI模型调用接口",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hjy/aimanager_hjy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic<3,>=2.0",
        "pydantic-settings<3,>=2.2",
        "httpx<1,>=0.27",
        "loguru<1,>=0.7",
        "mysql-connector-python<9,>=8.3",
        "cryptography<43,>=41",
        "oss2<3,>=2.18",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
