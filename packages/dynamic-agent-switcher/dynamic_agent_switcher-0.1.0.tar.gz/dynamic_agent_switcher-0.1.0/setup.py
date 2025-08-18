from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dynamic-agent-switcher",
    version="0.1.0",
    author="Sumit Paul",
    author_email="sumit.18.paul@gmail.com",
    description="A flexible package for switching AI models during agent execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sumitpaul/dynamic-agent-switcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic-ai>=0.1.0",
        "asyncio",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="ai, agent, model, switching, rate-limit, pydantic-ai, langchain",
    project_urls={
        "Bug Reports": "https://github.com/sumitpaul/dynamic-agent-switcher/issues",
        "Source": "https://github.com/sumitpaul/dynamic-agent-switcher",
        "Documentation": "https://github.com/sumitpaul/dynamic-agent-switcher#readme",
    },
)
