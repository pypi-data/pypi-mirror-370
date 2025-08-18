from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kyouka-cli",
    version="1.0.0",
    author="vyx",
    author_email="kiyoshi.dev31@gmail.com",
    description="yt dl wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lyraxial/kyouka",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "yt-dlp",
        "pygame",
        "pillow",
    ],
    extras_require={
        "full": [
            "opencv-python",
            "python-vlc",
            "tk"
        ]
    },
    entry_points={
        "console_scripts": [
            "kyouka = kyouka.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)