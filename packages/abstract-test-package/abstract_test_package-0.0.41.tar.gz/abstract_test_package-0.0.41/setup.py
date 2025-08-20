from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='abstract_test_package',
    version='0.0.41',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description='abstract_test_package is a Python package that facilitates testing with abstract scenarios. Utilizing PyTest, it offers extra utilities to streamline the creation and execution of abstract tests.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AbstractEndeavors/abstract_test_package',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
