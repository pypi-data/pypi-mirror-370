from setuptools import setup, find_packages, Extension


setup(
    name='python_stl_example',
    version='0.0.1.post2',
    description='A extended STL library',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='fourth-dimensional_universe',
    author_email='3817201131@qq.com',
    url='https://github.com/fourth-dimensional/python_stl_example',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=[]
)
