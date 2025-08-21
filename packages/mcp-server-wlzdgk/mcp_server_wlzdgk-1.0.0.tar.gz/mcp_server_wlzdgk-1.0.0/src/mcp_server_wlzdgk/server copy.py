# -*- coding: utf-8 -*-
import base64
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import sys
import requests
import execjs
import json
import os
import pymysql
from enum import Enum
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

class WlzdgkTools(str, Enum):
    UNBIND_WLZDGK = "unbind_wlzdgk"
    BIND_WLZDGK = "bind_wlzdgk"
    ALTER_WLZDGK = "alter_wlzdgk"


# 数据库操作
class DB():
    # 在setting.databases我已创建了数据库链接相关信息，在下方调用时直接写语句即可
    def __init__(self, host='host.docker.internal', port=3306, user='root', passwd='abc123456', db='wuhu_data'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd)
        # 创建游标
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()

# 查询数据
def select_data(select_sql):
    with DB() as db:
        db.execute(select_sql)
        data_list = db.fetchall()
        return data_list

def get_headers():
    sel_sql = "select token from db_token where sys_name = '网络终端边界准人系统access_token'"
    access_token = select_data(sel_sql)
    access_token = access_token[0].get('token')

    sel_sql = "select token from db_token where sys_name = '网络终端边界准人系统refresh_token'"
    refresh_token = select_data(sel_sql)
    refresh_token = refresh_token[0].get('token')

    cj_headers = {
        'APPORGID': '17',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'Bearer ' + access_token,
        'Connection': 'keep-alive',
        'Cookie': 'gwxt_token='+access_token+'; refreshLoginToken='+refresh_token,
        'Host': '10.138.189.220:16060',
        'Referer': 'https://10.138.189.220:16060/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    return cj_headers


def get_key():
    sel_sql = "select token from db_token where sys_name = '网络终端边界准人系统key'"
    key = select_data(sel_sql)
    key = key[0].get('token')
    return key


def decrypt(encrypted_base64, key):
    # 将密钥转换为字节
    key_bytes = key.encode('utf-8')

    # 解码Base64密文
    encrypted_bytes = base64.b64decode(encrypted_base64)

    # 创建AES密码器
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # 解密并移除PKCS7填充
    decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)

    # 转换为utf-8字符串
    return decrypted_bytes.decode('utf-8')


