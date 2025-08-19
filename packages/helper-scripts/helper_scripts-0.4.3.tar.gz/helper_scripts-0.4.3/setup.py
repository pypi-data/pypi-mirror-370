from setuptools import setup

setup(
    name = 'helper_scripts',
    packages = ['database_handler','send_mail','google_drive'],
    author='Samuel Kizza & Winston Ssentongo',
    author_email= 'winstondavid96@gmail.com',
    maintainer='Winston David Ssentongo',
    maintainer_email='winstondavid96@gmail.com',
    description='Database Helper Package',
    url='https://github.com/winston1o1/helper-scripts',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
    "psycopg2",
    "google-api-python-client"
    ]
)