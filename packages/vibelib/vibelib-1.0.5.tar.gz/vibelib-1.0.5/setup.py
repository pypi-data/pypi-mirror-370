from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibelib",
    version="1.0.5",
    author="soradotwav",
    author_email="dev@soradotwav.com",
    description="AI-powered computational operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soradotwav/vibelib",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
    ],
    package_data={
        "vibelib": ["py.typed"],
    },
    license="GPL-3.0",
)
