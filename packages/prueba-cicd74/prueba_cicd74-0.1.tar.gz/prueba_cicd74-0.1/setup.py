from setuptools import setup, find_packages

setup(
    name='prueba_cicd74',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        #aca irian las dependencias
        #ej: 'nunpy>=1.11.1'
    ],

    entry_points={
        "console_scripts": [
            "ejecutar-prueba = codigo_fuente.prueba_para_py_ci_cd:hola"
        ]
    }
)