import sys, io



import json
import time
import requests
import random
import os
import re
import urllib3
from typing import Optional
from mcp.server.fastmcp import FastMCP
from functools import wraps
import hashlib
import hmac
from datetime import datetime, timedelta
import sys

# 设置标准输出编码为UTF-8
if sys.platform.startswith("win"):
    # 确保 sys.stdout 是 TextIOWrapper 并且有 buffer 属性
    if not hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")
    if not hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8", errors="replace")

# 初始化 MCP 服务器
mcp = FastMCP("ilovepdf_server")


def get_server():
    """随机选择一个可用的 iLovePDF API 服务器"""
    servers = [
        "//api1o.ilovepdf.com",
        "//api2o.ilovepdf.com",
        "//api3o.ilovepdf.com",
        "//api4o.ilovepdf.com",
        "//api5o.ilovepdf.com",
        "//api7o.ilovepdf.com",
        "//api8o.ilovepdf.com",
        "//api9o.ilovepdf.com",
        "//api10o.ilovepdf.com",
        "//api11o.ilovepdf.com",
        "//api12o.ilovepdf.com",
        "//api13o.ilovepdf.com",
        "//api14o.ilovepdf.com",
        "//api16o.ilovepdf.com",
        "//api17o.ilovepdf.com",
        "//api18o.ilovepdf.com",
        "//api19o.ilovepdf.com",
        "//api20o.ilovepdf.com",
        "//api21o.ilovepdf.com",
        "//api22o.ilovepdf.com",
        "//api24o.ilovepdf.com",
        "//api25o.ilovepdf.com",
        "//api26o.ilovepdf.com",
        "//api27o.ilovepdf.com",
        "//api28o.ilovepdf.com",
        "//api29o.ilovepdf.com",
        "//api30o.ilovepdf.com",
        "//api31o.ilovepdf.com",
        "//api32o.ilovepdf.com",
        "//api33o.ilovepdf.com",
        "//api34o.ilovepdf.com",
        "//api35o.ilovepdf.com",
        "//api36o.ilovepdf.com",
        "//api37o.ilovepdf.com",
        "//api39o.ilovepdf.com",
        "//api40o.ilovepdf.com",
        "//api41o.ilovepdf.com",
        "//api42o.ilovepdf.com",
        "//api43o.ilovepdf.com",
        "//api44o.ilovepdf.com",
        "//api45o.ilovepdf.com",
        "//api46o.ilovepdf.com",
        "//api47o.ilovepdf.com",
        "//api48o.ilovepdf.com",
        "//api49o.ilovepdf.com",
        "//api50o.ilovepdf.com",
        "//api51o.ilovepdf.com",
        "//api52o.ilovepdf.com",
        "//api53o.ilovepdf.com",
        "//api54o.ilovepdf.com",
        "//api55o.ilovepdf.com",
        "//api56o.ilovepdf.com",
        "//api57o.ilovepdf.com",
        "//api58o.ilovepdf.com",
        "//api59o.ilovepdf.com",
        "//api60o.ilovepdf.com",
        "//api61o.ilovepdf.com",
        "//api62o.ilovepdf.com",
        "//api63o.ilovepdf.com",
        "//api64o.ilovepdf.com",
        "//api65o.ilovepdf.com",
        "//api66o.ilovepdf.com",
        "//api67o.ilovepdf.com",
        "//api68o.ilovepdf.com",
        "//api69o.ilovepdf.com",
        "//api70o.ilovepdf.com",
        "//api71o.ilovepdf.com",
        "//api72o.ilovepdf.com",
        "//api73o.ilovepdf.com",
        "//api74o.ilovepdf.com",
        "//api75o.ilovepdf.com",
        "//api77o.ilovepdf.com",
        "//api78o.ilovepdf.com",
        "//api79o.ilovepdf.com",
        "//api80o.ilovepdf.com",
        "//api81o.ilovepdf.com",
        "//api82o.ilovepdf.com",
        "//api83o.ilovepdf.com",
        "//api84o.ilovepdf.com",
        "//api85o.ilovepdf.com",
        "//api86o.ilovepdf.com",
        "//api87o.ilovepdf.com",
        "//api88o.ilovepdf.com",
        "//api89o.ilovepdf.com",
        "//api90o.ilovepdf.com",
        "//api91o.ilovepdf.com",
        "//api92o.ilovepdf.com",
        "//api93o.ilovepdf.com",
        "//api94o.ilovepdf.com",
        "//api95o.ilovepdf.com",
        "//api96o.ilovepdf.com",
        "//api97o.ilovepdf.com",
        "//api98o.ilovepdf.com",
        "//api99o.ilovepdf.com",
        "//api100o.ilovepdf.com",
        "//api101o.ilovepdf.com",
        "//api103o.ilovepdf.com",
        "//api104o.ilovepdf.com",
        "//api105o.ilovepdf.com",
        "//api106o.ilovepdf.com",
        "//api107o.ilovepdf.com",
        "//api108o.ilovepdf.com",
        "//api109o.ilovepdf.com",
        "//api110o.ilovepdf.com",
        "//api111o.ilovepdf.com",
        "//api112o.ilovepdf.com",
        "//api113o.ilovepdf.com",
        "//api114o.ilovepdf.com",
        "//api115o.ilovepdf.com"
    ]
    return "https:" + random.choice(servers)

