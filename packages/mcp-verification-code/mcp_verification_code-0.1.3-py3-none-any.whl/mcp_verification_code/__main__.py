"""
验证码生成包的入口点
"""


from .verification_code import generate_code_cli

if __name__ == "__main__":
    generate_code_cli()