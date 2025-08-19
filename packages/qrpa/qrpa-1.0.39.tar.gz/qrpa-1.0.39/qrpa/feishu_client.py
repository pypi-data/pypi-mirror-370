# -*- coding: UTF-8 -*-
import requests
import json
import time
import base64, os
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any

from .fun_base import log

class FeishuClient:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_access_token = None
        self.token_expire_time = 0
        self._refresh_token()

    def _refresh_token(self):
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id"    : self.app_id,
            "app_secret": self.app_secret
        }
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get("code") == 0:
            self.tenant_access_token = response_data.get("tenant_access_token")
            expire_seconds = response_data.get("expire", 7200)
            self.token_expire_time = time.time() + expire_seconds - 300
        else:
            raise Exception(f"获取token失败: {response_data.get('msg', '未知错误')}")

    def _ensure_valid_token(self):
        if not self.tenant_access_token or time.time() > self.token_expire_time:
            self._refresh_token()

    def _make_request(self, method: str, url: str, **kwargs):
        self._ensure_valid_token()

        headers = kwargs.get('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.tenant_access_token}',
            'Content-Type' : 'application/json; charset=utf-8'
        })
        kwargs['headers'] = headers

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get("code") == 0:
            log('----------------------------------------------------')
            log(f'url: {url}')
            log(f'kwargs: {json.dumps(kwargs, ensure_ascii=False, indent=4, sort_keys=True)}')
            log(f'data: {response_data["data"]}')
            log('====================================================')
            return response_data.get("data", {})
        else:
            raise Exception(f"API调用失败: {response_data.get('msg', '未知错误')}")

    # ==================== 文件夹操作 ====================

    def get_root_folder_meta(self):
        url = f"{self.base_url}/drive/explorer/v2/root_folder/meta"
        return self._make_request('GET', url)

    def create_folder(self, name: str, parent_folder_token: str = ""):
        url = f"{self.base_url}/drive/v1/files/create_folder"
        payload = {
            "name"        : name,
            "folder_token": parent_folder_token
        }
        return self._make_request('POST', url, json=payload)

    def list_folder_files(self, folder_token: str, page_size: int = 20, page_token: str = None):
        url = f"{self.base_url}/drive/v1/files"
        params = {
            "folder_token": folder_token,
            "page_size"   : page_size
        }
        if page_token:
            params["page_token"] = page_token
        return self._make_request('GET', url, params=params)

    def delete_file(self, file_token: str, file_type: str = "file"):
        url = f"{self.base_url}/drive/v1/files/{file_token}"
        params = {"type": file_type}
        return self._make_request('DELETE', url, params=params)

    # ==================== 表格操作 ====================

    def create_spreadsheet(self, title: str, folder_token: str):
        url = f"{self.base_url}/sheets/v3/spreadsheets"
        payload = {
            "title"       : title,
            "folder_token": folder_token
        }
        return self._make_request('POST', url, json=payload)

    def get_spreadsheet(self, spreadsheet_token: str, user_id_type: str = "open_id"):
        url = f"{self.base_url}/sheets/v3/spreadsheets/{spreadsheet_token}"
        params = {"user_id_type": user_id_type}
        return self._make_request('GET', url, params=params)

    def query_sheets(self, spreadsheet_token: str):
        url = f"{self.base_url}/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        return self._make_request('GET', url)

    def get_sheet(self, spreadsheet_token: str, sheet_id: str):
        url = f"{self.base_url}/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}"
        return self._make_request('GET', url)

    def add_sheet(self, spreadsheet_token: str, title: str, index: int = None):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
        request_data = {
            "addSheet": {
                "properties": {"title": title}
            }
        }
        if index is not None:
            request_data["addSheet"]["properties"]["index"] = index

        payload = {"requests": [request_data]}
        return self._make_request('POST', url, json=payload)

    def delete_sheet(self, spreadsheet_token: str, sheet_id: str):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
        payload = {
            "requests": [{
                "deleteSheet": {"sheetId": sheet_id}
            }]
        }
        return self._make_request('POST', url, json=payload)

    def update_sheet_properties(self, spreadsheet_token: str, properties: dict):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
        payload = {
            "requests": [{
                "updateSheet": {"properties": properties}
            }]
        }
        return self._make_request('POST', url, json=payload)

    def obtain_spreadsheet_metainfo(self, spreadsheet_token: str, extFields: str = 'protectedRange', user_id_type: str = "open_id"):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/metainfo"
        params = {
            "extFields"   : extFields,
            "user_id_type": user_id_type
        }
        return self._make_request('GET', url, params=params)

    # ==================== 数据操作 ====================

    def read_sheet_data(self, spreadsheet_token: str, sheet_id: str, range_str: str = None,
            value_render_option: str = "ToString", date_time_render_option: str = "FormattedString"):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
        params = {
            "value_render_option"    : value_render_option,
            "date_time_render_option": date_time_render_option
        }
        if range_str:
            params["range"] = range_str
        return self._make_request('GET', url, params=params)

    def read_multiple_ranges(self, spreadsheet_token: str, sheet_id: str, ranges: list,
            user_id_type: str = "open_id", date_time_render_option: str = "FormattedString",
            value_render_option: str = "ToString"):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_get"
        full_ranges = [f"{sheet_id}!{r}" for r in ranges]
        params = {
            "ranges"                 : full_ranges,
            "user_id_type"           : user_id_type,
            "date_time_render_option": date_time_render_option,
            "value_render_option"    : value_render_option
        }
        return self._make_request('GET', url, params=params)

    def write_data_to_range(self, spreadsheet_token: str, sheet_id: str, range_str: str, values: list, insert_data_option: str = 'INSERT_ROWS'):
        """写入数据到指定范围"""
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
        payload = {
            "valueRange"      : {
                "range" : f"{sheet_id}!{range_str}",
                "values": values
            },
            "insertDataOption": insert_data_option
        }
        return self._make_request('POST', url, json=payload)

    def write_data_to_multiple_ranges(self, spreadsheet_token: str, sheet_id: str, value_ranges: list):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update"
        formatted_ranges = []
        for vr in value_ranges:
            formatted_range = vr.copy()
            if '!' not in formatted_range['range']:
                formatted_range['range'] = f"{sheet_id}!{formatted_range['range']}"
            formatted_ranges.append(formatted_range)

        payload = {"value_ranges": formatted_ranges}
        return self._make_request('POST', url, json=payload)

    def image_url_to_path(self, image_url: str):
        image_dir = r'C:\Users\Administrator\Desktop\auto\image\shein'
        file_name = os.path.basename(urlparse(image_url).path)  # 获取 URL 路径中的文件名
        file_path = os.path.join(image_dir, file_name)  # 拼接文件路径
        if not os.path.exists(file_path):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
        return file_path

    def write_image(self, spreadsheet_token: str, range_str: str, image_url: str):
        image_path = self.image_url_to_path(image_url)
        with open(image_path, "rb") as image_file:
            fb = image_file.read()
            misssing_padding = 4 - len(fb) % 4
            if misssing_padding:
                fb += b'=' * misssing_padding
            fb = base64.b64encode(fb).decode('utf-8')

            name = os.path.basename(image_path)

            url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values_image"
            payload = {
                "range": f"{range_str}",
                "image": fb,
                "name" : name,
            }
            return self._make_request('POST', url, json=payload)

    # ==================== 单元格样式操作 ====================

    def merge_cells(self, spreadsheet_token: str, sheet_id: str, merge_type: str, range_str: str):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/merge_cells"
        payload = {
            "range"    : f"{sheet_id}!{range_str}",
            "mergeType": merge_type
        }
        return self._make_request('POST', url, json=payload)

    def unmerge_cells(self, spreadsheet_token: str, sheet_id: str, range_str: str):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/unmerge_cells"
        payload = {"range": f"{sheet_id}!{range_str}"}
        return self._make_request('POST', url, json=payload)

    def batch_set_cell_style(self, spreadsheet_token: str, data_list: list):
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/styles_batch_update"
        payload = {"data": data_list}
        return self._make_request('PUT', url, json=payload)

    # ==================== 权限管理 ====================

    def batch_create_permission_members(self, token: str, type: str, members: list, need_notification: bool = True):
        url = f"{self.base_url}/drive/v1/permissions/{token}/members/batch_create"
        params = {
            "type"             : type,
            "need_notification": str(need_notification).lower()
        }
        payload = {"members": members}
        return self._make_request('POST', url, params=params, json=payload)

    def update_permission_member(self, token: str, type: str, member_type: str, member_id: str,
            perm: str, need_notification: bool = True):
        url = f"{self.base_url}/drive/v2/permissions/{token}/members/{member_id}"
        params = {
            "type"             : type,
            "member_type"      : member_type,
            "need_notification": str(need_notification).lower()
        }
        payload = {"perm": perm}
        return self._make_request('PUT', url, params=params, json=payload)

    def list_permission_members(self, token: str, type: str, page_size: int = 50, page_token: str = None):
        url = f"{self.base_url}/drive/v2/permissions/{token}/members"
        params = {
            "type"     : type,
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
        return self._make_request('GET', url, params=params)

    def transfer_permission_owner(self, token: str, type: str, member_type: str, member_id: str, need_notification: bool = True):
        url = f"{self.base_url}/drive/v2/permissions/{token}/members/transfer_owner"
        params = {
            "type"             : type,
            "need_notification": str(need_notification).lower()
        }
        payload = {
            "member_type": member_type,
            "member_id"  : member_id
        }
        return self._make_request('POST', url, params=params, json=payload)

    def check_permission_member_auth(self, token: str, type: str, action_type: str, member_type: str, member_id: str):
        url = f"{self.base_url}/drive/v2/permissions/{token}/members/auth"
        params = {
            "type"       : type,
            "action_type": action_type,
            "member_type": member_type,
            "member_id"  : member_id
        }
        return self._make_request('GET', url, params=params)

    # ==================== 表格保护范围 ====================

    def add_protected_dimension(self, spreadsheet_token: str, add_protected_dimension: list, user_id_type: str = "open_id"):
        """增加电子表格保护范围的维度信息"""
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/protected_dimension"
        params = {
            "user_id_type": user_id_type
        }
        payload = {
            "addProtectedDimension": add_protected_dimension
        }
        return self._make_request('POST', url, params=params, json=payload)

    def batch_delete_protected_range(self, spreadsheet_token: str, protect_ids: list):
        """批量删除电子表格保护范围"""
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/protected_range_batch_del"
        payload = {
            "protectIds": protect_ids
        }
        return self._make_request('DELETE', url, json=payload)
