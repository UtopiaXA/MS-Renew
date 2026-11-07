# -*- coding: UTF-8 -*-
import http.server
import socketserver
import urllib.parse
import webbrowser
import requests as req
import json, sys, os, base64, hashlib
from Crypto.Cipher import AES

class aescrypt():
    def __init__(self, key, model, iv, encode_):
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    def aesencrypt(self, text):
        text = self.add_16(text)
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

auth_code = None
auth_error = None

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code, auth_error
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>授权成功</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: #28a745;">✅ 授权成功！</h1>
                <p>已成功获取微软授权码，你可以关闭本浏览器标签页，返回终端查看后续结果。</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif 'error' in params:
            auth_error = params.get('error_description', ['未知错误'])[0]
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>授权失败</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: #dc3545;">❌ 授权失败</h1>
                <p>错误信息: {auth_error}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    if len(sys.argv) >= 4:
        password_raw = sys.argv[1].strip()
        client_id = sys.argv[2].strip()
        client_secret = sys.argv[3].strip()
    else:
        print("=" * 60)
        print("          微软保活 Token 一键获取与加密工具")
        print("=" * 60)
        client_id = input("1. 请输入应用 ID (Client ID): ").strip()
        client_secret = input("2. 请输入应用机密 (Client Secret): ").strip()
        password_raw = input("3. 请输入加密密码 (自定义的 PASSWORD，同 GitHub Secrets): ").strip()

    if not client_id or not client_secret or not password_raw:
        print("[ERROR] 必须完整提供应用 ID、应用机密和密码！")
        sys.exit(1)

    password = str(hashlib.md5(password_raw.encode("utf-8")).hexdigest()[8:-8])
    redirect_uri = "http://localhost:53682/"
    scopes = "offline_access Files.ReadWrite.All User.Read Mail.Read"

    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        + urllib.parse.urlencode({
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'response_mode': 'query',
            'scope': scopes
        })
    )

    port = 53682
    try:
        server = socketserver.TCPServer(('localhost', port), OAuthHandler)
        server.allow_reuse_address = True
    except Exception as e:
        print(f"[ERROR] 无法监听本地端口 {port}，请确认未被占用: {e}")
        sys.exit(1)

    print("\n正在启动本地监听并打开浏览器进行授权...")
    print(f"如果浏览器未自动打开，请手动复制以下链接到浏览器打开：\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("等待浏览器授权回调中 (请在弹出的微软页面中登录并同意授权)...")
    while auth_code is None and auth_error is None:
        server.handle_request()
    server.server_close()

    if auth_error:
        print(f"\n[ERROR] 授权失败: {auth_error}")
        sys.exit(1)

    print("\n[OK] 成功捕获授权码，正在向微软请求 Refresh Token...")
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = req.post(token_url, data=token_data, headers=headers)

    try:
        jsontxt = resp.json()
    except Exception as e:
        print(f"[ERROR] 微软响应解析失败，HTTP 状态码: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    if 'refresh_token' not in jsontxt:
        print(f"[ERROR] 换取 Token 失败，HTTP 状态码: {resp.status_code}")
        print(f"错误详情:\n{json.dumps(jsontxt, indent=2, ensure_ascii=False)}")
        sys.exit(1)

    refresh_token = jsontxt['refresh_token']
    print("[OK] 成功获取新的 Refresh Token！")

    # 加密并写入 token/0.txt
    aes = aescrypt(password, 'ECB', '', 'utf8')
    encrypted_token = aes.aesencrypt(refresh_token)

    token_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token')
    os.makedirs(token_dir, exist_ok=True)
    target_file = os.path.join(token_dir, '0.txt')
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(encrypted_token)

    print(f"[OK] 已成功加密并写入: {target_file}")
    print("\n" + "=" * 60)
    print("               配置完成！后续步骤：")
    print("=" * 60)
    print("1. 请前往 GitHub 仓库: Settings -> Secrets and variables -> Actions")
    print("   确保配置以下三个 Secret：")
    print(f"   - ID_LIST   : {client_id}")
    print(f"   - KEY_LIST  : {client_secret}")
    print(f"   - PASSWORD  : {password_raw}")
    print("2. 在本地执行 git 提交并推送新的 token：")
    print("   git add token/0.txt")
    print('   git commit -m "Update new token from OneIndex app"')
    print("   git push")
    print("=" * 60)

if __name__ == '__main__':
    main()

