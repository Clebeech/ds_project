# 前端使用说明

## 功能特性

- **Aurora Gradient Hero风格**：科技感渐变背景
- **全屏分页滚动**：使用fullpage.js实现平滑滚动
- **超大数字展示**：突出核心数据（832个贫困县）
- **数据可视化**：使用ECharts展示图表
- **响应式设计**：适配不同屏幕尺寸

## 使用方法

### 1. 启动后端API

```bash
# 在项目根目录
python run.py
```

确保API运行在 `http://localhost:5001`

### 2. 打开前端页面

直接使用浏览器打开 `frontend/index.html`，或使用本地服务器：

```bash
# 使用Python简单服务器
cd frontend
python -m http.server 8000

# 然后在浏览器访问
# http://localhost:8000
```

## 页面结构

### Section 1: Hero页面
- 超大数字"832"展示
- 核心标题和描述
- 导航按钮

### Section 2: 数据概览
- 贫困县总数
- 已摘帽县数
- 访谈记录数
- 调研员数

### Section 3: 县域探索
- 县列表展示
- 筛选功能（地区、省份）
- 搜索功能
- 点击查看详情

### Section 4: 县域详情
- 经济数据趋势图
- 农业数据柱状图
- 从Section 3点击县卡片进入

### Section 5: 访谈记录
- 访谈列表
- 关键词搜索
- 访谈内容预览

### Section 6: 对比分析
- 多县对比功能
- 输入县代码进行对比
- 趋势对比图表

## 技术栈

- **HTML5**：页面结构
- **TailwindCSS 3.0+**：样式框架（CDN）
- **FullPage.js**：全屏滚动
- **ECharts 5**：数据可视化
- **Font Awesome**：图标库
- **Google Fonts**：字体（Inter, JetBrains Mono）

## 自定义配置

### 修改API地址

编辑 `app.js` 文件：

```javascript
const API_BASE = 'http://your-api-url:5000/api';
```

### 修改颜色主题

编辑 `index.html` 中的CSS变量和渐变类。

## 注意事项

1. 确保后端API已启动并可以访问
2. 如果遇到CORS问题，检查后端CORS配置
3. 建议使用现代浏览器（Chrome, Firefox, Safari, Edge）

