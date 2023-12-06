"""
setting up packages to make sure our machine read our packages properly.
"""
from os import path

from setuptools import setup, find_packages

working_dir = path.abspath(path.dirname(__file__))

if __name__ in ("__main__", "builtins"):
    setup(
        name="자람 허브 API v2",
        description="FastAPI로 재작성된 자람 허브 API 입니다.",
        url="https://github.com/msng-devs/JGW-hub/tree/bnbong",
        author="bnbong",
        author_email="bbbong9@gmail.com",
        packages=find_packages(),
        package_data={},
        python_requires=">=3.10, <3.11",
    )