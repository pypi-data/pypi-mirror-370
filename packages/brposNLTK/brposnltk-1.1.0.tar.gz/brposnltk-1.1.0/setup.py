from setuptools import setup, find_packages

setup(
    name='brposNLTK',
    version='1.1.0',
    description='A Part-of-Speech Tagger for Bengali Dialects.',
    author='Mahmudul Haque Shakir',
    author_email='mahmudulhaqueshakir@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'tensorflow',
        'openpyxl',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: Linguistic'
    ],
    python_requires='>=3.6',
)