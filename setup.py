from setuptools import setup, find_packages

setup(
    name="nebula-writer",
    version="0.1.0",
    description="AI-Powered Fiction Writing Assistant with Persistent Memory",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.3",
        "python-multipart>=0.0.6",
    ],
    entry_points={
        "console_scripts": [
            "nebula-writer=nebula-writer:main",
        ],
    },
    python_requires=">=3.10",
)
