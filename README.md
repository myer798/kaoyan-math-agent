# 考研数学模拟卷生成器

输入知识点，AI 自动生成考研数学（一）风格模拟卷，含答案和详细解析。

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能特点

- 输入任意知识点（如"极限"、"中值定理"），自动生成完整模拟卷
- 题型包含：5 选择题 + 5 填空题 + 6 解答题
- 每题附答案和详细解析，公式用 LaTeX 渲染
- 基于 1987-2026 年考研数学一真题风格训练
- 支持导出 Word 文档
- 内置 2022-2026 年真题向量索引，开箱即用

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/kaoyan-math-agent.git
cd kaoyan-math-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
```

需要两个 Key：
- **阿里云百炼**：https://bailian.console.aliyun.com/ （用于向量检索）
- **DeepSeek**：https://platform.deepseek.com/ （用于生成题目）

### 4. 启动服务

```bash
python app.py
```

浏览器打开 http://127.0.0.1:5000 即可使用。

## 一键部署

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

部署后需要设置环境变量：
- `VISION_API_KEY`
- `LLM_API_KEY`

## 项目结构

```
kaoyan-math-agent/
├── app.py              # Flask Web 服务主程序
├── config.py           # 配置文件
├── .env.example        # 环境变量模板
├── requirements.txt    # Python 依赖
├── data/
│   └── index/
│       └── vectors.json    # 预构建的真题向量索引（2.6MB）
├── web/
│   └── index.html      # 前端页面
└── output/
    └── papers/         # 生成的试卷存档
```

## 技术栈

- **后端**：Python + Flask
- **向量检索**：阿里云百炼 text-embedding-v3
- **题目生成**：DeepSeek Chat
- **前端**：HTML + Tailwind CSS + MathJax

## 免责声明

- 本项目仅供学习交流使用
- 真题数据来源于网络，版权归原作者所有
- 生成的模拟卷仅供参考，不代表真实考试难度

## License

MIT License
