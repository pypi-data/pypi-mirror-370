from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="anges",
    version="0.1.1",
    description="Anges - An LLM Powered Engineering Agent System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anges Team",
    author_email="me@anges.ai",
    url="https://github.com/anges-ai/anges",
    project_urls={
        "Documentation": "https://github.com/anges-ai/anges/tree/main/docs",
        "Examples": "https://github.com/anges-ai/anges/tree/main/examples",
        "Source": "https://github.com/anges-ai/anges",
        "Bug Tracker": "https://github.com/anges-ai/anges/issues",
    },
    packages=find_packages(include=['anges', 'anges.*']),
    include_package_data=True,
    package_data={
        'anges': [
            'configs/*',
            'prompt_templates/*',
            'web_interface/static/**/*',
            'web_interface/templates/*',
        ],
    },
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "flask-login>=0.6.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "openai>=1.0.0",
        "vertexai>=1.0.0",
        "anthropic>=0.3.0",
        "panel>=1.0.0",
        "google-generativeai>=0.3.0",
        "pandas>=1.3.0",
        "datasets>=2.0.0",
        "pytest>=6.0.0",
        "mime-files-reader>=0.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.15.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'anges-web=anges.web_interface.web_interface:main',
            'anges=anges.cli:main',
        ],
    },
    keywords=[
        "ai", "agent", "orchestration", "automation", "framework",
        "llm", "openai", "anthropic", "google", "vertexai",
        "workflow", "event-driven", "multi-agent", "assistant",
        "custom-actions", "plugin-system", "ai-automation"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Distributed Computing",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
