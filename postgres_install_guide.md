# PostgreSQL 安装指南

## 推荐方案：Postgres.app（最简单）

对于 macOS 10.15，推荐使用 Postgres.app，它是最稳定的解决方案。

### 安装步骤：

1. **下载 Postgres.app**
   - 访问：https://postgresapp.com/
   - 下载 "Postgres.app with PostgreSQL 16"

2. **安装**
   - 双击下载的 .zip 文件
   - 将 Postgres.app 拖到 Applications 文件夹

3. **启动**
   - 打开 Postgres.app
   - 点击 "Initialize" 创建数据库
   - 选择 "Start" 启动服务器

4. **命令行工具配置**
   - 打开 Postgres.app
   - 点击 "Postgres.app" → "Preferences"
   - 选择 "CLI Tools" 标签
   - 点击 "Install Command Line Tools"

5. **连接信息**
   - Host: localhost
   - Port: 5432
   - User: 你的 macOS 用户名 (huihui)
   - Database: postgres

### 使用 TablePlus 连接

1. 打开 TablePlus
2. 创建新连接：
   - Type: PostgreSQL
   - Name: InvestWin DB
   - Host: localhost
   - Port: 5432
   - User: huihui
   - Database: postgres
   - Password: (留空)

### 备选方案：使用 Docker

如果 Postgres.app 也有问题，可以使用 Docker：

```bash
docker run --name postgres-investwin \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_USER=investwin \
  -e POSTGRES_DB=investwin \
  -p 5432:5432 \
  -d postgres:15
```

连接信息：
- Host: localhost
- Port: 5432
- User: investwin
- Database: investwin
- Password: your_password