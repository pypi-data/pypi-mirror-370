"""
自定义异常类
"""


class NetworkUtilsError(Exception):
    """网络工具包的基础异常类"""
    pass


class ConnectionError(NetworkUtilsError):
    """连接错误异常"""
    pass


class TimeoutError(NetworkUtilsError):
    """超时错误异常"""
    pass


class DNSResolutionError(NetworkUtilsError):
    """DNS解析错误异常"""
    pass


class PortScanError(NetworkUtilsError):
    """端口扫描错误异常"""
    pass


class HTTPRequestError(NetworkUtilsError):
    """HTTP请求错误异常"""
    pass 