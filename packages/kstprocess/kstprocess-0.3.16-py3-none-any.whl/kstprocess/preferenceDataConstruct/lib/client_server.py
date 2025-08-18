import requests
import json
import random
from collections import deque


#### 设置访客模型 ####
class ClientServer:
    def __init__(self, config) -> None:
        self.domian = config["client_config"]["domain"]
        self.origin = config["client_config"]["origin"]
        self.domian_cn_map = {"paediastric": "儿科", 
                              "hair": "植发科", 
                              "andrology": "男科", 
                              "白癜风": "vitiligo"}
        self.client_server_url = config["client_config"]["client_server_url"]  # 原始访客模型 URL
        self.hanflow_url = config["client_config"].get("hanflow_url", "https://test-hanflow.kuaishang.cn/v1/workflows/run")  # Hanflow API URL
        self.authorization_token = config["client_config"].get("authorization_token", "Bearer app-tELzDoUVJgWT2JFEkg2fmQ7t")  # Hanflow 授权 Token
        self.cookie = config["client_config"].get("cookie", "SERVERID=24161a1ce1fde9d622cae03a6d54cbca")  # Hanflow Cookie
        self.use_hanflow = config["client_config"].getboolean("use_hanflow", fallback=False)  # 是否使用 Hanflow 访客模型
        self.role_content_queue = deque(maxlen=100)  # 保存最近 100 个对话 ID 的访客画像

    def sft_client_return(self, dialogrecord: list) -> str:
        """
        原始访客模型请求方法
        """
        post_msg = {
            "dialogId": "1707019307",
            "domain": self.domian,
            "proxyType": "half",
            "promptInfo": "",
            "basicInfo": {},
            "utterance": "",
              "pushUrl": "http://dkf-kicp.kuaishang.cn/serviceRobot/chatGPT/callback",
            "task_type": "generate",
            "keyword": "",
            "control_role": "CLIENT",
            "extensionData": "0",
            "dialogRecord": dialogrecord
        }
        response = requests.post(self.client_server_url, json=post_msg)
        generate_text_list = json.loads(response.text)["data"]
        sft_client_response = random.choices(generate_text_list, k=1)[0].replace("[conti]", "<sep>")
        return sft_client_response

    def hanflow_client_return(self, dialogrecord: list, dialog_id: str, role_content: str = None) -> str:
        """
        Hanflow 访客模型请求方法
        """
        # 查找当前对话 ID 的访客画像
        current_role_content = None
        for item in self.role_content_queue:
            if item["dialog_id"] == dialog_id:
                current_role_content = item["role_content"]
                break

        # 如果 role_content 为空，则使用保存的访客画像
        if role_content is None:
            role_content = current_role_content

        payload = json.dumps({
            "inputs": {
                "dialogRecord": json.dumps(dialogrecord),  # 将对话记录转换为 JSON 字符串
                "dialogId": dialog_id,
                "domain": self.domian,
                "origin": self.origin,
                "domain_cn":  self.domian_cn_map[self.domian],
                "role_content": role_content if role_content else ""  # 如果 role_content 为空，则发送空值
            },
            "response_mode": "blocking",
            "user": "abc-123"
        })
        headers = {
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',
            'Cookie': self.cookie
        }
        response = requests.post(self.hanflow_url, headers=headers, data=payload)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            # 如果响应中包含 role_content，则更新或添加到队列
            if "role_content" in response_data["data"]["outputs"]:
                new_role_content = response_data["data"]["outputs"]["role_content"]
                # 移除旧的访客画像（如果存在）
                self.role_content_queue = deque(
                    [item for item in self.role_content_queue if item["dialog_id"] != dialog_id],
                    maxlen=100
                )
                # 添加新的访客画像
                self.role_content_queue.append({"dialog_id": dialog_id, "role_content": new_role_content})
            init_response_text = json.loads(response.text)["data"]["outputs"]["data"].replace("我继续回复：", "")
            candidates_text = [init_response_text for _ in range(10)]
            return   random.choices(candidates_text, k=1)[0]
        else:
            raise Exception(f"Hanflow request failed with status code {response.status_code}: {response.text}")


    def get_client_response(self, dialogrecord: list, dialog_id: str = None, role_content: str = None) -> str:
        """
        根据配置选择使用哪种访客模型
        """
        if self.use_hanflow:
            if not dialog_id:
                raise ValueError("dialog_id is required when using Hanflow.")
            return self.hanflow_client_return(dialogrecord, dialog_id, role_content)
        else:
            return self.sft_client_return(dialogrecord)