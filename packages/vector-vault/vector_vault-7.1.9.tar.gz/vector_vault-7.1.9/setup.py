from setuptools import setup, find_packages

setup(
    name="vector_vault",
    version="7.1.9",
    packages=find_packages(),
    author="VectorVault.io",
    author_email="john@johnrood.com",
    description="Quickly create RAG apps, Agents, and Unleash the full power of AI with Vector Vault",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/John-Rood/VectorVault",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    data_files=[('', ['LICENSE'])],
    install_requires=[
        'numpy',
        'requests',
        'bs4',
        'google-cloud-storage',
        'annoy',
        'openai',
        'tiktoken',
        'cerebras_cloud_sdk',
        'anthropic',
        'pymupdf',
        'google-genai',
        # any other dependencies
    ],
)
