import requests
import json

# 由 Mignon Rex 的 MignonFramework.CurlToRequestsConverter 生成
# Have a good Request

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5",
    "Authorization": "Basic YWRtaW46Z29TQ0lAMTIz",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "http://localhost:20257",
    "Referer": "http://localhost:20257/doc.html",
    "Request-Origion": "Knife4j",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

cookies = {
    "Idea-aafc9cbc": "d41f03a7-ebb0-4b0a-aeee-b9ffd8c1712e",
    "Webstorm-5dc34d03": "df4c5011-f515-4d7d-84c5-d95bbcb2e1ab",
    "Pycharm-24fe29c8": "4089f3f5-511c-4328-b4ac-efb5fb54a351",
    "Webstorm-5dc34d04": "271a2c70-318b-41a2-9d95-40e1c34cbf19",
    "Pycharm-24fe29c9": "19f2fc1c-89c5-42b5-bee5-aaf111904cdc",
    "JSESSIONID": "FvM3lKq6MshZlNNaMtT9vem7yHh_Va-BwONYLKvu"
}

json_data = {
    "data": {
        "linkNames": "",
        "achiTransferMethodName": "",
        "generalKeyword": ""
    },
    "pageNo": 1,
    "pageSize": 1,
    "endTime": "",
    "startTime": "",
    "sort": [],
    "order": ""
}

url = "http://localhost:20257/achiInfo/getPage"

response = requests.post(
    url,
    headers=headers,
    cookies=cookies,
    json=json_data
)

# The following print statements are for debugging and are not part of the core request logic.
print(f"状态码: {response.status_code}")
try:
    print("响应 JSON:", response.json())
except json.JSONDecodeError:
    print("响应文本:", response.text)