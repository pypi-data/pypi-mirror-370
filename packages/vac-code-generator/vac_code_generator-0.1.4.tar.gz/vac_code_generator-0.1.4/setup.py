from setuptools import setup, find_packages

setup(
    name="vac-code-generator",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        'mcp[cli]>=1.13.0',
    ],

    entry_points={
        'console_scripts': [
            'verification-code-server=mcp_ts.server:create_and_run_server',
            'verification-code-sse-server=mcp_ts.server:create_and_run_sse_server',
            'verification-code-codebuddy=mcp_ts.server:create_and_run_server',
        ],
    },

    author="MCP Developer",
    author_email="example@example.com",
    description="基于FastMCP框架的验证码生成工具",
    url="https://github.com/mcp-project/verification-code-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.8',
)
