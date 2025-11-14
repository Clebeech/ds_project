# 部署指南

将832工程数据库应用系统部署到互联网的完整指南。

## 推荐方案

### 方案1：Railway（推荐，最简单）

**优点：**
- 免费额度充足（每月$5免费额度）
- 支持MySQL数据库
- 自动部署，配置简单
- 提供HTTPS证书

**步骤：**

1. **注册Railway账号**
   - 访问 https://railway.app
   - 使用GitHub账号登录

2. **部署后端**
   - 在Railway创建新项目
   - 连接GitHub仓库
   - 选择"Deploy from GitHub repo"
   - Railway会自动检测Flask应用

3. **配置数据库**
   - 在Railway项目中添加MySQL服务
   - 获取数据库连接信息（会自动生成环境变量）

4. **设置环境变量**
   - 在Railway项目设置中添加：
     ```
     DB_HOST=你的数据库主机
     DB_USER=你的数据库用户
     DB_PASSWORD=你的数据库密码
     DB_NAME=poverty_alleviation_832
     ```

5. **部署前端**
   - 使用Vercel或Netlify部署前端
   - 连接GitHub仓库
   - 设置构建命令：无需（静态文件）
   - 设置输出目录：`frontend`

### 方案2：Render

**优点：**
- 免费套餐可用
- 支持MySQL
- 提供免费PostgreSQL（需要迁移）

**步骤：**

1. **注册Render账号**
   - 访问 https://render.com
   - 使用GitHub账号登录

2. **部署后端**
   - 创建新的Web Service
   - 连接GitHub仓库
   - 设置：
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn backend.app:application`
   - 添加环境变量（数据库配置）

3. **部署数据库**
   - 创建MySQL数据库服务
   - 获取连接信息

4. **部署前端**
   - 创建Static Site
   - 连接GitHub仓库
   - 设置根目录：`frontend`

### 方案3：Vercel + PlanetScale（推荐用于快速演示）

**优点：**
- Vercel部署前端非常快
- PlanetScale提供免费MySQL
- 两者配合很好

**步骤：**

1. **部署前端到Vercel**
   - 访问 https://vercel.com
   - 导入GitHub仓库
   - 设置根目录：`frontend`
   - 自动部署完成

2. **部署后端到Vercel（Serverless）**
   - Vercel支持Python Serverless Functions
   - 需要调整代码结构（可选）

3. **使用PlanetScale数据库**
   - 注册 https://planetscale.com
   - 创建免费数据库
   - 导入数据

## 部署前准备

### 1. 修改数据库配置支持环境变量

已创建 `backend/db.py` 支持环境变量，确保使用最新版本。

### 2. 更新前端API地址

部署后需要修改 `frontend/app.js` 中的 `API_BASE` 为实际的后端地址。

### 3. 创建部署配置文件

已创建以下文件：
- `Procfile` - Railway/Render部署配置
- `.env.example` - 环境变量示例
- `runtime.txt` - Python版本指定

## 快速部署步骤（Railway示例）

```bash
# 1. 确保代码已提交到GitHub
git add .
git commit -m "准备部署"
git push

# 2. 在Railway创建项目
# - 登录 railway.app
# - New Project -> Deploy from GitHub repo
# - 选择你的仓库

# 3. 添加MySQL数据库
# - 在项目中点击 "+ New" -> Database -> MySQL

# 4. 设置环境变量
# - Settings -> Variables
# - 添加数据库连接信息

# 5. 导入数据
# - 在本地运行: python backend/init_database.py
# - 或使用Railway的MySQL终端导入

# 6. 部署前端到Vercel
# - 登录 vercel.com
# - Import Project -> 选择仓库
# - Root Directory: frontend
# - 修改 frontend/app.js 中的 API_BASE 为Railway后端地址
```

## 注意事项

1. **数据库迁移**：需要将本地MySQL数据导出并导入到云数据库
2. **CORS设置**：确保后端允许前端域名访问
3. **环境变量**：不要将敏感信息提交到GitHub
4. **HTTPS**：Railway和Vercel都自动提供HTTPS
5. **免费额度**：注意各平台的免费额度限制

## 数据迁移

```bash
# 导出本地数据库
mysqldump -u root -p poverty_alleviation_832 > database_dump.sql

# 导入到云数据库（根据平台调整）
mysql -h 云数据库主机 -u 用户名 -p poverty_alleviation_832 < database_dump.sql
```

## 故障排查

1. **后端无法连接数据库**：检查环境变量是否正确设置
2. **前端无法访问API**：检查CORS设置和API地址
3. **静态资源404**：检查前端部署路径配置

## 推荐配置

- **后端**：Railway（简单易用）
- **前端**：Vercel（快速免费）
- **数据库**：Railway MySQL 或 PlanetScale

这样配置后，你的应用就可以通过链接分享给朋友了！

