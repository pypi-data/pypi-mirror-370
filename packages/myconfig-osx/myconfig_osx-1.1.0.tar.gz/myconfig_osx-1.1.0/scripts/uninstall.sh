#!/bin/bash
#########################################################################
# @File Name:    uninstall.sh
# @Author:       MyConfig Team
# @Created Time: 2024
# @Copyright:    GPL 2.0
# @Description:  MyConfig 卸载脚本
#########################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}▸${NC} $1"
}

print_success() {
    echo -e "${GREEN}✔${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✖${NC} $1"
}

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  MyConfig 卸载工具${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
}

# 检查是否已安装
check_installation() {
    print_info "检查 MyConfig 安装状态..."
    
    if command -v myconfig >/dev/null 2>&1; then
        print_info "找到 myconfig 命令: $(which myconfig)"
        return 0
    else
        print_warning "未找到 myconfig 命令"
        return 1
    fi
}

# 卸载用户安装
uninstall_user() {
    print_info "卸载用户安装..."
    
    if pip3 uninstall myconfig -y 2>/dev/null; then
        print_success "用户安装卸载成功"
    else
        print_warning "用户安装卸载失败或未安装"
    fi
}

# 卸载系统安装
uninstall_system() {
    print_info "卸载系统安装 (需要管理员权限)..."
    
    if sudo pip3 uninstall myconfig -y 2>/dev/null; then
        print_success "系统安装卸载成功"
    else
        print_warning "系统安装卸载失败或未安装"
    fi
}

# 清理残留文件
cleanup_files() {
    print_info "清理可能的残留文件..."
    
    # 清理用户目录
    USER_BIN="$HOME/.local/bin/myconfig"
    if [[ -f "$USER_BIN" ]]; then
        rm -f "$USER_BIN"
        print_info "已删除: $USER_BIN"
    fi
    
    # 清理系统目录
    SYSTEM_BINS=("/usr/local/bin/myconfig" "/usr/bin/myconfig")
    for bin in "${SYSTEM_BINS[@]}"; do
        if [[ -f "$bin" ]]; then
            if sudo rm -f "$bin" 2>/dev/null; then
                print_info "已删除: $bin"
            fi
        fi
    done
    
    # 清理 Python 包缓存
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import site
import os
for path in site.getsitepackages() + [site.getusersitepackages()]:
    myconfig_path = os.path.join(path, 'myconfig')
    if os.path.exists(myconfig_path):
        print(f'Found package at: {myconfig_path}')
" 2>/dev/null || true
    fi
}

# 验证卸载
verify_uninstall() {
    print_info "验证卸载结果..."
    
    if command -v myconfig >/dev/null 2>&1; then
        print_error "myconfig 命令仍然存在: $(which myconfig)"
        print_warning "可能需要:"
        echo "  1. 重新加载 shell 配置"
        echo "  2. 手动删除残留文件"
        echo "  3. 检查 PATH 设置"
        return 1
    else
        print_success "myconfig 命令已成功卸载"
        return 0
    fi
}

# 显示手动清理说明
show_manual_cleanup() {
    echo
    print_info "如果自动卸载不完整，请手动检查以下位置:"
    echo "  用户安装:"
    echo "    ~/.local/bin/myconfig"
    echo "    ~/.local/lib/python*/site-packages/myconfig*"
    echo
    echo "  系统安装:"
    echo "    /usr/local/bin/myconfig"
    echo "    /usr/bin/myconfig"
    echo "    /usr/local/lib/python*/site-packages/myconfig*"
    echo
    echo "  配置文件 (如果需要的话):"
    echo "    ~/.myconfig/"
    echo "    ~/.config/myconfig/"
    echo
}

# 主函数
main() {
    print_header
    
    case "${1:-}" in
        --force)
            print_warning "强制卸载模式"
            uninstall_user
            uninstall_system
            cleanup_files
            verify_uninstall
            ;;
        --user)
            uninstall_user
            verify_uninstall
            ;;
        --system)
            uninstall_system
            verify_uninstall
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo
            echo "选项:"
            echo "  --user    仅卸载用户安装"
            echo "  --system  仅卸载系统安装"
            echo "  --force   强制卸载所有安装"
            echo "  --help    显示此帮助"
            echo
            echo "不带参数运行将尝试智能卸载"
            ;;
        "")
            if check_installation; then
                echo
                print_info "将尝试卸载 MyConfig..."
                echo "这将尝试用户安装和系统安装的卸载"
                echo
                read -p "继续? [y/N]: " confirm
                
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    uninstall_user
                    uninstall_system
                    cleanup_files
                    
                    if verify_uninstall; then
                        print_success "卸载完成！"
                    else
                        show_manual_cleanup
                    fi
                else
                    print_info "卸载已取消"
                fi
            else
                print_info "MyConfig 似乎未安装或已卸载"
            fi
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用 $0 --help 查看帮助"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