def safe_print(message):
    """安全的打印函数，处理编码问题"""
    try:
        print(message)
    except UnicodeEncodeError:
        # 如果遇到编码错误，使用ASCII编码并忽略无法编码的字符
        if isinstance(message, str):
            print(message.encode('ascii', 'ignore').decode('ascii'))
        else:
            print(str(message).encode('ascii', 'ignore').decode('ascii'))

def extract_js_variables(html_content):
    """
    从HTML内容中提取JavaScript变量

    Args:
        html_content (str): HTML内容

    Returns:
        dict: 包含提取的变量值
    """
    result = {
        'ilovepdfConfig': {
            'token': None,
            'taskId': None
        },
        'siteData': {
            'csrfParam': None,
            'csrfToken': None
        }
    }

    try:
        # 提取 ilovepdfConfig 变量
        ilovepdf_pattern = r'var\s+ilovepdfConfig\s*=\s*({.*?});'
        ilovepdf_match = re.search(ilovepdf_pattern, html_content, re.DOTALL)

        if ilovepdf_match:
            config_str = ilovepdf_match.group(1)
            safe_print("找到 ilovepdfConfig 变量")

            # 提取 token
            token_pattern = r'["\']token["\']\s*:\s*["\']([^"\']+)["\']'
            token_match = re.search(token_pattern, config_str)
            if token_match:
                result['ilovepdfConfig']['token'] = token_match.group(1)
                safe_print(f"token: {result['ilovepdfConfig']['token']}")
        else:
            safe_print("未找到 ilovepdfConfig 变量")
            
        # 提取 taskId
        taskId_pattern = r"ilovepdfConfig\.taskId\s*=\s*'([^']+)'"
        taskId_match = re.search(taskId_pattern, html_content, re.DOTALL)

        if taskId_match:
            result['ilovepdfConfig']['taskId'] = taskId_match.group(1)
            safe_print("提取的 taskId: " + taskId_match.group(1))
        else:
            safe_print("未找到 taskId")

        # 提取 siteData 变量
        sitedata_pattern = r'var\s+siteData\s*=\s*({.*?});'
        sitedata_match = re.search(sitedata_pattern, html_content, re.DOTALL)

        if sitedata_match:
            sitedata_str = sitedata_match.group(1)
            safe_print("找到 siteData 变量")

            # 提取 csrfParam
            param_match = re.search(r"csrfParam:\s*'([^']+)'", sitedata_str)
            # 提取 csrfToken
            token_match = re.search(r"csrfToken:\s*'([^']+)'", sitedata_str)

            if param_match and token_match:
                csrf_param = param_match.group(1)
                csrf_token = token_match.group(1)
                result['siteData']['csrfParam'] = csrf_param
                safe_print(f"csrfParam: {result['siteData']['csrfParam']}")

                result['siteData']['csrfToken'] = csrf_token
                safe_print(f"csrfToken: {result['siteData']['csrfToken']}")
            else:
                safe_print("未找到参数")
        else:
            safe_print("未找到 siteData 变量")

    except Exception as e:
        safe_print(f"提取JS变量失败: {e}")

    return result

def pdf_to_word(session, cookies):
    """获取PDF转Word的配置信息"""
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    url = "https://www.ilovepdf.com/zh-cn/pdf_to_word"
    response = session.get(url, headers=headers, cookies=cookies)
    js_variables = extract_js_variables(response.text)
    return js_variables

