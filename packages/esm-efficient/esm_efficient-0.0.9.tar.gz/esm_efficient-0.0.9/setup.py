from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

requirements = [
    'setuptools',
    'tqdm',
    'torch',
    'einops',
    'flash_attn>2.6.3',
    'accelerate',
    'pandas',
    'numpy',
    'polars',
    'torchmetrics',
    'lightning',
    'scikit-learn',
    'huggingface_hub'
]

test_requirements = [
    'pytest',
    'pytest-runner',
    'pooch',
    'fair-esm',
]


setup(
    name="esm-efficient",
    version='0.0.9',
    description="Efficient Evolutionary Scale Modeling: Efficient and simplified implementation of protein language model for inference and training.",
    keywords=['LLM', 'PLM', 'protein language model'],
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/uci-cbcl/esm-efficient",
    license="MIT",

    packages=find_packages(include=['esme*']),
    include_package_data=True,
    zip_safe=True,

    install_requires=requirements,
    entry_points='''
        [console_scripts]
        esme_download=esme.cli:cli_download
    ''',

    # test_suite='tests',
    # tests_require=test_requirements,
)
