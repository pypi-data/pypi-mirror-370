from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='duplipy',
    version='0.2.5',
    author='Infinitode Pty Ltd',
    author_email='infinitode.ltd@gmail.com',
    description='DupliPy is a quick and easy-to-use package that can handle text formatting and data augmentation tasks for NLP in Python, with added support for image augmentation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/infinitode/duplipy',
    packages=find_packages(),
    install_requires=[
        'nltk',
        'numpy',
        'langcodes',
        'joblib',
        'tqdm',
        'pillow',
        'valx'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6',
)