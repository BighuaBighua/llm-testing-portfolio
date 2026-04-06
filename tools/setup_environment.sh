#!/bin/bash
#
# 开发环境自动配置脚本
# 功能：自动检测并配置开发环境
#

set -e

echo "🔧 开发环境配置脚本"
echo "================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测函数
check_python() {
    echo "📝 检测 Python 环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✅ Python 已安装: $PYTHON_VERSION${NC}"
        return 0
    else
        echo -e "${RED}❌ Python 未安装${NC}"
        echo "请安装 Python 3.8+"
        return 1
    fi
}

check_pip() {
    echo "📝 检测 pip..."
    
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        echo -e "${GREEN}✅ pip 已安装: $PIP_VERSION${NC}"
        return 0
    else
        echo -e "${RED}❌ pip 未安装${NC}"
        return 1
    fi
}

install_dependencies() {
    echo
    echo "📦 安装 Python 依赖..."
    
    # 使用国内镜像
    MIRRORS=(
        "https://pypi.tuna.tsinghua.edu.cn/simple"
        "https://mirrors.aliyun.com/pypi/simple/"
        "https://pypi.douban.com/simple/"
    )
    
    for mirror in "${MIRRORS[@]}"; do
        echo "尝试使用镜像: $mirror"
        if pip3 install -r requirements.txt -i "$mirror"; then
            echo -e "${GREEN}✅ 依赖安装成功${NC}"
            return 0
        fi
    done
    
    echo -e "${RED}❌ 依赖安装失败，请手动安装${NC}"
    return 1
}

check_env_file() {
    echo
    echo "📝 检查环境变量配置..."
    
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env 文件已存在${NC}"
    else
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}⚠️  .env 文件不存在，正在创建...${NC}"
            cp .env.example .env
            echo -e "${GREEN}✅ 已创建 .env 文件${NC}"
            echo -e "${YELLOW}⚠️  请编辑 .env 文件，填入你的 API Key${NC}"
        else
            echo -e "${RED}❌ .env.example 文件不存在${NC}"
        fi
    fi
}

verify_installation() {
    echo
    echo "🔍 验证安装..."
    
    # 检查关键依赖
    if python3 -c "import requests" 2>/dev/null; then
        echo -e "${GREEN}✅ requests 已安装${NC}"
    else
        echo -e "${RED}❌ requests 未安装${NC}"
    fi
    
    if python3 -c "import dotenv" 2>/dev/null; then
        echo -e "${GREEN}✅ python-dotenv 已安装${NC}"
    else
        echo -e "${RED}❌ python-dotenv 未安装${NC}"
    fi
    
    # 检查测试脚本
    if [ -f "scripts/run_tests.py" ]; then
        echo -e "${GREEN}✅ 测试脚本存在${NC}"
    else
        echo -e "${RED}❌ 测试脚本不存在${NC}"
    fi
}

# 主流程
main() {
    echo "开始配置开发环境..."
    echo
    
    # 1. 检测 Python
    check_python || exit 1
    
    # 2. 检测 pip
    check_pip || exit 1
    
    # 3. 安装依赖
    install_dependencies
    
    # 4. 检查环境变量
    check_env_file
    
    # 5. 验证安装
    verify_installation
    
    echo
    echo "================================"
    echo -e "${GREEN}✅ 环境配置完成！${NC}"
    echo
    echo "下一步："
    echo "1. 编辑 .env 文件，填入你的 API Key"
    echo "2. 阅读 AI_CODING_RULES.md 了解编码规范"
    echo "3. 运行 python scripts/run_tests.py 开始测试"
    echo
}

# 执行主流程
main
