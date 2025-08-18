from setuptools import setup, find_packages

setup(
    name='starlasu-specs',
    version = "0.4.3",
    author='Federico Tomassetti',
    author_email='federico@strumenta.com',
    description='Starlasu Specs',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'lionweb>=0.3.2',
        'requests>=2.32.3'
    ]
)