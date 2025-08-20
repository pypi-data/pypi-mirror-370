from setuptools import setup, find_packages

setup(
    name='amazon-scraper-vivektyagi',
    version='0.1.10',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.12.3',
        'selenium>=4.20.0',
    ],
    author='VIVEK TYAGI',
    description='A Python module to scrape product details from Amazon India using Selenium.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='amazon scraper selenium india',
    python_requires='>=3.7',
)
