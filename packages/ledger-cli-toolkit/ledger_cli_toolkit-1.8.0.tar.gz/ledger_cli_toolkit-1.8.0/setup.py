from setuptools import setup, find_packages

# Leer el archivo README para usarlo como descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ledger-cli-toolkit",
    version="1.8.0",  # Cambia según el versionado de tu proyecto
    author="Eduardo Rangel",
    author_email="dante61918@gmail.com",
    description="Library for manipulating accounting files in .ledger format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EddyBel/Ledgerpy",  # Reemplaza con la URL de tu repositorio
    project_urls={
        "Bug Tracker": "https://github.com/EddyBel/Ledgerpy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",  # Cambia según el estado del proyecto
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    packages=find_packages(),  # Encuentra automáticamente todos los paquetes en el proyecto
    python_requires=">=3.7",  # Versión mínima de Python requerida
    install_requires=[
        "tabulate>=0.9.0",  # Para la funcionalidad de visualización
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black",
            "flake8",
        ],  # Dependencias opcionales para desarrollo
    },
    entry_points={
        "console_scripts": [
            "ledgerpy=ledgerpy.cli:main",  # Si planeas agregar un CLI para la librería
        ],
    },
    license="MIT",
    include_package_data=True,  # Incluye archivos adicionales especificados en MANIFEST.in
)