# 查询ip资源管理信息
def get_ipzygl(mac, ip, ctx, headers, key):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        params = {
            'ip': '',
            'tmnMac': '',
            'resState': '',
            'vlanId': '',
            'pageSize': 10,
            'pageNum': 1
        }
        if mac:
            params['tmnMac'] = mac
        if ip:
            params['ip'] = ip
        url = 'https://10.138.189.220:16060/api/tms/ipAddress'
        main_url_html = requests.get(url=url, params=params, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200':
            datas = json_result.get('data')['records']
            if datas:
                return datas[0]
            else:
                return None
        else:
            return "程序报错,请重试！"
    except Exception as e:
        return "程序报错,请重试！"


# 查询交换机信息
def get_jhjxx(ctx, headers, key, switchId, switchName):
    jhjxx_rows = []
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        url = 'https://10.138.189.220:16060/api/tms/allocations/portData'
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200':
            datas = json_result.get('data')
            if datas:
                for data in datas:
                    jhjxx_rows.append([data['id'], data['text']])
                    children_1s = data['children']
                    if children_1s:
                        for children_1 in children_1s:
                            jhjxx_rows.append([children_1['id'], children_1['text']])
                            children_2s = children_1['children']
                            if children_2s:
                                for children_2 in children_2s:
                                    jhjxx_rows.append([children_2['id'], children_2['text']])
                                    children_3s = children_2['children']
                                    if children_3s:
                                        for children_3 in children_3s:
                                            jhjxx_rows.append([children_3['id'], children_3['text']])
                                            children_4s = children_3['children']
                                            if children_4s:
                                                for children_4 in children_4s:
                                                    jhjxx_rows.append([children_4['id'], children_4['text']])
        if [switchId, switchName] in jhjxx_rows:
            return False
        else:
            return True
    except Exception as e:
        return "程序报错,请重试！"


# 交换机端口信息
def get_jhjdkxx(ctx, headers, key, switchId, portName, vlanNumber):
    jhjdkxx_rows = []
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        url = 'https://10.138.189.220:16060/api/tms/allocations/port?switchId='+switchId
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200':
            datas = json_result.get('data')
            if datas:
                for data in datas:
                    jhjdkxx_rows.append([data['portName'], data['vlanNumber']])
        if [portName, vlanNumber] in jhjdkxx_rows:
            return False
        else:
            return True
    except Exception as e:
        return "程序报错,请重试！"


# 查询资源分配信息
def get_zyfpxx(ctx, headers, key, ipResId):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        url = 'https://10.138.189.220:16060/api/tms/allocations/' + str(ipResId)
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200':
            datas = json_result.get('data')
            if datas:
                return datas
        return None
    except Exception as e:
        return "程序报错,请重试！"




# 解绑操作
def unbind(ctx, headers, key, ipResId):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        url = 'https://10.138.189.220:16060/api/tms/allocations?ipResId='+str(ipResId)
        main_url_html = requests.delete(url=url, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200' and json_result['msg'] == '处理成功':
            return "解绑成功"
        else:
            return "解绑失败"
    except Exception as e:
        return "程序报错,请重试！"



# 绑定操作
def bind(ctx, headers, key, ip, mac, switchId, switchName, portName, vlanNumber, tmnType, zyfpxx, ipzygl_ip):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        params = {
            "ip": ip,
            "tmnMac": mac,
            "vlanNumber": vlanNumber,
            "switchId": switchId,
            "switchName": switchName,
            "portName": portName,
            "tmnType": tmnType,
            "phone": zyfpxx['phone'],
            "panel": zyfpxx['panel'],
            "ipResId": zyfpxx['ipResId'],
            "staffId": zyfpxx['staffId'],
            "room": zyfpxx['room'],
            "remark": zyfpxx['remark'],
            "tmnId": zyfpxx['tmnId'],
            "vlanId": ipzygl_ip['vlanId'],
            "block": zyfpxx['block'],
            "resState": 4,
            "portDesc": zyfpxx['portDesc'],
            "orgId": zyfpxx['orgId'],
            "deptId": zyfpxx['deptId'],
            "confirmBind": False,
            "qzBind": False,
            "validDate": "2099-12-29T16:00:00.000Z",
            "apply": {"summary": "", "fileList": []}
        }
        url = 'https://10.138.189.220:16060/api/tms/allocations'
        main_url_html = requests.post(url=url, json=params, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200' and json_result['msg'] == '处理成功':
            return "绑定成功"
        else:
            return "绑定失败"
    except Exception as e:
        return "程序报错,请重试！"


# 绑定完之后更新
def update_gengxin(ctx, headers, key, switchIds):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        url = 'https://10.138.189.220:16060/api/tms/analys/scan?switchIds=' + str(switchIds)
        main_url_html = requests.post(url=url, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
    except Exception as e:
        print(e)



# 更新绑定操作
def alter(ctx, headers, key, ip, mac, tmnType, zyfpxx, ipzygl_ip):
    try:
        youo_key = ctx.call("encryptLong", key)
        headers['youo_key'] = youo_key
        headers['Cookie'] = headers['Cookie'] + '; expirationTime=' + str(int(time.time() * 1000))
        params = {
            "ip": ip,
            "staffId": zyfpxx['staffId'],
            "room":zyfpxx['room'],
            "remark":zyfpxx['remark'],
            "portName":zyfpxx['portName'],
            "phone":zyfpxx['phone'],
            "panel":zyfpxx['panel'],
            "ipResId":zyfpxx['ipResId'],
            "tmnId":zyfpxx['tmnId'],
            "switchId":zyfpxx['switchId'],
            "block":zyfpxx['block'],
            "resState":zyfpxx['resState'],
            "tmnType": tmnType,
            "tmnMac": mac,
            "portDesc":zyfpxx['portDesc'],
            "validDate":zyfpxx['validDate'],
            "vlanId":ipzygl_ip['vlanId'],
            "orgId":zyfpxx['orgId'],
            "deptId":zyfpxx['deptId'],
            "vlanNumber":zyfpxx['vlanNumber'],
            "confirmBind": False,
            "qzBind": False,
            "apply":{"summary":"","fileList":[]}
        }
        url = 'https://10.138.189.220:16060/api/tms/allocations'
        main_url_html = requests.put(url=url, json=params, headers=headers, verify=False)
        response = main_url_html.text
        decrypt_str = decrypt(response, key)
        json_result = json.loads(decrypt_str)
        if json_result['code'] == '200' and json_result['msg'] == '处理成功':
            return "更新绑定成功"
        else:
            return "更新绑定失败"
    except Exception as e:
        return "程序报错,请重试！"
    

class WlzdgkServer:
    # 解绑
    def update_unbind(self, mac: str, ip: str)->str:
        headers = get_headers()
        key = get_key()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_file_path = os.path.join(current_dir, "2_wlzd.js")

        with open(js_file_path, "r", encoding="UTF-8") as file:
            js_code = file.read()
        # 执行 JavaScript 代码
        ctx = execjs.compile(js_code)

        # 查询ip资源情况
        ipzygl = get_ipzygl(mac, ip, ctx, headers, key)

        if ipzygl == "程序报错,请重试！":
            return ipzygl
        if ipzygl:
            if ipzygl['resState'] == 4:
                msg = unbind(ctx, headers, key, ipzygl['ipResId'])
                return msg
            else:
                return "此ip或mac没有绑定,无需解绑"
        else:
            return "无法查到此ip或mac,无需解绑"
        
        # 绑定
    def update_bind(self, mac: str, ip: str, switchId: str, switchName: str, portName: str, vlanNumber: str, tmnType: str)->str:
        headers = get_headers()
        key = get_key()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_file_path = os.path.join(current_dir, "2_wlzd.js")

        with open(js_file_path, "r", encoding="UTF-8") as file:
            js_code = file.read()
        # 执行 JavaScript 代码
        ctx = execjs.compile(js_code)

        # 查询ip资源情况
        ipzygl_mac = get_ipzygl(mac, "", ctx, headers, key)
        if ipzygl_mac == "程序报错,请重试！":
            return ipzygl_mac
        if ipzygl_mac:
            return "此mac已经绑定,ip为" + ipzygl_mac['ip'] + ",绑定失败"
        ipzygl_ip = get_ipzygl("", ip , ctx, headers, key)
        if ipzygl_ip == "程序报错,请重试！":
            return ipzygl_ip
        if ipzygl_ip is None:
            return "无法查到此ip，绑定失败"
        if ipzygl_ip and ipzygl_ip['resState'] == 4:
            return "此ip已分配，绑定失败"
        if ipzygl_ip and ipzygl_ip['resState'] == 5:
            return "此ip为网关地址，绑定失败"
        # 查询交换机信息
        jhjxx = get_jhjxx(ctx, headers, key, switchId, switchName)
        if jhjxx == "程序报错,请重试！":
            return jhjxx
        if jhjxx:
            return "交换机信息有误，绑定失败"

        # 查询交换机端口信息
        jhjdkxx = get_jhjdkxx(ctx, headers, key,switchId, portName, vlanNumber)
        if jhjdkxx == "程序报错,请重试！":
            return jhjdkxx
        if jhjdkxx:
            return "交换机端口信息有误，绑定失败"

        # 查询资源分配信息
        zyfpxx = get_zyfpxx(ctx, headers, key, ipzygl_ip['ipResId'])
        if zyfpxx == "程序报错,请重试！":
            return zyfpxx
        if zyfpxx is None:
            return "资源信息有误，绑定失败"

        msg = bind(ctx, headers, key, ip, mac, switchId, switchName, portName, vlanNumber, tmnType, zyfpxx, ipzygl_ip)
        time.sleep(3)
        update_gengxin(ctx, headers, key, switchId)
        return msg

    # 更新绑定
    def update_alter(self, mac: str, ip: str, tmnType: str)->str:
        headers = get_headers()
        key = get_key()
        # headers = get_headers()
        # key = get_key()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_file_path = os.path.join(current_dir, "2_wlzd.js")

        with open(js_file_path, "r", encoding="UTF-8") as file:
            js_code = file.read()
        # 执行 JavaScript 代码
        ctx = execjs.compile(js_code)

        # 查询ip资源情况
        ipzygl_mac = get_ipzygl(mac, "", ctx, headers, key)
        if ipzygl_mac == "程序报错,请重试！":
            return ipzygl_mac
        if ipzygl_mac and ipzygl_mac['ip'] != ip:
            return "此mac已经绑定,ip为" + ipzygl_mac['ip'] + ",更新绑定失败"
        ipzygl_ip = get_ipzygl("", ip, ctx, headers, key)
        if ipzygl_ip == "程序报错,请重试！":
            return ipzygl_ip
        if ipzygl_ip is None:
            return "无法查到此ip，更新绑定失败"
        if ipzygl_ip and ipzygl_ip['resState'] != 4:
            return "此ip未分配，更新绑定失败"

        # 查询资源分配信息
        zyfpxx = get_zyfpxx(ctx, headers, key, ipzygl_ip['ipResId'])
        if zyfpxx == "程序报错,请重试！":
            return zyfpxx
        if zyfpxx is None:
            return "资源信息有误，绑定失败"

        msg = alter(ctx, headers, key, ip, mac, tmnType, zyfpxx, ipzygl_ip)
        time.sleep(3)
        update_gengxin(ctx, headers, key, zyfpxx['switchId'])
        return msg

    
async def serve() -> None:
    server = Server("mcp-wlzdgk")
    wlzdgk_server = WlzdgkServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=WlzdgkTools.ALTER_WLZDGK.value,
                description="终端绑定更新",
                inputSchema={
                    "type": "object",
                    "properties": {
                         "mac": {
                            "type": "string",
                            "description": "MAC address",
                        },
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address",
                        },
                        "tmnType": {
                            "type": "string",
                            "description": "设备类型",
                        }
                    },
                    "required": ["mac","ip", "tmnType"]
                },
            ),
            Tool(
                name=WlzdgkTools.BIND_WLZDGK.value,
                description="网络终端绑定",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mac": {
                            "type": "string",
                            "description": "MAC address",
                        },
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address",
                        },
                        "switchId": {
                            "type": "string",
                            "description": "交换机编号",
                        },
                        "switchName": {
                            "type": "string",
                            "description": "交换机名称",
                        },
                        "portName": {
                            "type": "string",
                            "description": "交换机接口名称",
                        },
                        "vlanNumber": {
                            "type": "string",
                            "description": "交换机的vlan编号",
                        },
                         "tmnType": {
                            "type": "string",
                            "description": "设备类型",
                        },
                    },
                    "required": ["mac","ip","switchId","switchName","portName","vlanNumber","tmnType"]
                },
            ),
            Tool(
                name=WlzdgkTools.UNBIND_WLZDGK.value,
                description="终端网络阻断",
                inputSchema={
                    "type": "object",
                    "properties": {
                         "mac": {
                            "type": "string",
                            "description": "MAC address",
                        },
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address",
                        }
                    },
                    "required": ["mac", "ip"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                case WlzdgkTools.ALTER_WLZDGK.value:
                    if not all(k in arguments for k in ["mac","ip", "tmnType"]):
                        raise ValueError("Missing required arguments")
                    result = wlzdgk_server.update_alter(arguments["mac"], arguments["ip"], arguments["tmnType"])

                case WlzdgkTools.BIND_WLZDGK.value:
                    if not all(k in arguments for k in ["mac","ip","switchId","switchName","portName","vlanNumber","tmnType"]):
                        raise ValueError("Missing required arguments")
                    result = wlzdgk_server.update_bind(arguments["mac"], arguments["ip"], arguments["switchId"], 
                                                                         arguments["switchName"], arguments["portName"], arguments["vlanNumber"], arguments["tmnType"],)
                case WlzdgkTools.UNBIND_WLZDGK.value:
                    if not all(k in arguments for k in ["mac","ip"]):
                        raise ValueError("Missing required arguments")
                    result = wlzdgk_server.update_unbind(arguments["mac"], arguments["ip"])
                case _:
                    raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            raise ValueError(f"Error processing mcp-server-wlzdgk query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)



