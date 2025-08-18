from pathlib import Path

from setuptools import find_packages, setup

THIS_DIR = Path(__file__).parent

# with open(THIS_DIR / "docs/description.md", encoding="utf-8") as f:
with open(THIS_DIR / "README.md", encoding="utf-8") as f:
    long_description = f.read()


def read_requirements(filepath: Path) -> list[str]:
    with open(filepath, encoding="utf-8") as fd:
        return [
            package.strip("\n")
            for package in fd.readlines()
            if not package.startswith("#")
        ]


requirements = read_requirements(THIS_DIR / "requirements.txt")


setup(
    name="spt",
    version="0.2.5",
    description="Scientific Matplotlib plot rcParams configuration template python package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "scientific plot",
        "Matplotlib",
    ],
    author="yangsl",
    author_email="yangsl2126@sjtu.edu.cn",
    maintainer="yangsl",
    maintainer_email="yangsl2126@sjtu.edu.cn",
    url="https://github.com/Bit-Part-Young/spt",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        "examples": [
            "numpy",
            "pandas",
            "scikit-learn",
        ]
    },
    python_requires=">=3.9",
    platforms=["all"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
