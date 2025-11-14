# 快速部署指南

## 第一步：准备代码

```bash
# 1. 检查部署准备
./deploy_helper.sh

# 2. 提交所有更改到Git
git add .
git commit -m "准备部署到生产环境"

# 3. 推送到GitHub（如果还没有远程仓库）
# 在GitHub创建新仓库，然后：
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

## 第二步：部署后端到Railway

### 1. 注册Railway
- 访问 https://railway.app
- 点击 "Login" → 选择 "Login with GitHub"
- 授权Railway访问你的GitHub账号

### 2. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的仓库
- Railway会自动检测Flask应用

### 3. 添加MySQL数据库
- 在项目页面点击 "+ New"
- 选择 "Database" → "Add MySQL"
- 等待数据库创建完成（约1-2分钟）

### 4. 配置环境变量
- 点击数据库服务，进入 "Variables" 标签
- 复制以下环境变量（Railway会自动生成）：
  - `MYSQLHOST` → 作为 `DB_HOST`
  - `MYSQLUSER` → 作为 `DB_USER`
  - `MYSQLPASSWORD` → 作为 `DB_PASSWORD`
  - `MYSQLDATABASE` → 作为 `DB_NAME`
  - `MYSQLPORT` → 作为 `DB_PORT`（如果需要）

- 在Web服务中，进入 "Variables" 标签，添加：
  ```
  DB_HOST=${{MySQL.MYSQLHOST}}
  DB_USER=${{MySQL.MYSQLUSER}}
  DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
  DB_NAME=${{MySQL.MYSQLDATABASE}}
  ```

### 5. 导入数据
有两种方式：

**方式1：使用Railway的MySQL终端**
- 点击数据库服务 → "Connect" → "MySQL"
- 在终端中运行：
```sql
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS poverty_alleviation_832;
USE poverty_alleviation_832;

-- 然后导入表结构（从plan/05_create_tables.sql）
-- 和运行数据导入脚本
```

**方式2：从本地导入**
```bash
# 在本地导出数据库
mysqldump -u root -p poverty_alleviation_832 > database_dump.sql

# 在Railway MySQL终端中导入
# 或者使用Railway的数据库连接信息，在本地运行：
mysql -h [Railway数据库主机] -u [用户名] -p poverty_alleviation_832 < database_dump.sql
```

### 6. 获取后端地址
- 部署完成后，Railway会提供一个URL，例如：`https://your-app.railway.app`
- 复制这个地址，稍后用于前端配置

## 第三步：部署前端到Vercel

### 1. 注册Vercel
- 访问 https://vercel.com
- 点击 "Sign Up" → 选择 "Continue with GitHub"
- 授权Vercel访问你的GitHub账号

### 2. 导入项目
- 点击 "Add New..." → "Project"
- 选择你的GitHub仓库
- 配置项目：
  - **Framework Preset**: Other
  - **Root Directory**: `frontend`
  - **Build Command**: 留空（静态文件，无需构建）
  - **Output Directory**: `.`（当前目录）

### 3. 修改API地址
- 部署前，需要修改 `frontend/index.html` 中的API地址
- 找到这一行：
```javascript
window.API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5001/api'
    : 'https://your-backend-url.railway.app/api';  // 部署后修改这里
```
- 将 `your-backend-url.railway.app` 替换为你的Railway后端地址

### 4. 重新提交并部署
```bash
git add frontend/index.html
git commit -m "更新前端API地址"
git push
```
- Vercel会自动检测到更改并重新部署

## 第四步：测试部署

1. **测试后端API**
   - 访问：`https://your-backend.railway.app/api/stats/overview`
   - 应该返回JSON数据

2. **测试前端**
   - 访问：`https://your-project.vercel.app`
   - 检查是否能正常加载数据

## 常见问题

### 后端无法连接数据库
- 检查环境变量是否正确设置
- 确保数据库服务已启动
- 检查数据库连接信息

### 前端无法访问API
- 检查CORS设置（已在backend/app.py中配置）
- 确认API地址正确
- 检查浏览器控制台的错误信息

### 数据未显示
- 确认数据已成功导入到云数据库
- 检查数据库连接是否正常
- 查看Railway的日志输出

## 费用说明

- **Railway**: 每月$5免费额度，通常足够使用
- **Vercel**: 免费套餐对个人项目完全够用
- **总计**: 完全免费（在免费额度内）

## 完成！

部署完成后，你就可以通过链接分享给朋友了：
- 前端地址：`https://your-project.vercel.app`
- 后端API：`https://your-backend.railway.app/api`

