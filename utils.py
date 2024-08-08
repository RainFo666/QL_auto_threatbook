import re


def get_csrf_token(cookie: str):
    # 定义Cookie字符串
    # 使用正则表达式从Cookie中提取值
    csrf_token_match = re.search(r'csrfToken=([^;]+)', cookie)
    xx_csrf_match = re.search(r'xx-csrf=([^;]+)', cookie)

    # 获取并打印值
    x_csrf_token = csrf_token_match.group(1) if csrf_token_match else None
    xx_csrf = xx_csrf_match.group(1) if xx_csrf_match else None

    return x_csrf_token, xx_csrf
