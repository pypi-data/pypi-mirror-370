from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["Math/*.pyx", "Math/*.pxd"],
                          compiler_directives={'language_level': "3"}),
    name='nlptoolkit-math-cy',
    version='1.0.17',
    packages=['Math'],
    package_data={'Math': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/StarlangSoftware/Math-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Math library',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
