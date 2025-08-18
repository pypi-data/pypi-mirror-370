from setuptools import setup, find_packages

setup(
    name="mcp-verification-code",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.13.0",
    ],
    entry_points={
        'console_scripts': [
            'mcp-verification-code=mcp_verification_code.verification_code:run_server',
        ],
    },
)