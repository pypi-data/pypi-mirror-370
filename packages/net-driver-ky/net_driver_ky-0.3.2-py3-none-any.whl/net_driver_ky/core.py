"""
核心功能模块
"""

import socket
import time
import threading
from typing import Optional, Tuple, List, Union, Dict, Any
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    NetworkUtilsError,
    ConnectionError,
    TimeoutError,
    DNSResolutionError,
    PortScanError,
    HTTPRequestError,
)


class HTTPClient:
    """HTTP客户端类"""
    
    def __init__(
        self,
        timeout: Tuple[int, int] = (5, 30),
        proxy: Optional[str] = None,
        retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        初始化HTTP客户端
        
        Args:
            timeout: (连接超时, 读取超时)
            proxy: 代理地址
            retries: 重试次数
            headers: 默认请求头
        """
        self.timeout = timeout
        self.proxy = proxy
        self.retries = retries
        self.headers = headers or {}
        
        # 创建session
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置代理
        if proxy:
            self.session.proxies = {
                "http": proxy,
                "https": proxy,
            }
        
        # 设置默认请求头
        if headers:
            self.session.headers.update(headers)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPRequestError(f"GET请求失败: {e}")
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        try:
            response = self.session.post(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPRequestError(f"POST请求失败: {e}")
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        try:
            response = self.session.put(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPRequestError(f"PUT请求失败: {e}")
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        try:
            response = self.session.delete(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise HTTPRequestError(f"DELETE请求失败: {e}")
    
    def close(self):
        """关闭session"""
        self.session.close()


class NetworkChecker:
    """网络连接检测类"""
    
    def __init__(self, timeout: int = 5):
        """
        初始化网络检测器
        
        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout
    
    def is_connected(self, test_url: str = "https://www.google.com") -> bool:
        """
        检查网络连接
        
        Args:
            test_url: 测试URL
            
        Returns:
            bool: 是否连接正常
        """
        try:
            response = requests.get(test_url, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
    
    def can_reach(self, url: str) -> bool:
        """
        检查是否可以访问指定URL
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 是否可以访问
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            return response.status_code < 400
        except:
            return False
    
    def dns_works(self, domain: str = "google.com") -> bool:
        """
        检查DNS解析是否正常
        
        Args:
            domain: 要检查的域名
            
        Returns:
            bool: DNS解析是否正常
        """
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
    
    def get_latency(self, host: str = "8.8.8.8", port: int = 53) -> Optional[float]:
        """
        获取网络延迟
        
        Args:
            host: 目标主机
            port: 目标端口
            
        Returns:
            float: 延迟时间（毫秒），失败返回None
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))
            sock.close()
            return (time.time() - start_time) * 1000
        except:
            return None


class PortScanner:
    """端口扫描类"""
    
    def __init__(self, timeout: float = 1.0):
        """
        初始化端口扫描器
        
        Args:
            timeout: 连接超时时间
        """
        self.timeout = timeout
    
    def is_port_open(self, host: str, port: int) -> bool:
        """
        检查单个端口是否开放
        
        Args:
            host: 目标主机
            port: 目标端口
            
        Returns:
            bool: 端口是否开放
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def scan_ports(self, host: str, ports: Union[List[int], range]) -> List[int]:
        """
        扫描多个端口
        
        Args:
            host: 目标主机
            ports: 端口列表或范围
            
        Returns:
            List[int]: 开放的端口列表
        """
        open_ports = []
        
        for port in ports:
            if self.is_port_open(host, port):
                open_ports.append(port)
        
        return open_ports
    
    def scan_common_ports(self, host: str) -> Dict[int, bool]:
        """
        扫描常见端口
        
        Args:
            host: 目标主机
            
        Returns:
            Dict[int, bool]: 端口状态字典
        """
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 8080]
        results = {}
        
        for port in common_ports:
            results[port] = self.is_port_open(host, port)
        
        return results


class NetworkUtils:
    """网络工具主类"""
    
    def __init__(
        self,
        timeout: Tuple[int, int] = (5, 30),
        proxy: Optional[str] = None,
        retries: int = 3,
    ):
        """
        初始化网络工具
        
        Args:
            timeout: (连接超时, 读取超时)
            proxy: 代理地址
            retries: 重试次数
        """
        self.http_client = HTTPClient(timeout, proxy, retries)
        self.network_checker = NetworkChecker(timeout[0])
        self.port_scanner = PortScanner()
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self.http_client.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self.http_client.post(url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self.http_client.put(url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self.http_client.delete(url, **kwargs)
    
    def is_connected(self, test_url: str = "https://www.google.com") -> bool:
        """检查网络连接"""
        return self.network_checker.is_connected(test_url)
    
    def can_reach(self, url: str) -> bool:
        """检查是否可以访问指定URL"""
        return self.network_checker.can_reach(url)
    
    def dns_works(self, domain: str = "google.com") -> bool:
        """检查DNS解析是否正常"""
        return self.network_checker.dns_works(domain)
    
    def get_latency(self, host: str = "8.8.8.8", port: int = 53) -> Optional[float]:
        """获取网络延迟"""
        return self.network_checker.get_latency(host, port)
    
    def is_port_open(self, host: str, port: int) -> bool:
        """检查端口是否开放"""
        return self.port_scanner.is_port_open(host, port)
    
    def scan_ports(self, host: str, ports: Union[List[int], range]) -> List[int]:
        """扫描端口"""
        return self.port_scanner.scan_ports(host, ports)
    
    def scan_common_ports(self, host: str) -> Dict[int, bool]:
        """扫描常见端口"""
        return self.port_scanner.scan_common_ports(host)
    
    def close(self):
        """关闭连接"""
        self.http_client.close() 