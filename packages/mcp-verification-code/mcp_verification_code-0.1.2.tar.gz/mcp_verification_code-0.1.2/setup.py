from setuptools import setup, find_packages

setup(
    name="mcp-verification-code",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.13.0",
    ],
    entry_points={
        'console_scripts': [
            'mcp-verification-code=mcp_verification_code.verification_code:generate_code_cli',
        ],
    },
    scripts=['mcp_verification_code/verification_code.py'],
    author="MCP Developer",
    author_email="example@example.com",
    description="一个基于FastMCP的验证码生成工具",
    url="https://github.com/yourusername/mcp-verification-code",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)