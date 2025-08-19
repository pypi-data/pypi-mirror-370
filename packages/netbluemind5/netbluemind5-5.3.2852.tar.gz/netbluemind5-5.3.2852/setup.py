import sys
from setuptools import setup, find_packages

install_requires = ['requests']
if sys.version_info < (3, 4):
    install_requires.append('enum34')

setup(
    name = 'netbluemind5',
    packages = find_packages(),
    version = '5.3.2852',
    description = 'Automatically generated client for BlueMind >= 5 REST API. Check netbluemind4 for older releases',
    author = 'BlueMind team',
    author_email = 'contact@bluemind.net',
    url = 'http://gitlab.bluemind.net/',
    keywords = ['bluemind', 'rest', 'api', 'mail', 'groupware'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_requires
)
