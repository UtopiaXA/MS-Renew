# -*- coding: UTF-8 -*-
import requests as req
import json, sys, time, random

# 先注册azure应用,确保应用有以下权限:
# files:	Files.Read.All、Files.ReadWrite.All、Sites.Read.All、Sites.ReadWrite.All
# user:	User.Read.All、User.ReadWrite.All、Directory.Read.All、Directory.ReadWrite.All
# mail:  Mail.Read、Mail.ReadWrite、MailboxSettings.Read、MailboxSettings.ReadWrite
# 注册后一定要再点代表xxx授予管理员同意,否则outlook api无法调用

randomapi = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
path = sys.path[0] + r'/randomapi.txt'

random.shuffle(randomapi)
str2 = ','.join([str(x) for x in randomapi])
with open(path, 'w+') as f:
    f.write(str2)
