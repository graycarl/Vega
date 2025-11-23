from cryptography.fernet import Fernet
import os
import base64

class Crypto:
    """加密工具类"""
    
    def __init__(self, key: str = None):
        """
        初始化加密工具
        :param key: Fernet 密钥 (base64 encoded 32 bytes). 如果未提供，尝试从环境变量 VEGA_SECRET_KEY 获取
        """
        if not key:
            key = os.getenv("VEGA_SECRET_KEY")
        
        if not key:
            # 如果没有密钥，生成一个临时的（仅用于开发/测试，生产环境必须配置）
            # 注意：每次重启都会变化，导致无法解密之前的数据
            key = Fernet.generate_key().decode()
            print("WARNING: No VEGA_SECRET_KEY provided. Using a temporary key.")
            
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        """加密字符串"""
        if not data:
            return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        """解密字符串"""
        if not token:
            return ""
        return self.fernet.decrypt(token.encode()).decode()

# 全局实例
_crypto = None

def get_crypto() -> Crypto:
    global _crypto
    if _crypto is None:
        _crypto = Crypto()
    return _crypto
