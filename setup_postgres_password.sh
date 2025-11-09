#!/bin/bash

echo "PostgreSQL 密码设置工具"
echo "===================="

# 设置 PATH
export PATH="/usr/local/opt/postgresql@15/bin:$PATH"

echo "请输入新的 PostgreSQL 密码："
read -s new_password

if [ -z "$new_password" ]; then
    echo "密码不能为空！"
    exit 1
fi

echo ""
echo "正在设置密码..."

# 执行密码修改
psql -d postgres -c "ALTER USER huihui PASSWORD '$new_password';" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 密码设置成功！"
    echo ""
    echo "新的连接信息："
    echo "Host: localhost"
    echo "Port: 5432"
    echo "Database: postgres"
    echo "Username: huihui"
    echo "Password: $new_password"
else
    echo "❌ 密码设置失败，请检查 PostgreSQL 服务是否正常运行"
fi