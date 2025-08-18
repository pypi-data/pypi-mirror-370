from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metis-agent",
    version="0.17.4",
    author="Metis OS Team",
    author_email="cjohnson@metisos.com",
    description="A comprehensive framework for building powerful AI agents with enhanced developer experience, intelligent project awareness, and enterprise-grade security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metisos/metisos_agentV1",
    project_urls={
        "Documentation": "https://github.com/metisos/metisos_agentV1/blob/main/DOCUMENTATION.md",
        "Bug Tracker": "https://github.com/metisos/metisos_agentV1/issues",
        "Source Code": "https://github.com/metisos/metisos_agentV1",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ],
    keywords="ai, agent, llm, openai, groq, anthropic, huggingface, ollama, local-models, transformers, tools, memory, conversation, context-management, token-aware, intelligent-summarization, blueprint-detection, autonomous-tools, dynamic-generation, capability-expansion, text-analysis, sentiment-analysis, web-scraping, python-execution, advanced-math, nlp, readability-assessment, e2b, code-sandbox, secure-execution, cloud-sandbox, privacy, offline, quantization, knowledge-base, knowledge-management, sqlite, search, categorization, tagging, import-export, cli-management, knowledge-first-processing, todo, checklist, task-management, progress-tracking, project-planning, workflow-automation, project-awareness, codebase-analysis, code-understanding, intelligent-analysis, project-intelligence, code-insights, ast-parsing, security, encryption, aes-256-gcm, pbkdf2, input-validation, path-security, command-injection-prevention, enterprise-security",
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "groq>=0.4.0",
        "anthropic>=0.5.0",
        "huggingface-hub>=0.16.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "click>=8.0.0",
        "numpy>=1.20.0",
        "cryptography>=41.0.0",  # Enhanced: Required for AES-256-GCM encryption and PBKDF2 key derivation
        "pydantic>=1.8.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",  # For advanced web scraping
        "scipy>=1.7.0",  # For advanced mathematical operations
        "sympy>=1.8",    # For symbolic mathematics
        "e2b-code-interpreter>=1.5.0",  # For secure code execution in cloud sandboxes
        "PyYAML>=5.4.0",  # For YAML configuration files in Knowledge Base
        "tabulate>=0.8.0",  # For CLI table formatting in Knowledge Base
        "networkx>=2.8.0",  # For graph algorithms and data structures in Knowledge Base
        "scikit-learn>=1.0.0",  # For advanced similarity calculations in graph analysis
        "rich>=10.0.0",  # For enhanced CLI interface with colors, tables, and progress bars
        "psutil>=5.8.0",  # For system resource monitoring and process management
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
            "mypy>=0.812",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.2",
            "myst-parser>=0.15.1",
        ],
        "local-models": [
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "requests>=2.25.0",  # For Ollama integration
        ],
        "security": [
            "cryptography>=41.0.0",  # For advanced encryption features
            "psutil>=5.8.0",         # For system monitoring in security contexts
            "pyotp>=2.6.0",          # For TOTP/HOTP support if needed
        ],
    },
    entry_points={
        "console_scripts": [
            "metis=metis_core_package.cli.commands:cli",
        ],
    },
    include_package_data=True,
    license="Apache License 2.0",
)