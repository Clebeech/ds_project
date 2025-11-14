// API配置
// 开发环境：使用本地API
// 生产环境：部署后修改为实际的后端地址
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5001/api'
    : 'https://your-backend-url.railway.app/api';  // 部署后修改这里

