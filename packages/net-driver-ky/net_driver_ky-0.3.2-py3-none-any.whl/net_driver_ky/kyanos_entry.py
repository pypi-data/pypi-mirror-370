import sys
import os
import subprocess
import platform
import pkg_resources

def main():
    # 自动选择二进制
    arch = platform.machine().lower()
    if arch in ('x86_64', 'amd64'):
        bin_name = 'kyanos-x86_64'
    elif arch in ('aarch64', 'arm64'):
        bin_name = 'kyanos-arm64'
    else:
        sys.stderr.write(f'Unsupported arch: {arch}\n')
        sys.exit(1)
    bin_path = pkg_resources.resource_filename('net_utils_ky', f'libs/kyanos/{bin_name}')
    if not os.path.isfile(bin_path):
        sys.stderr.write(f'kyanos binary not found: {bin_path}\n')
        sys.exit(1)
    # 传递所有参数
    args = [bin_path] + sys.argv[1:]
    # 运行二进制
    os.execv(bin_path, args)