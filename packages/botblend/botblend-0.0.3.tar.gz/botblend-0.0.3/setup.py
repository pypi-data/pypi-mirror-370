from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='botblend',
    version='0.0.3',
    description='Librería de utilerías para automatizaciones RPA con Microsoft Graph y otras herramientas.',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Para que interprete markdown correctamente
    author='Raul Sanz',
    author_email='mail@rulosanz.com',
    url='https://github.com/raulsanvaz/botblend',  # Pon aquí el repo correcto
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'msal>=1.0.0',
        'requests>=2.0.0',
        'python-dotenv>=1.0.0',
        'pandas>=1.0.0',
        'openpyxl>=3.0.0',
        'Office365-REST-Python-Client>=2.3.11'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Cambia según el estado real
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  # Ajusta si usas otra licencia
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    project_urls={
        'Documentation': 'https://github.com/raulsanvaz/botblend#readme',  # O tu URL de docs si tienes
        'Source': 'https://github.com/raulsanvaz/botblend',
    },
)

