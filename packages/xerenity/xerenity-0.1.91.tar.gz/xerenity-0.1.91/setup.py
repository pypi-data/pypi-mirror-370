from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='xerenity',
    version='0.1.91',
    description='Python package for xerenity',
    url='https://xerenity.vercel.app/login',
    author='Andres Velez',
    author_email='svelez@xerenity.co',
    license='BSD 2-clause',
    install_requires=['supabase>=2.4.4'],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
    ],
)
