from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="lhs-global-service-fastapi",
    version="0.1.9",
    description="Global Oracle logging and debug management for FastAPI apps.",
    long_description=(here / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Rohit Jagtap",
    author_email="rohit.jagtap@lighthouseindia.com",
    url="https://github.com/yourusername/your-repo",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "cx_Oracle",
        "requests",
        "python-dotenv"
    ],
    python_requires=">=3.9",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["oracle", "logging", "fastapi", "debug", "global-service"],
    project_urls={
        "Source": "https://github.com/yourusername/your-repo",
        "Tracker": "https://github.com/yourusername/your-repo/issues",
    },
)