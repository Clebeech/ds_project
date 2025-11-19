# 访谈词云图实现方案

## 1. 技术选型

### 方案A：ECharts WordCloud 扩展（推荐）
- **优点**：与现有 ECharts 生态一致，样式统一，支持交互
- **缺点**：需要额外引入扩展库
- **实现难度**：⭐⭐ (简单)

### 方案B：WordCloud2.js
- **优点**：轻量级，纯JS实现
- **缺点**：样式需要自定义，与现有图表风格可能不一致
- **实现难度**：⭐⭐⭐ (中等)

## 2. 推荐方案：ECharts WordCloud

### 2.1 引入方式
```html
<!-- 在 index.html 中，ECharts 之后引入 -->
<script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.1.0/dist/echarts-wordcloud.min.js"></script>
```

### 2.2 数据准备
需要后端提供词频统计接口：
- `GET /api/interviews/wordcloud?county_code=xxx&surveyor_id=xxx`
- 返回格式：`[{name: '关键词', value: 频次}, ...]`

### 2.3 实现位置
建议在"田野访谈"页面（Section 5）添加词云图，可以：
- 放在访谈列表上方，作为整体关键词概览
- 或者放在右侧，与列表并排显示

## 3. 实现步骤

1. **后端**：创建词频统计接口（使用 Python `jieba` 分词 + `collections.Counter`）
2. **前端**：引入 echarts-wordcloud，添加词云图表容器
3. **交互**：点击词云中的词，可以筛选访谈记录

## 4. 中文分词处理

由于是中文访谈内容，需要：
- 后端使用 `jieba` 进行中文分词
- 过滤停用词（的、了、是、在等）
- 统计词频并返回

## 5. 预估工作量

- **后端接口**：30-40 分钟（分词 + 统计）
- **前端实现**：20-30 分钟（引入库 + 渲染）
- **总计**：约 1 小时

## 6. 效果预览

词云图将展示访谈内容中的高频关键词，字体大小反映词频，颜色可配置。点击词语可筛选相关访谈记录。

