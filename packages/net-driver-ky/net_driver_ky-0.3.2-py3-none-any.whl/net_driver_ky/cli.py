"""
命令行接口模块
"""

import argparse
import sys
import json
from typing import List, Optional

from .core import NetworkUtils, PortScanner
from .async_utils import AsyncNetworkUtils
from .exceptions import NetworkUtilsError


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="Net Utils KY - 网络工具包命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  net-utils check-connection                    # 检查网络连接
  net-utils get https://api.github.com         # 发送GET请求
  net-utils scan-ports example.com 80,443,8080 # 扫描端口
  net-utils latency 8.8.8.8                    # 测试延迟
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 检查连接命令
    check_parser = subparsers.add_parser("check-connection", help="检查网络连接")
    check_parser.add_argument("--url", default="https://www.google.com", help="测试URL")
    
    # GET请求命令
    get_parser = subparsers.add_parser("get", help="发送GET请求")
    get_parser.add_argument("url", help="请求URL")
    get_parser.add_argument("--headers", help="请求头 (JSON格式)")
    get_parser.add_argument("--timeout", type=int, default=30, help="超时时间(秒)")
    
    # POST请求命令
    post_parser = subparsers.add_parser("post", help="发送POST请求")
    post_parser.add_argument("url", help="请求URL")
    post_parser.add_argument("--data", help="POST数据 (JSON格式)")
    post_parser.add_argument("--headers", help="请求头 (JSON格式)")
    post_parser.add_argument("--timeout", type=int, default=30, help="超时时间(秒)")
    
    # 端口扫描命令
    scan_parser = subparsers.add_parser("scan-ports", help="扫描端口")
    scan_parser.add_argument("host", help="目标主机")
    scan_parser.add_argument("ports", help="端口列表 (逗号分隔)")
    scan_parser.add_argument("--timeout", type=float, default=1.0, help="连接超时时间(秒)")
    
    # 延迟测试命令
    latency_parser = subparsers.add_parser("latency", help="测试网络延迟")
    latency_parser.add_argument("host", help="目标主机")
    latency_parser.add_argument("--port", type=int, default=53, help="目标端口")
    
    # DNS检查命令
    dns_parser = subparsers.add_parser("dns", help="检查DNS解析")
    dns_parser.add_argument("domain", help="要检查的域名")
    
    # 常见端口扫描命令
    common_parser = subparsers.add_parser("common-ports", help="扫描常见端口")
    common_parser.add_argument("host", help="目标主机")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "check-connection":
            check_connection(args.url)
        elif args.command == "get":
            make_get_request(args.url, args.headers, args.timeout)
        elif args.command == "post":
            make_post_request(args.url, args.data, args.headers, args.timeout)
        elif args.command == "scan-ports":
            scan_ports(args.host, args.ports, args.timeout)
        elif args.command == "latency":
            test_latency(args.host, args.port)
        elif args.command == "dns":
            check_dns(args.domain)
        elif args.command == "common-ports":
            scan_common_ports(args.host)
    except NetworkUtilsError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n操作被用户中断", file=sys.stderr)
        sys.exit(1)


def check_connection(test_url: str):
    """检查网络连接"""
    print(f"正在检查网络连接 ({test_url})...")
    
    net_utils = NetworkUtils()
    if net_utils.is_connected(test_url):
        print("✅ 网络连接正常")
    else:
        print("❌ 网络连接失败")
        sys.exit(1)


def make_get_request(url: str, headers: Optional[str], timeout: int):
    """发送GET请求"""
    print(f"正在发送GET请求到 {url}...")
    
    # 解析请求头
    headers_dict = {}
    if headers:
        try:
            headers_dict = json.loads(headers)
        except json.JSONDecodeError:
            print("错误: 请求头格式无效 (应为JSON格式)", file=sys.stderr)
            sys.exit(1)
    
    net_utils = NetworkUtils(timeout=(5, timeout))
    try:
        response = net_utils.get(url, headers=headers_dict)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text[:500]}...")
    finally:
        net_utils.close()


def make_post_request(url: str, data: Optional[str], headers: Optional[str], timeout: int):
    """发送POST请求"""
    print(f"正在发送POST请求到 {url}...")
    
    # 解析数据
    data_dict = {}
    if data:
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError:
            print("错误: POST数据格式无效 (应为JSON格式)", file=sys.stderr)
            sys.exit(1)
    
    # 解析请求头
    headers_dict = {}
    if headers:
        try:
            headers_dict = json.loads(headers)
        except json.JSONDecodeError:
            print("错误: 请求头格式无效 (应为JSON格式)", file=sys.stderr)
            sys.exit(1)
    
    net_utils = NetworkUtils(timeout=(5, timeout))
    try:
        response = net_utils.post(url, json=data_dict, headers=headers_dict)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text[:500]}...")
    finally:
        net_utils.close()


def scan_ports(host: str, ports_str: str, timeout: float):
    """扫描端口"""
    # 解析端口列表
    try:
        ports = [int(p.strip()) for p in ports_str.split(",")]
    except ValueError:
        print("错误: 端口格式无效 (应为逗号分隔的数字)", file=sys.stderr)
        sys.exit(1)
    
    print(f"正在扫描 {host} 的端口: {ports}")
    
    scanner = PortScanner(timeout=timeout)
    open_ports = scanner.scan_ports(host, ports)
    
    if open_ports:
        print(f"✅ 开放的端口: {open_ports}")
    else:
        print("❌ 没有发现开放的端口")


def test_latency(host: str, port: int):
    """测试网络延迟"""
    print(f"正在测试到 {host}:{port} 的延迟...")
    
    net_utils = NetworkUtils()
    latency = net_utils.get_latency(host, port)
    
    if latency is not None:
        print(f"✅ 延迟: {latency:.2f}ms")
    else:
        print("❌ 无法测试延迟")
        sys.exit(1)


def check_dns(domain: str):
    """检查DNS解析"""
    print(f"正在检查 {domain} 的DNS解析...")
    
    net_utils = NetworkUtils()
    if net_utils.dns_works(domain):
        print(f"✅ DNS解析正常")
    else:
        print("❌ DNS解析失败")
        sys.exit(1)


def scan_common_ports(host: str):
    """扫描常见端口"""
    print(f"正在扫描 {host} 的常见端口...")
    
    scanner = PortScanner()
    results = scanner.scan_common_ports(host)
    
    print("端口扫描结果:")
    for port, is_open in results.items():
        status = "✅ 开放" if is_open else "❌ 关闭"
        print(f"  端口 {port}: {status}")


if __name__ == "__main__":
    main() 