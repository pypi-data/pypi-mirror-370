"""
setuptools es un abiblioteca q tiene la funcionalidad definir como se va empaquetar y distribuir el sw
setup es el nucleo dela configuracion del paquete, le dice a como empaquetar y organizar el proyecto para que otro la puedan instalas
find_packages busca y encuentra todos los paquetes con archivos __init__.py
"""
from setuptools import setup, find_packages

setup(
    name="aplicacon_ventas_aruiz",
    version="0.1.0",
    author="Liliana Mora",
    author_email="liliana@gmail.com",
    description='Paquete para gestionar, ventas, precios, impuestos y descuentos',
    long_description=open('README.MD').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/curso_python_camara/gestor/apliacion_ventas', 
    packages=find_packages(), 
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        #'Sistema Operativo:Multiplataforma',    
    ],
    python_requires='>=3.7'
    )
#https://pypi.org/account/register/
#crear una cuenta 

