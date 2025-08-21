#!/bin/bash

# Excel to Markdown MCP - PyPI发布脚本
# 使用方法: ./upload_to_pypi.sh [test|prod]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
ENVIRONMENT=${1:-test}  # 默认为测试环境

if [[ "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "参数错误! 使用: $0 [test|prod]"
    print_info "  test - 上传到 TestPyPI (推荐先测试)"
    print_info "  prod - 上传到正式 PyPI"
    exit 1
fi

print_info "准备发布到 $ENVIRONMENT 环境..."

# 1. 检查必要工具
print_info "检查必要工具..."

if ! command -v uv &> /dev/null; then
    print_error "uv 未安装! 请先安装 uv"
    exit 1
fi

if ! command -v twine &> /dev/null; then
    print_warning "twine 未安装，正在安装..."
    pip install twine
fi

# 2. 清理旧的构建文件
print_info "清理旧的构建文件..."
if [ -d "dist" ]; then
    rm -rf dist/
    print_success "已清理 dist/ 目录"
fi

# 3. 构建包
print_info "构建Python包..."
uv build

if [ $? -eq 0 ]; then
    print_success "包构建成功!"
    ls -la dist/
else
    print_error "包构建失败!"
    exit 1
fi

# 4. 检查包
print_info "检查包完整性..."
twine check dist/*

if [ $? -ne 0 ]; then
    print_error "包检查失败!"
    exit 1
fi

print_success "包检查通过!"

# 5. 上传包
if [ "$ENVIRONMENT" = "test" ]; then
    print_info "上传到 TestPyPI..."
    print_warning "请输入 TestPyPI 的用户名和密码/Token"
    print_info "TestPyPI 注册地址: https://test.pypi.org/account/register/"
    twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_success "成功上传到 TestPyPI!"
        print_info "测试安装命令:"
        echo "pip install --index-url https://test.pypi.org/simple/ excel-to-markdown-mcp"
        print_info "TestPyPI 页面: https://test.pypi.org/project/excel-to-markdown-mcp/"
    fi
else
    print_warning "即将上传到正式 PyPI！"
    read -p "确认上传到正式 PyPI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "上传到正式 PyPI..."
        print_warning "请输入 PyPI 的用户名和密码/Token"
        twine upload dist/*
        
        if [ $? -eq 0 ]; then
            print_success "成功上传到 PyPI!"
            print_info "安装命令: pip install excel-to-markdown-mcp"
            print_info "PyPI 页面: https://pypi.org/project/excel-to-markdown-mcp/"
        fi
    else
        print_info "取消上传到正式 PyPI"
    fi
fi

print_success "脚本执行完成!"