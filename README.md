# 考研数学模拟卷生成器

输入知识点，AI 自动生成考研数学（一）风格模拟卷，含答案和详细解析。

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 效果预览

| 输入 | 输出 |
|------|------|
| 知识点："中值定理" | 一套完整模拟卷：5 选择 + 5 填空 + 6 解答 |
| 知识点："极限" | 风格接近真题，附详细解析 |

> 提示：生成的试卷支持导出 Word 文档，可直接打印刷题。

---

## 使用教程

### 第一步：安装环境

**1.1 安装 Python**

- 打开 https://www.python.org/downloads/
- 点击 "Download Python 3.x.x"
- 安装时**勾选 "Add Python to PATH"**
- 验证：打开命令行输入 `python --version`，显示版本号即成功

**1.2 安装 Git**

- 打开 https://git-scm.com/download/win
- 下载并安装
- 验证：命令行输入 `git --version`

---

### 第二步：获取代码

```bash
git clone https://github.com/myer798/kaoyan-math-agent.git
cd kaoyan-math-agent
```

---

### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

如果下载慢，可以换国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 第四步：申请 API Key

本项目需要两个 API Key，会产生少量费用（见下方费用说明）：

#### 4.1 阿里云百炼（用于题目检索）

1. 打开 https://bailian.console.aliyun.com/
2. 登录/注册阿里云账号
3. 左侧菜单找到 **"API-KEY"**
4. 点击 **"创建我的 API-KEY"**
5. 复制生成的 Key（格式：`sk-xxxxxxxx`）

#### 4.2 DeepSeek（用于生成题目）

1. 打开 https://platform.deepseek.com/
2. 登录/注册账号
3. 左侧菜单找到 **"API keys"**
4. 点击 **"创建 API key"**
5. 复制生成的 Key（格式：`sk-xxxxxxxx`）

#### 4.3 费用说明

| 服务 | 费用 | 预估每次生成 |
|------|------|------------|
| 阿里云百炼 text-embedding-v3 | ¥0.0005/千 tokens | 约 ¥0.01-0.02 |
| DeepSeek Chat | ¥0.001/千 tokens（输入）<br>¥0.002/千 tokens（输出） | 约 ¥0.05-0.15 |

**生成一套试卷总成本：约 ¥0.1-0.2**

新用户通常有免费额度：
- 阿里云百炼：新用户送 100 万 tokens
- DeepSeek：新用户送 ¥10 余额

建议先充值少量金额（如 ¥10）测试，确认可用后再正常使用。

---

### 第五步：配置 Key

**方法 1：复制模板文件（推荐）**

1. 找到项目里的 `.env.example` 文件
2. 复制一份，改名为 `.env`
3. 用记事本打开 `.env`，把 Key 填进去：

```bash
# 把"你的Key"替换成刚才复制的
VISION_API_KEY=sk-你的阿里云Key
LLM_API_KEY=sk-你的DeepSeekKey
```

**方法 2：命令行创建**

```bash
# 复制模板
cp .env.example .env

# 然后用记事本编辑 .env 文件
```

---

### 第六步：启动！

```bash
python app.py
```

看到下面的输出就是成功了：

```
==================================================
  数学模拟卷生成系统
  浏览器打开: http://127.0.0.1:5000
  按 Ctrl+C 停止
==================================================
```

---

### 第七步：使用

1. 打开浏览器，输入 `http://127.0.0.1:5000`
2. 在输入框里填一个知识点，比如：**中值定理**
3. 点击"生成模拟卷"
4. 等待 10-30 秒，一套试卷就出来了！
5. 可以点击"导出 Word"下载打印

---

## 常见问题 FAQ

### Q1: 启动时报错 `ModuleNotFoundError: No module named 'flask'`

**A:** 依赖没装好，重新执行：
```bash
pip install -r requirements.txt
```

---

### Q2: 报错 `KeyError: 'VISION_API_KEY'` 或提示 Key 无效

**A:** 检查 `.env` 文件：
- 文件名是不是 `.env`（不是 `.env.example`）
- Key 是否填对了（没有多余的空格、引号）
- Key 是否有效（去阿里云/DeepSeek 后台确认）

---

### Q3: 生成试卷时卡住或报错

**A:** 可能原因：
- 网络问题，检查是否能访问阿里云和 DeepSeek
- API 额度用完了，去平台查看用量
- 换个知识点重试

---

### Q4: 可以修改题型数量吗？

**A:** 可以！编辑 `app.py` 文件，找到 `GEN_PROMPT`，修改里面的要求：

```python
# 比如改成 3 道选择题、3 道填空、4 道大题
"1. 选择题 3 道（每题 5 分）"
"2. 填空题 3 道（每题 5 分）"
"3. 解答题 4 道（每题 15 分，需写详细过程）"
```

---

### Q5: 支持其他科目吗？

**A:** 目前只支持考研数学一。但你可以：
- 修改 `data/index/vectors.json` 里的数据（需要重新处理真题）
- 或者修改 `GEN_PROMPT` 里的提示词，改成其他科目

---

### Q6: 生成的试卷版权归谁？

**A:** 
- 代码：MIT 开源，随便用
- 生成的试卷：你自己使用没问题，但**不要商用**（因为 AI 生成的题目可能涉及真题风格）
- 原始真题数据：版权归原作者所有，仅供学习

---

## 项目结构

```
kaoyan-math-agent/
├── app.py                 # 主程序（启动这个）
├── config.py              # 配置文件
├── .env.example           # Key 配置模板
├── .env                   # 你的 Key（需要自己创建）
├── requirements.txt       # 依赖列表
├── data/
│   └── index/
│       └── vectors.json   # 真题向量索引（已内置）
├── web/
│   └── index.html         # 网页界面
├── scripts/               # 数据处理脚本（一般用不到）
│   ├── 01_pdf_to_images.py
│   ├── 02_ocr_vision.py
│   ├── 03_structure_questions.py
│   ├── 04_build_index.py
│   └── 05_generate_paper.py
└── output/
    └── papers/            # 生成的试卷自动存这里
```

---

## 技术栈

| 组件 | 用途 |
|------|------|
| Python + Flask | 后端服务 |
| 阿里云百炼 text-embedding-v3 | 检索相似真题 |
| DeepSeek Chat | 生成新题目 |
| HTML + Tailwind + MathJax | 网页界面 |

---

## 免责声明

- 本项目仅供学习交流使用
- 真题数据来源于网络，版权归原作者所有
- 生成的模拟卷仅供参考，不代表真实考试难度
- 请勿用于商业用途

---

## 参与贡献

欢迎提交 Issue 或 Pull Request！

如果你觉得这个项目有用，请给个 ⭐ Star！

---

## License

MIT License
