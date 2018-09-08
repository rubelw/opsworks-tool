from setuptools import setup
import os




DESCRIPTION = ("Creates opsworks template and deploys it.")
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


VERSION = '0.0.2'



def find_data(starting_dir, the_dir):
    original_cwd = os.getcwd()
    tree = []
    try:
        os.chdir(starting_dir)
        for folder, subs, files in os.walk(the_dir):
            for file in files:
                tree.append('{}/{}'.format(folder, file))
    except Exception:
        pass

    os.chdir(original_cwd)
    return tree


setup(
    name='OpsworksTool',
    version='0.0.1',
    packages=['opsworkstool'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Will Rubel',
    author_email='willrubel@gmail.com',
    include_package_data=True,
    package_data={'opsworkstool': find_data('opsworkstool', 'template')},
    install_requires=[
        'boto3>=1.4.3',
        'GitPython>=2.1.7',
        'Click>=6.7',
        'PyYAML>=3.12',
        'pymongo>=3.4.0',
        'stackility>=0.3',
        'Mako>=1.0.6'
    ],
    entry_points="""
        [console_scripts]
        opsworkstool=opsworkstool.command:cli
    """
)
