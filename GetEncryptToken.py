# -*- coding: UTF-8 -*-
import requests as req
import json, sys, time, random
import base64
from Crypto.Cipher import AES
import hashlib


class aescrypt():
    def __init__(self,key,model,iv,encode_):
        self.encode_ = encode_
        self.model =  {'ECB':AES.MODE_ECB,'CBC':AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key,self.model)
        elif model == 'CBC':
            self.aes = AES.new(self.key,self.model,iv)

    def add_16(self,par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    def aesencrypt(self,text):
        text = self.add_16(text)
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    def aesdecrypt(self,text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).strip('\0')

args = sys.argv[1:]
password=str(hashlib.md5(args[0].encode("utf-8")).hexdigest()[8:-8])
args=args[1:]
args_len = int((len(sys.argv) - 1) / 2)
id_list = args[:args_len]
secret_list = args[args_len:]
aes = aescrypt(password,'ECB','','utf8')


def gettoken(refresh_token):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'refresh_token',
            'refresh_token': refresh_token, 
            'client_id': id_list[a],
            'client_secret': secret_list[a],
            'redirect_uri': 'http://localhost:53682/'}
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers)
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    with open(path, 'w+') as f:
        f.write(aes.aesencrypt(refresh_token))


def main():
    fo = open(path, "r+")
    refresh_token = fo.read()
    fo.close()
    access_token = gettoken(refresh_token)


for a in range(0, len(id_list)):
    path = sys.path[0] + r'/token/' + str(a) + '.txt'
    main()