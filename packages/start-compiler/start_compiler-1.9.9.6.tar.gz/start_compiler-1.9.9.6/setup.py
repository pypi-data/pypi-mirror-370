from setuptools import setup, find_packages

setup(
    name="start_compiler",
    version="1.9.9.6",
    packages=find_packages(),
    package_data={'': ['start_grammar.ebnf']},
    install_requires=[
        "lark>=1.1.2",
        "numpy>=1.26.4",
        "pynput>=1.8.1"
    ],
    include_package_data=True,
    description="A package to compile the langauge START",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/jjgsherwood/start_compiler",
    author="Joost Broekens; Jonne Goedhart",
    author_email="Joost.broekens@gmail.com",
    license="Creative Commons CC BY-NC-SA 4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)