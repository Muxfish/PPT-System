# 高级PPT生成系统

基于 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) 设计理念，使用 **Python + FastAPI + LangChain + DeepSeek + React** 构建的全栈智能 PPT 生成系统。

## 功能特性

### 🎨 双重视觉系统

| | Style A — 电子杂志×电子墨水 | Style B — 瑞士国际主义 |
|---|---|---|
| 风格 | Monocle杂志风、衬线字体、大片留白 | 16列网格、直角发丝线、高饱和锚点色 |
| 适合场景 | 个人分享、观点表达、线下私享会 | 产品分析、方法论、AI产品发布 |
| 配色主题 | 墨水经典 / 靛蓝瓷 / 森林墨 / 牛皮纸 / 沙丘 | IKB克莱因蓝 / 柠檬黄 / 柠檬绿 / 安全橙 |

### 🤖 AI 智能生成
- **DeepSeek 大模型**驱动的 PPT 内容生成
- **LangChain** 编排多步骤生成流水线：需求分析 → 大纲规划 → 内容增强 → 配图描述
- 支持 **SSE 流式输出**，实时查看生成进度
- **对话式迭代编辑**，与AI交互调整内容

### 🖼️ 丰富图片与背景

**四种幻灯片背景类型：**

| 类型 | 说明 | 效果 |
|------|------|------|
| 🎨 **渐变** | 60套精选CSS渐变，按内容情绪自动匹配 | 暖色/冷色/自然/科技/优雅/柔和等8类 |
| 📸 **摄影** | 基于关键词的Picsum高质量摄影图 | 免费、无需API Key、自动匹配内容 |
| 🔷 **几何** | 7种SVG几何图案（圆点/网格/波纹/六边形等） | 低干扰、专业感、适合数据页 |
| ⬜ **无背景** | 保持默认简洁风格 | 纯色背景 |

**三种图片布局：**

| 布局 | 效果 | 适用场景 |
|------|------|----------|
| `image-full` | 全屏大图 + 渐变遮罩 + 标题叠加 + 四角装饰 | 封面、章节开场 |
| `image-left` | 左侧图片 + 右侧文字内容 | 产品展示、案例介绍 |
| `image-right` | 右侧图片 + 左侧文字 | 交替展示、节奏变化 |

### 📄 单文件 HTML 导出
- 完整的单文件 HTML 演示文稿
- 支持键盘翻页（← →）、滚轮翻页、触屏滑动
- 瑞士风格支持 ESC 切换16列网格线
- 无需任何构建工具，浏览器直接打开

---

