import base58

def decode_token(encoded_str):
    try:
        # 尝试解码 Base58 编码的字符串
        decoded_bytes = base58.b58decode(encoded_str)
    except ValueError as e:
        raise ValueError(f"Base58 decoding failed: {e}") from e

    try:
        # 尝试将字节序列解码为 UTF-8 字符串
        decoded_str = decoded_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decoding failed: {e}") from e

    # 检查解码后的字符串是否包含 ":" 分隔符
    if ":" in decoded_str:
        api_address, secret = decoded_str.rsplit(":", 1)
        return api_address, secret
    else:
        raise ValueError("Decoded string does not contain ':' separator")
