from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='api-blueprint-generator',
    version='1.0.0',
    author='James The Giblet',
    author_email='your_email@example.com', # Add your email here
    description='Generate production-ready APIs from a simple Markdown specification.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/your_username/Project-API-Blueprint-Strategy', # Add your GitHub repo URL here
    packages=find_packages(),
    install_requires=[
        'click>=8.0',
        'jinja2>=3.0',
        'pyyaml>=6.0',
        'python-frontmatter>=1.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Build Tools",
        "Framework :: FastAPI",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'blueprint=api_blueprint_generator.cli:cli',
        ],
    },
    include_package_data=True,
)