# -*- coding: utf-8 -*-  
"""
验证码生成工具模块
"""
import random
import string
import argparse

def generate_numeric_verification_code(digits: int = 6) -> str:
    """
    生成一个数字验证码。
    如果未指定位数，默认生成6位数字验证码。
    """
    return ''.join(random.choices(string.digits, k=digits))

def generate_alphabetic_verification_code(length: int = 6) -> str:
    """
    生成一个纯字母验证码（包含大小写）。
    如果未指定长度，默认生成6位字母验证码。
    """
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_mixed_verification_code(length: int = 6) -> str:
    """
    生成一个字母和数字混合的验证码。
    如果未指定长度，默认生成6位混合验证码。
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def generate_code_cli():
    """
    命令行接口生成验证码
    """
    parser = argparse.ArgumentParser(description='生成验证码')
    parser.add_argument('--type', choices=['numeric', 'alphabetic', 'mixed'], default='numeric',
                        help='验证码类型：数字、字母、混合（默认：数字）')
    parser.add_argument('--length', type=int, default=6,
                        help='验证码长度（默认：6）')
    args = parser.parse_args()
    
    if args.type == 'numeric':
        code = generate_numeric_verification_code(args.length)
    elif args.type == 'alphabetic':
        code = generate_alphabetic_verification_code(args.length)
    else:
        code = generate_mixed_verification_code(args.length)
    
    print(code)

if __name__ == "__main__":
    generate_code_cli()