## 使用方法

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **DeepSeek API Key**（[获取地址](https://platform.deepseek.com/)）

### 第一步：启动后端

打开一个终端，执行：

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

看到以下输出表示启动成功：

```
[INFO] PPT Generation System starting on port 8001
[INFO] DeepSeek model: deepseek-chat
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 第二步：启动前端

打开另一个终端（保持后端运行），执行：

```bash
cd frontend
npm install
npm run dev
```

看到以下输出表示启动成功：

```
VITE v6.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 第三步：打开浏览器

在浏览器中访问 **http://localhost:5173**

### 第四步：创建PPT

#### 1. 选择风格
在首页点击「瑞士风 PPT」或「杂志风 PPT」按钮进入生成页，也可以在生成页顶部随时切换。

#### 2. 选择配色主题
点击色块预览选择喜欢的配色方案，生成页上方实色圆点即为当前主题色。

#### 3. 输入 PPT 主题
在文本框中描述你的PPT主题，越具体生成效果越好。例如：
- `2024年AI行业发展趋势分析`
- `我们产品的年度总结与未来展望`
- `新能源汽车市场的竞争格局与投资机会`

#### 4. 配置参数（可选）

| 参数 | 说明 | 可选值 |
|------|------|--------|
| 目标受众 | 影响措辞和深度 | 投资人、技术团队、学生… |
| 页数 | 大约生成页数 | 5 / 8 / 10 / 12 / 15 / 20 / 25 |
| 语言风格 | 影响表达方式 | 专业严谨 / 轻松活泼 / 学术研究 / 激励人心 / 极简风格 |
| 语言 | 输出语言 | 中文 / English |

#### 5. 高级选项（推荐展开）

- **幻灯片背景类型**：选择「渐变」「摄影」「几何」或「无背景」—— 让每页都有独特视觉效果
- **额外要求**：输入特殊需求，如"每页不超过50字"、"包含SWOT分析"、"多用数据对比"
- **自动生成配图**：开启后AI会为图片布局页自动生成配图关键词

#### 6. 点击「开始生成 PPT」

系统将通过 SSE 实时流式展示生成进度：
1. 分析主题需求
2. 生成PPT大纲结构（封面→目录→内容→总结→结束）
3. 逐页丰富内容细节
4. 为图片布局页生成配图关键词

#### 7. 预览与导出

生成完成后：
- 展开每页卡片查看详细内容（标题、正文、要点、配图描述）
- 点击「**预览 PPT**」进入全功能预览页
- 在预览页可以：
  - 切换**背景类型**（渐变/照片/几何/无）实时重新渲染
  - 切换**桌面/平板/手机**视口尺寸
  - 查看**HTML源码**或**复制源码**
  - 点击「**下载 HTML**」保存为单文件
  - 全屏预览

---

### 生成的 HTML 演示操作

| 操作 | 效果 |
|------|------|
| ← → 方向键 | 上一页 / 下一页 |
| 空格键 | 下一页 |
| 鼠标滚轮 | 翻页（800ms防抖） |
| 触屏滑动 | 移动端翻页 |
| Home / End | 跳转首页 / 末页 |
| 点击底部圆点 | 跳转到对应页 |
| ESC（瑞士风） | 显示/隐藏 16列网格线 |
| 底部左右箭头 | 上一页 / 下一页 |

---

## 项目结构

```
高级PPT生成系统/
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── main.py                # 应用入口 (uvicorn)
│   │   ├── api/routes.py          # API 路由 (7个端点)
│   │   ├── core/config.py         # 配置管理 (Pydantic Settings)
│   │   ├── models/schemas.py      # 数据模型 (14种布局 + 17种背景)
│   │   └── services/
│   │       ├── llm_service.py          # DeepSeek + LangChain 集成
│   │       ├── ppt_service.py          # PPT 多步骤生成流水线
│   │       ├── template_service.py     # HTML 双风格渲染引擎
│   │       └── bg_service.py           # 背景图片服务 (渐变/摄影/几何)
│   ├── requirements.txt
│   └── .env                       # DeepSeek API Key
│
├── frontend/                       # React + Vite 前端
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx           # 首页/风格选择/功能介绍
│   │   │   ├── GeneratePage.jsx       # PPT生成配置 (风格/主题/背景/参数)
│   │   │   └── PreviewPage.jsx        # HTML预览 (背景切换/视口/源码/下载)
│   │   ├── services/api.js            # API通信 + SSE流式
│   │   └── store/useStore.js          # Zustand 全局状态管理
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## API 接口

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/health` | — | 健康检查 |
| GET | `/api/themes` | — | 获取可用风格、主题、配色 |
| POST | `/api/generate-outline` | JSON body | 生成 PPT 大纲（JSON结构） |
| POST | `/api/generate-full` | JSON body | 生成完整 PPT（大纲+详细内容） |
| POST | `/api/enhance-slides` | JSON body | 增强已有大纲的每页内容 |
| POST | `/api/render-html` | `?bg_type=gradient\|photo\|pattern\|none` | 渲染为单文件 HTML |
| POST | `/api/stream-generate` | JSON body | SSE 流式生成（实时进度） |
| POST | `/api/chat` | JSON body | 对话式迭代编辑 |

### cURL 示例

```bash
# 生成大纲
curl -X POST http://localhost:8001/api/generate-outline \
  -H "Content-Type: application/json" \
  -d '{"topic":"AI如何改变教育行业","style":"style-b","slide_count":8,"language":"zh-CN"}'

# 渲染HTML（渐变背景）
curl -X POST "http://localhost:8001/api/render-html?bg_type=gradient" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","style":"style-b","theme":"ikb-blue","slides":[
    {"slide_number":1,"layout":"cover","title":"封面"},
    {"slide_number":2,"layout":"image-full","title":"全屏大图","body":"配图文案","image_placeholder":"科技数据流"},
    {"slide_number":3,"layout":"closing","title":"谢谢"}
  ]}'

# 渲染HTML（摄影背景）
curl -X POST "http://localhost:8001/api/render-html?bg_type=photo" \
  -H "Content-Type: application/json" \
  -d '{"title":"摄影背景测试","style":"style-a","theme":"ink-classic","slides":[...]}'
```

### 请求体字段说明

**PPTRequest:**
```json
{
  "topic": "PPT主题（必填）",
  "style": "style-a | style-b",
  "theme": "ink-classic | ikb-blue | ...",
  "audience": "目标受众",
  "slide_count": 10,
  "language": "zh-CN | en",
  "tone": "professional | casual | academic | inspirational | minimal",
  "bg_type": "gradient | photo | pattern | none",
  "include_images": false,
  "additional_requirements": "额外文字要求"
}
```

**SlideContent（每页结构）:**
```json
{
  "slide_number": 1,
  "layout": "cover | title-body | image-full | image-left | image-right | two-column | comparison | quote | big-number | timeline | grid-cards | section | closing",
  "title": "页标题",
  "subtitle": "副标题",
  "body": "正文内容（支持markdown）",
  "bullet_points": ["要点1", "要点2"],
  "image_placeholder": "配图关键词",
  "quote": "引用文字",
  "quote_author": "引用作者",
  "big_number": "100亿",
  "big_number_label": "数据说明"
}
```

---

## 环境变量

在 `backend/.env` 中配置：

```
DEEPSEEK_API_KEY=sk-your_key_here
DEEPSEEK_MODEL=deepseek-chat

# 可选配置
# APP_PORT=8001
```

> 注意：`APP_PORT` 需与 `frontend/vite.config.js` 中的 proxy target 端口保持一致。

---

## 背景图片系统详解

### 渐变类型（gradient）
60套精选CSS渐变按8种情绪分类，系统根据幻灯片内容关键词自动匹配：
- **暖色**：日落、珊瑚、桃梦、玫瑰花瓣
- **冷色**：深海、晨霜、极光、午夜蓝
- **自然**：林冠、薄荷、翡翠、鼠尾草
- **科技**：霓虹脉冲、数据流、量子辉光
- **优雅**：大理石、银线、珍珠、羊绒
- **大胆**：火山灰、绯红潮、黑曜石、电暴

### 摄影类型（photo）
使用 Picsum 免费图片服务，基于幻灯片内容关键词生成稳定种子URL。
- 封面页、章节页效果最佳
- 自动添加半透明遮罩层确保文字可读
- 每页根据标题/正文/要点自动提取关键词

### 几何类型（pattern）
7种SVG几何纹理：
- **圆点** — 均匀分布小圆点
- **网格** — 规整矩形网格线
- **对角线** — 斜线纹理
- **波纹** — 正弦波形
- **六边形** — 蜂巢纹理
- **十字** — 十字交叉线
- **三角** — 三角形连续图案

所有图案使用 accent 色并保持极低透明度（4-6%），不影响内容阅读。

---

## 设计来源

本项目基于歸藏（op7418）的开源项目 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) 的设计理念重新实现，是一个独立的全栈 Web 应用版本。

- 视觉系统参考：电子杂志×电子墨水风格、瑞士国际主义风格
- 布局系统扩展：新增 `image-full` `image-left` `image-right` 三种图片布局
- 背景系统原创：60套渐变、7种几何图案、智能关键词匹配摄影背景
