from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-repo-manager-jkn",
    version="1.0.0",
    author="Jonathan K-N",
    author_email="your.email@example.com",
    description="Un outil professionnel pour créer et gérer des dépôts GitHub avec interface graphique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JonathanK-N/github-manager-pro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "github-manager=github_manager.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)