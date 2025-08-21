import os
import re
from setuptools import setup, find_packages
from os import path


def read(fname):
    return open(path.join(path.dirname(__file__), fname), encoding='UTF-8').read()


# def save_version(v: str):
#     f = open('version.txt', 'w')
#     f.write(f'\tOking {v} - Openk Tecnologia')
#     f.close()


def get_version():
    version_file = os.path.join("src", "__init__.py")
    with open(version_file, "r") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if match:
        return match.group(1)
    raise RuntimeError("Não foi possível encontrar a variável __version__.")


version = get_version()  # <-- Nova forma de obter a versão
package_name = "oking" if len([c for c in version if c == '.']) < 3 else 'okingtest'
# save_version(version)
setup(
    name=package_name,
    version=version,
    author="Openk Tecnologia",
    author_email="<suporte.b2c@openk.com.br>",
    description='Pacote de integração de produtos, preço, estoque e pedidos com o sistema OkVendas da Openk',
    long_description_content_type="text/markdown; charset=UTF-8; variant=GFM",
    long_description=read('project_description.md'),
    packages=find_packages(include=['src', 'src.*']),
    include_package_data=True,
    install_requires=['schedule',
                      'requests',
                      'configparser',
                      'logger',
                      'jsonpickle',
                      'PySimpleGUI',
                      'pandas',
                      'pynput',
                      'setuptools'
                      ],
    keywords=['python', 'oking', 'openk', 'okvendas', 'ok'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        # "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [f'{package_name}=src.__main__:main']
    }
)
