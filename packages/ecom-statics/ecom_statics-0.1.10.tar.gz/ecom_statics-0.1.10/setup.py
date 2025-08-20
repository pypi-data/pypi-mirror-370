from setuptools import setup, find_packages


with open('version.txt', 'r') as file:
    version = file.read().strip()


setup(
    # Nombre del paquete
    name='ecom_statics',

    # Versión del paquete
    version=version,

    # Encuentra automaticamente todos los subpaquetes
    packages=find_packages(),

    # Incluir archivos no Python definidos en package_data
    include_package_data=True,

    # Descripcion corta del paquete
    description='Ecom statics',

    # Descripcion larga, tomada desde el README
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    # Datos del autor
    author='Ecom',
    author_email='equipo.ecomdata@gmail.com',

    # URL del proyecto
    url='https://git.ecom.com.ar/ecom-data/ecom_statics',

    # Clasificacion del paquete
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],

    # Define la version minima de Python compatible
    python_requires='>=3.8'
)
