from setuptools import setup, find_packages

setup(
    name="Trueflagger",  # Nome que aparecerá no PyPI
    version="0.1.2",  # Primeira versão
    author="Leonardo Nery",
    author_email="leonardonery616@gmail.com",  # Substitua por seu e-mail
    description="Uma biblioteca simples para criação e controle de flags por arquivos.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
      # Substitua pelo seu repositório
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