def upload(session, authorization, TaskId, Filename, cookies, worker_server, path):
    """上传PDF文件到服务器"""
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Origin": "https://www.ilovepdf.com",
        "Pragma": "no-cache",
        "Referer": "https://www.ilovepdf.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    
    status_url = f"{worker_server}/status.json"
    response = requests.get(status_url, headers=headers)
    safe_print(response.text)

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "Access-Control-Request-Headers": "authorization",
        "Access-Control-Request-Method": "POST",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Origin": "https://www.ilovepdf.com",
        "Pragma": "no-cache",
        "Referer": "https://www.ilovepdf.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    upload_url = f"{worker_server}/v1/upload"
    response = requests.options(upload_url, headers=headers, cookies=cookies)
    safe_print(response)

    headers = {
        "POST": "/v1/upload HTTP/1.1",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": worker_server[8:],
        "Origin": "https://www.ilovepdf.com",
        "Pragma": "no-cache",
        "Referer": "https://www.ilovepdf.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "accept": "application/json",
        "authorization": authorization,
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }

    form_data = {
        'name': Filename,
        'chunk': '0',
        'chunks': '1',
        'task': TaskId,
        'preview': '1',
        'pdfinfo': '0',
        'pdfforms': '0',
        'pdfresetforms': '0',
        'v': 'web.0'
    }

    file_path = path

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'rb') as file:
        files = {
            'file': (Filename, file, 'application/pdf')
        }
        response = session.post(upload_url, headers=headers, data=form_data, files=files, cookies=cookies)
        safe_print(response.status_code)
        return response.json()['server_filename']

