from setuptools import setup, find_packages

setup(
    name="discord-embed-model",
    version="0.1.1",
    author="Zackary W",
    description="discord.py advanced embeds",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ZackaryW/discord_embed_model",
    packages=find_packages(exclude=("tests", "examples")),
    install_requires=[
        "pydantic",
        "discord",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],

)