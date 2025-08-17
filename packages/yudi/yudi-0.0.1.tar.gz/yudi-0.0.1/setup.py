from setuptools import setup,find_packages

setup(
    name='yudi',
    version='0.0.1',
    author='Yuvraj Dixit',
    author_email='yuvrajdixit017@gmail.com',
    description='A simple voice assistant created speech recognition and text to speech',
)
package = find_packages()
install_requirements = [
    'selenium',
    'webdriver-manager'
]
