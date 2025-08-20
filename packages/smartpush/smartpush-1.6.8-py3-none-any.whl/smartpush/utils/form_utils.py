import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def aes_encrypt(data, key, iv):
    """
    参数加密
    :param data:
    :param key:
    :param iv:
    :return:
    """
    key = key.encode('utf-8')
    iv = iv.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(ciphertext).decode('utf-8')


def aes_decrypt(ciphertext, key, iv):
    """
    参数解密
    :param ciphertext:
    :param key:
    :param iv:
    :return:
    """
    key = key.encode('utf-8')
    iv = iv.encode('utf-8')
    ciphertext = base64.b64decode(ciphertext)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_data.decode('utf-8')
