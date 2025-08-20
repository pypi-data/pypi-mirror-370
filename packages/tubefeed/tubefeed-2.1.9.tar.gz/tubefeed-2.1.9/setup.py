from setuptools import setup, find_packages


version = '2.1.9'

requirements = [
    'aiofiles==24.1.0',
    'aiohttp==3.12.15',
    'aiosqlite==0.21.0',
    'yt-dlp==2025.8.20',
]

with open('README.md', 'r', encoding='utf-8') as readme_file:
    description = 'Most of the links in this description will only work if you view the [README.md](https://gitlab.com/troebs/tubefeed) on GitLab.\n\n'
    description += readme_file.read()

setup(
    name='tubefeed',
    version=version,
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='seamlessly integrate YouTube with Audiobookshelf',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/troebs/tubefeed',
    project_urls={
        'Bug Tracker': 'https://gitlab.com/troebs/tubefeed/-/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.10',
    install_requires=requirements
)
