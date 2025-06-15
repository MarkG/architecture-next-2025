from setuptools import setup, find_packages

setup(
    name='cv-architect-assistant',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pygit2',
    ],
    entry_points={
        'console_scripts': [
            'cvaa = cvaa.main:cli',
        ],
    },
    author="Mark",
    author_email="",
    description="A command-line tool to assist software architects.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/cv-architect-assistant", # Replace with your URL
)