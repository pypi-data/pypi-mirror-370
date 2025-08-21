import os
import time
from typing import TypeVar, Type, Dict, Any, Optional, Union, List
from urllib.parse import unquote

import requests
from requests.exceptions import RequestException

T = TypeVar('T')


class TaientClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 配置初始化
        self.HRP_SERVER = os.getenv("TAIENT_HRP_SERVER", config.get("TAIENT_HRP_SERVER"))
        self.HRP_USERNAME = config.get('TAIENT_HRP_USERNAME')
        self.HRP_PASSWORD = config.get('TAIENT_HRP_PASSWORD')

        # 检查 TAIENT_HRP_SERVER 必须存在
        if not self.HRP_SERVER:
            raise ValueError("环境变量 'TAIENT_HRP_SERVER' 必须设置")

        # 检查 TAIENT_HRP_USERNAME 和 TAIENT_HRP_PASSWORD 必须存在
        if not self.HRP_USERNAME or not self.HRP_PASSWORD:
            raise ValueError("配置必须包含 'TAIENT_HRP_USERNAME' 和 'TAIENT_HRP_PASSWORD'")

        # 凭证缓存
        self._cached_cookie = None
        self._cookie_timestamp = 0
        self._cached_token = None
        self._token_timestamp = 0

        # 超时时间设置（7天）
        self.EXPIRATION_TIME = 7 * 24 * 60 * 60
        self.session = requests.Session()  # 复用HTTP连接

    # URL构建器 =================================================================
    def hrp_url(self, api: str) -> str:
        return f"https://{self.HRP_SERVER}/guofu/api/v1{api}"

    # 认证管理 =================================================================
    def get_cookie(self) -> str:
        """获取HRP系统的Cookie（带缓存和自动刷新）"""
        if not self._cached_cookie or time.time() - self._cookie_timestamp > self.EXPIRATION_TIME:
            self._cached_cookie = self._login_and_get_cookie()
            self._cookie_timestamp = time.time()
        return self._cached_cookie

    def _login_and_get_cookie(self) -> str:
        """登录HRP系统并获取Cookie"""
        url = self.hrp_url("/pass/login")
        payload = {"username": self.HRP_USERNAME, "password": self.HRP_PASSWORD}

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return '; '.join([f"{name}={value}" for name, value in response.cookies.items()])
        except RequestException as e:
            raise Exception(f"HRP登录失败: {str(e)}")

    # HTTP请求封装 =============================================================
    def hrp_get(self, api: str) -> Optional[Dict[str, Any]]:
        """HRP系统GET请求"""
        return self._request_with_cookie("GET", self.hrp_url(api))

    def hrp_post(self, api: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """HRP系统POST请求"""
        return self._request_with_cookie("POST", self.hrp_url(api), payload)

    def _request_with_cookie(self, method: str, url: str, payload: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """携带Cookie的请求"""
        headers = {"Cookie": self.get_cookie()}
        return self._make_request(method, url, headers, payload)

    def _make_request(self, method: str, url: str, headers: Dict[str, str], payload: Optional[Dict]) -> Optional[
        Dict[str, Any]]:
        """统一的请求处理"""
        headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            else:
                response = self.session.post(url, json=payload, headers=headers, timeout=10)

            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"请求失败: {method} {url} - {str(e)}")
            return None

    # 响应数据处理 =============================================================
    def get_code(self, response: Dict[str, Any]) -> int:
        """提取响应状态码"""
        return response.get('result', {}).get('code', -1)

    def get_message(self, response: Dict[str, Any]) -> str:
        """提取响应消息"""
        return response.get('result', {}).get('message', '')

    def get_data(self, response: Dict[str, Any], data_type: Type[T]) -> Optional[Union[T, List[T]]]:
        """提取data对象，支持返回单个对象或列表"""
        data = response.get('data')
        if not data:
            return None

        if isinstance(data, list):
            return [data_type(**item) for item in data]  # 处理列表
        return data_type(**data)

    def download_file(self, file_id: str, internal_id: str, save_dir: str) -> Optional[str]:
        """
        下载文件并保存到本地（复用客户端会话和认证）

        :param file_id: 文件ID（如 "492276"）
        :param internal_id: 人才ID（如 "2514f893-e4e2-40a2-a7fe-db3e4d066fc4"）
        :param save_dir: 附件保存目录（自动从响应头提取文件名）
        :return: 下载文件的完整路径（失败返回None）
        """
        api_path = f"/resume/attach/{file_id}/{internal_id}/download"
        url = self.hrp_url(api_path)

        try:
            # 复用Session和Cookie
            headers = {"Cookie": self.get_cookie()}
            response = self.session.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            # 从响应头提取文件名（兼容不同浏览器格式）
            content_disposition = response.headers.get("Content-Disposition", "")
            filename = (
                content_disposition.split("filename=")[-1].strip('"\'')
                if "filename=" in content_disposition
                else f"file_{file_id}_{internal_id[:8]}.bin"  # 默认文件名
            )
            try:
                filename = unquote(filename)
            except Exception:
                pass  # 保持原文件名

            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)

            # 流式下载大文件
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤keep-alive空块
                        f.write(chunk)

            # print(f"[SUCCESS] 文件保存至: {save_path}")
            return save_path

        except RequestException as e:
            print(f"[ERROR] 文件下载失败: {url} - {str(e)}")
            return None
