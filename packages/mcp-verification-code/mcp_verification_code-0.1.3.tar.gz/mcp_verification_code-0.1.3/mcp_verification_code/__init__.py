"""
验证码生成包

提供三种验证码生成方式：
- 数字验证码
- 字母验证码
- 混合验证码

版本: 0.1.2
"""

from .verification_code import generate_numeric_verification_code, generate_alphabetic_verification_code, generate_mixed_verification_code

__version__ = '0.1.2'
__all__ = [
    'generate_numeric_verification_code',
    'generate_alphabetic_verification_code',
    'generate_mixed_verification_code',
    '__version__'
]