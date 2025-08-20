from setuptools import setup, find_packages

setup(
    name='context-log-python',
    version='0.1.3',
    packages=find_packages(),
    description='A contextual logging framework for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ramakrishna Bapathu',
    author_email='ramkrishna9493@gmail.com',
    url='https://github.com/Ramakrishna9493/context_logger',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
