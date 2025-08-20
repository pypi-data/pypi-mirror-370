"""
Setup configuration for Skyrelis - AI Agent Security Library
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Package metadata
PACKAGE_NAME = "skyrelis"
VERSION = "0.1.5"
DESCRIPTION = "AI Agent Security Library - Enterprise-grade security for AI agents, starting with comprehensive observability across multiple frameworks"
AUTHOR = "Skyrelis Security Team" 
AUTHOR_EMAIL = "security@skyrelis.com"
URL = "https://github.com/skyrelis/skyrelis"
LICENSE = "Proprietary"

# Dependencies
INSTALL_REQUIRES = [
    "langchain>=0.1.0",
    "langchain-core>=0.1.0", 
    "langchain-openai>=0.0.5",
    "requests>=2.25.0",
    "aiohttp>=3.8.0",
    "pydantic>=1.8.0",
    "python-dotenv>=0.19.0",
]

# Optional dependencies for different features
EXTRAS_REQUIRE = {
    "security": [
        "cryptography>=3.4.0",
        "bcrypt>=3.2.0",
        "pyjwt>=2.0.0",
    ],
    "opentelemetry": [
        "opentelemetry-api>=1.0.0",
        "opentelemetry-sdk>=1.0.0", 
        "opentelemetry-instrumentation>=0.30b0",
        "opentelemetry-exporter-jaeger>=1.0.0",
    ],
    "langsmith": [
        "langsmith>=0.0.30",
    ],
    "crewai": [
        "crewai>=0.70.0",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
    ],
    "compliance": [
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=1.4.0",
    ],
    "threat-detection": [
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.991",
        "bandit>=1.7.0",  # Security linting
    ],
}

# All optional dependencies
EXTRAS_REQUIRE["all"] = [
    dep for deps in EXTRAS_REQUIRE.values() for dep in deps
]

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Information Technology",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9", 
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Monitoring",
    "Topic :: Security",
    "Topic :: Security :: Cryptography",
    "Topic :: System :: Logging",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Office/Business :: Financial",
    "Framework :: AsyncIO",
    "Environment :: Web Environment",
]

# Keywords for discoverability
KEYWORDS = [
    "ai", "agents", "security", "observability", "monitoring", "tracing", 
    "langchain", "telemetry", "analytics", "debugging", "performance", 
    "opentelemetry", "compliance", "audit", "threat-detection", "cybersecurity",
    "enterprise", "SOC2", "GDPR", "HIPAA", "risk-management", "governance"
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.8",
    classifiers=CLASSIFIERS,
    keywords=" ".join(KEYWORDS),
    project_urls={
        "Documentation": "https://skyrelis.readthedocs.io",
        "Source": "https://github.com/skyrelis/skyrelis", 
        "Bug Reports": "https://github.com/skyrelis/skyrelis/issues",
        "Security": "https://github.com/skyrelis/skyrelis/security",
        "Funding": "https://github.com/sponsors/skyrelis",
    },
    entry_points={
        "console_scripts": [
            "skyrelis=skyrelis.cli:main",
        ],
    },
) 