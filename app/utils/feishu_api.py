import requests
import json
import time

class FeishuAPI:
    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or "cli_a1a1a1a1a1a1a1a1"
        self.app_secret = app_secret or "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.token_expire_time = 0

    def get_access_token(self):
        current_time = time.time()
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                self.token_expire_time = current_time + result.get("expire", 7200) - 100
                return self.access_token
            else:
                raise Exception(f"获取token失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"获取access_token异常: {str(e)}")

    def add_record(self, table_id, record):
        token = self.get_access_token()
        url = f"{self.base_url}/bitable/v1/apps/bcnrsnl3m9wk/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fields": record
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("record", {})
            else:
                raise Exception(f"添加记录失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"添加记录异常: {str(e)}")

    def update_record(self, table_id, record_id, record):
        token = self.get_access_token()
        url = f"{self.base_url}/bitable/v1/apps/bcnrsnl3m9wk/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fields": record
        }
        
        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("record", {})
            else:
                raise Exception(f"更新记录失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"更新记录异常: {str(e)}")

    def get_record(self, table_id, record_id):
        token = self.get_access_token()
        url = f"{self.base_url}/bitable/v1/apps/bcnrsnl3m9wk/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("record", {})
            else:
                raise Exception(f"获取记录失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"获取记录异常: {str(e)}")

    def list_records(self, table_id, page_size=100, page_token=""):
        token = self.get_access_token()
        url = f"{self.base_url}/bitable/v1/apps/bcnrsnl3m9wk/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "page_size": page_size,
            "page_token": page_token
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {})
            else:
                raise Exception(f"查询记录失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"查询记录异常: {str(e)}")