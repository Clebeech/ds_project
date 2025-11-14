#!/bin/bash

# 数据库导出脚本
# 用于将本地数据库导出，方便迁移到云数据库

echo "=========================================="
echo "导出数据库..."
echo "=========================================="

DB_NAME="poverty_alleviation_832"
OUTPUT_FILE="database_dump.sql"

# 检查MySQL是否可用
if ! command -v mysql &> /dev/null; then
    echo "错误: MySQL客户端未安装"
    exit 1
fi

# 导出数据库
echo "正在导出数据库: $DB_NAME"
mysqldump -u root -p $DB_NAME > $OUTPUT_FILE

if [ $? -eq 0 ]; then
    echo "✓ 数据库导出成功: $OUTPUT_FILE"
    echo ""
    echo "文件大小: $(du -h $OUTPUT_FILE | cut -f1)"
    echo ""
    echo "下一步："
    echo "1. 在Railway创建MySQL数据库"
    echo "2. 使用以下命令导入数据："
    echo "   mysql -h [Railway主机] -u [用户名] -p $DB_NAME < $OUTPUT_FILE"
    echo "   或者使用Railway的MySQL终端导入"
else
    echo "✗ 数据库导出失败"
    exit 1
fi

