from mignonFramework import Curl2Reuqest
from mignonFramework import start

if __name__ == '__main__':
    data = """
    curl 'http://localhost:20257/achiInfo/getPage' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5' \
  -H 'Authorization: Basic YWRtaW46Z29TQ0lAMTIz' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -b 'Idea-aafc9cbc=d41f03a7-ebb0-4b0a-aeee-b9ffd8c1712e; Webstorm-5dc34d03=df4c5011-f515-4d7d-84c5-d95bbcb2e1ab; Pycharm-24fe29c8=4089f3f5-511c-4328-b4ac-efb5fb54a351; Webstorm-5dc34d04=271a2c70-318b-41a2-9d95-40e1c34cbf19; Pycharm-24fe29c9=19f2fc1c-89c5-42b5-bee5-aaf111904cdc; JSESSIONID=FvM3lKq6MshZlNNaMtT9vem7yHh_Va-BwONYLKvu' \
  -H 'Origin: http://localhost:20257' \
  -H 'Referer: http://localhost:20257/doc.html' \
  -H 'Request-Origion: Knife4j' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw $'{\n  "data": {\n    "linkNames": "",\n    "achiTransferMethodName": "",\n    "generalKeyword": ""\n  },\n  "pageNo": 1,\n  "pageSize": 1,\n  "endTime": "",\n  "startTime": "",\n  "sort": [],\n  "order": ""\n}'
    """

    start()