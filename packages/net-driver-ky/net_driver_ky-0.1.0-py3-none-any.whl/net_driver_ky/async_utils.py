"""
异步工具模块
"""

import asyncio
import aiohttp
import socket
import time
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse

from .exceptions import NetworkUtilsError, HTTPRequestError


class AsyncNetworkUtils:
    """异步网络工具类"""
    
    def __init__(
        self,
        timeout: int = 30,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        初始化异步网络工具
        
        Args:
            timeout: 超时时间（秒）
            proxy: 代理地址
            headers: 默认请求头
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.proxy = proxy
        self.headers = headers or {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def _ensure_session(self):
        """确保session已创建"""
        if self._session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=connector,
                headers=self.headers,
            )
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """发送异步GET请求"""
        await self._ensure_session()
        try:
            async with self._session.get(url, proxy=self.proxy, **kwargs) as response:
                response.raise_for_status()
                return response
        except aiohttp.ClientError as e:
            raise HTTPRequestError(f"异步GET请求失败: {e}")
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """发送异步POST请求"""
        await self._ensure_session()
        try:
            async with self._session.post(url, proxy=self.proxy, **kwargs) as response:
                response.raise_for_status()
                return response
        except aiohttp.ClientError as e:
            raise HTTPRequestError(f"异步POST请求失败: {e}")
    
    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """发送异步PUT请求"""
        await self._ensure_session()
        try:
            async with self._session.put(url, proxy=self.proxy, **kwargs) as response:
                response.raise_for_status()
                return response
        except aiohttp.ClientError as e:
            raise HTTPRequestError(f"异步PUT请求失败: {e}")
    
    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """发送异步DELETE请求"""
        await self._ensure_session()
        try:
            async with self._session.delete(url, proxy=self.proxy, **kwargs) as response:
                response.raise_for_status()
                return response
        except aiohttp.ClientError as e:
            raise HTTPRequestError(f"异步DELETE请求失败: {e}")
    
    async def get_all(self, urls: List[str], **kwargs) -> List[aiohttp.ClientResponse]:
        """
        并发发送多个GET请求
        
        Args:
            urls: URL列表
            **kwargs: 其他请求参数
            
        Returns:
            List[aiohttp.ClientResponse]: 响应列表
        """
        await self._ensure_session()
        
        async def fetch_url(url: str) -> aiohttp.ClientResponse:
            try:
                async with self._session.get(url, proxy=self.proxy, **kwargs) as response:
                    response.raise_for_status()
                    return response
            except aiohttp.ClientError as e:
                raise HTTPRequestError(f"请求 {url} 失败: {e}")
        
        tasks = [fetch_url(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def post_all(self, urls: List[str], data_list: List[Dict], **kwargs) -> List[aiohttp.ClientResponse]:
        """
        并发发送多个POST请求
        
        Args:
            urls: URL列表
            data_list: 数据列表
            **kwargs: 其他请求参数
            
        Returns:
            List[aiohttp.ClientResponse]: 响应列表
        """
        await self._ensure_session()
        
        async def fetch_url(url: str, data: Dict) -> aiohttp.ClientResponse:
            try:
                async with self._session.post(url, json=data, proxy=self.proxy, **kwargs) as response:
                    response.raise_for_status()
                    return response
            except aiohttp.ClientError as e:
                raise HTTPRequestError(f"请求 {url} 失败: {e}")
        
        tasks = [fetch_url(url, data) for url, data in zip(urls, data_list)]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def is_connected(self, test_url: str = "https://www.google.com") -> bool:
        """
        异步检查网络连接
        
        Args:
            test_url: 测试URL
            
        Returns:
            bool: 是否连接正常
        """
        try:
            await self.get(test_url)
            return True
        except:
            return False
    
    async def can_reach(self, url: str) -> bool:
        """
        异步检查是否可以访问指定URL
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 是否可以访问
        """
        try:
            response = await self.get(url)
            return response.status < 400
        except:
            return False
    
    async def get_latency(self, host: str = "8.8.8.8", port: int = 53) -> Optional[float]:
        """
        异步获取网络延迟
        
        Args:
            host: 目标主机
            port: 目标端口
            
        Returns:
            float: 延迟时间（毫秒），失败返回None
        """
        try:
            start_time = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            return (time.time() - start_time) * 1000
        except:
            return None
    
    async def close(self):
        """关闭异步session"""
        if self._session:
            await self._session.close()
            self._session = None 