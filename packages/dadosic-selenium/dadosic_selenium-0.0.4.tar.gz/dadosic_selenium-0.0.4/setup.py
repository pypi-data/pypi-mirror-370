from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='dadosic-selenium',
    version='0.0.4',
    license='MIT License',
    author='Gustavo Sartorio',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='strov3rl@gmail.com',
    keywords='zendesk selenium',
    description=u'Automação do zendesk com selenium e zenpy',
    packages=['dadosic'],
    install_requires=['selenium',
    'zenpy',
    'requests',
    'urllib3',
    'python-dotenv',
    'pandas',
    'pandas-gbq',
    'google-auth' 
    ],)