from setuptools import setup, find_packages


setup(
    name="BronkzTech",
    version="0.1.0",
    packages=find_packages(),
    description="API da BronkzTech",
    author="Dran",
    url="https://discord.gg/MJ5qfSqRy8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv"
    ],
)