def process(session, authorization, TaskId, Filename, cookies, server_filename, worker_server):
    """处理PDF转Word的转换请求"""
    headers = {
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "Authorization": authorization,
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Origin": "https://www.ilovepdf.com",
        "Pragma": "no-cache",
        "Referer": "https://www.ilovepdf.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    
    process_url = f"{worker_server}/v1/process"
    form_data = {
        "convert_to": "docx",
        "output_filename": Filename[:-4],
        "packaged_filename": "ilovepdf_converted",
        "ocr": "0",
        "task": TaskId,
        "tool": "pdfoffice",
        "files[0][server_filename]": server_filename,
        "files[0][filename]": Filename
    }

    response = session.post(process_url, headers=headers, data=form_data, cookies=cookies)
    return response.status_code

def upload_file(file_content, suggested_name):
    """
    上传文件内容到指定的服务器
    
    Args:
        file_content (bytes): 要上传的文件内容
        suggested_name (str): 建议的文件名
    
    Returns:
        dict: 上传结果
    """
    upload_url = "http://cninct.com/upfast/group4/upload"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    
    try:
        if not file_content:
            safe_print("文件内容为空")
            return {"success": False, "error": "文件内容为空"}
        
        files = {
            'file': (suggested_name, file_content, 'application/octet-stream')
        }
        
        safe_print(f"开始上传文件到: {upload_url}")
        response = requests.post(upload_url, headers=headers, files=files, timeout=60)
        
        if response.status_code == 200:
            safe_print(f"文件上传成功: {suggested_name}")
            try:
                local_url = response.text
                local_url = local_url.replace(
                    "http://192.168.1.241:8064/group4/default",
                    "http://cninct.com/fast4"
                ) + "?download=0"
                return {"success": True, "data": local_url}
            except:
                return {"success": False, "error": "文件上传成功，但获取本地URL失败"}
        else:
            return {"success": False, "error": f"上传失败，状态码: {response.status_code}"}
            
    except Exception as e:
        safe_print(f"上传过程中发生错误: {e}")
        return {"success": False, "error": str(e)}

def go_download(session, TaskId, worker_server, filename, cookies):
    """下载转换后的Word文件并上传到指定服务器"""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    downloadUrl = f"{worker_server}/v1/download/{TaskId}"
    safe_print(downloadUrl)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,fr;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    
    response = session.get(downloadUrl, headers=headers, cookies=cookies, verify=False, timeout=120)
    if response.status_code == 200:
        converted_filename = filename.replace('.pdf', '.docx') if filename.endswith('.pdf') else filename + '.docx'
        
        upload_result = upload_file(response.content, converted_filename)
        if upload_result["success"]:
            safe_print("文件已成功上传到服务器")
            return {"success": True, "message": "文件转换并上传成功", "data": upload_result["data"]}
        else:
            return {"success": False, "error": f"文件上传失败: {upload_result['error']}"}
    else:
        return {"success": False, "error": f"下载失败，状态码: {response.status_code}"}

@mcp.tool()
async def convert_pdf_to_word(
    filename: str,
    file_path: str,
    auth_token: Optional[str] = None
) -> str:
    """
    PDF转Word文档工具
    
    功能描述：
    使用iLovePDF在线服务将PDF文件转换为Word文档（.docx格式）。
    该工具支持自动上传、转换和下载，转换完成后会将结果文件上传到指定服务器并返回下载链接。
    
    支持的转换功能：
    
    1. PDF到Word转换
       - 支持标准PDF文档转换
       - 保持原文档格式和布局
       - 输出为.docx格式
    
    2. 自动化处理流程
       - 自动获取转换令牌
       - 上传PDF文件到iLovePDF服务器
       - 执行转换处理
       - 下载转换后的Word文档
       - 上传到指定服务器获取永久链接
    
    3. 错误处理和重试机制
       - 自动选择可用的API服务器
       - 完整的错误处理和状态反馈
       - 支持大文件转换（120秒超时）
    
    使用场景：
    - 文档格式转换需求
    - 批量PDF文档处理
    - 在线文档转换服务集成
    - 自动化文档处理流程
    
    技术特点：
    - 使用多个API服务器负载均衡
    - 支持大文件处理
    - 自动文件上传和下载
    - 返回永久访问链接
    
    Args:
        filename (str): PDF文件名，必须包含.pdf扩展名
                       示例: "document.pdf", "报告.pdf"
        file_path (str): PDF文件的完整路径，必须是存在的文件路径
                        示例: "C:/Documents/file.pdf", "/home/user/document.pdf"
    
    Returns:
        str: JSON格式的转换结果，包含以下字段：
            - status (str): 转换状态，"success" 表示成功，"error" 表示失败
            - message (str): 转换结果描述信息
            - data (str): 成功时返回转换后Word文档的下载链接
            - error (str): 失败时返回错误信息描述
            
        成功示例:
        {
            "status": "success",
            "message": "文件转换并上传成功",
            "data": "http://cninct.com/fast4/M00/00/01/document.docx?download=0"
        }
        
        失败示例:
        {
            "status": "error", 
            "error": "文件不存在: /path/to/file.pdf"
        }
        
    Raises:
        FileNotFoundError: 当指定的PDF文件路径不存在时
        ConnectionError: 当网络连接失败或服务器不可用时
        TimeoutError: 当转换过程超时时
        Exception: 其他转换过程中的异常
    """
    try:
        # 验证文件路径
        if not os.path.exists(file_path):
            return json.dumps({
                "status": "error",
                "error": f"文件不存在: {file_path}"
            }, ensure_ascii=False, indent=2)
        
        # 验证文件扩展名
        if not filename.lower().endswith('.pdf'):
            return json.dumps({
                "status": "error", 
                "error": "文件必须是PDF格式（.pdf扩展名）"
            }, ensure_ascii=False, indent=2)
        
        cookies = {
            "_ga_44KQ8HETWT": "GS2.1.s1752809201$o1$g0$t1752809201$j60$l0$h0; lastTool=pdfoffice"
        }
        worker_server = get_server()
        session = requests.session()
        
        # 获取转换配置
        try:
            js_variables = pdf_to_word(session, cookies)
            if not js_variables['ilovepdfConfig']['token'] or not js_variables['ilovepdfConfig']['taskId']:
                return json.dumps({
                    "status": "error",
                    "error": "获取转换配置失败，无法获取有效的token或taskId"
                }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"获取转换配置失败: {str(e)}"
            }, ensure_ascii=False, indent=2)
        
        # 上传PDF文件
        try:
            server_filename = upload(
                session, 
                'Bearer ' + js_variables['ilovepdfConfig']['token'],
                js_variables['ilovepdfConfig']['taskId'], 
                filename,
                cookies,
                worker_server,
                file_path
            )
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"文件上传失败: {str(e)}"
            }, ensure_ascii=False, indent=2)
        
        # 处理转换请求
        try:
            process_result = process(
                session, 
                'Bearer ' + js_variables['ilovepdfConfig']['token'],
                js_variables['ilovepdfConfig']['taskId'],
                filename,
                cookies,
                server_filename,
                worker_server
            )
            safe_print(f"转换处理状态码: {process_result}")
            
            if process_result != 200:
                return json.dumps({
                    "status": "error",
                    "error": f"转换处理失败，状态码: {process_result}"
                }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"转换处理失败: {str(e)}"
            }, ensure_ascii=False, indent=2)
        
        # 下载转换后的文件
        try:
            result = go_download(
                session,
                js_variables['ilovepdfConfig']['taskId'],
                worker_server,
                filename,
                cookies
            )
            
            if result["success"]:
                return json.dumps({
                    "status": "success",
                    "message": result["message"],
                    "data": result["data"]
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "status": "error",
                    "error": result["error"]
                }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"下载转换文件失败: {str(e)}"
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"PDF转Word转换失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

def main() -> None:
    print("[PDF to Word MCP] Starting server...")
    mcp.run(transport='stdio')
