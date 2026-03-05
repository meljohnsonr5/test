# 🔒 加密文件管理器

一个基于 Python + tkinter 的桌面应用程序，支持用户注册/登录，并对用户文件进行 AES-256 加密存储。

---

## 📌 项目简介

加密文件管理器是一个本地桌面应用，主要功能包括：

- **用户注册/登录**：使用 SQLite 存储用户信息，密码通过 PBKDF2-HMAC-SHA256 + 随机盐哈希，不存储明文密码
- **文件加密存储**：所有文件内容使用 AES-256（Fernet）加密后存储到本地磁盘，密钥由用户密码通过 PBKDF2 派生
- **可视化文件管理**：左右分栏界面，左侧列出加密文件，右侧为文本编辑器，支持新建、保存、删除
- **自动保存**：关闭程序时自动保存当前正在编辑的文件（加密后存储）

---

## 🖥️ 环境要求

| 条件 | 要求 |
|------|------|
| Python 版本 | 3.10 及以上（推荐 3.12） |
| 操作系统 | Windows / macOS / Linux |
| 额外依赖 | `cryptography >= 41.0.0`（见 requirements.txt） |

> tkinter 为 Python 标准库，通常无需额外安装。  
> 在 Ubuntu/Debian 上若缺少 tkinter，请执行：`sudo apt install python3-tk`

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <仓库地址>
cd <项目目录>
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 直接运行

```bash
python main.py
```

### 4. 打包为 exe（Windows）

**方式一：使用一键脚本**

```bat
build.bat
```

**方式二：手动执行**

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "加密文件管理器" main.py
```

打包完成后，可执行文件位于 `dist/` 目录。

### 5. 打包为可执行文件（Linux / macOS）

```bash
chmod +x build.sh
./build.sh
```

---

## 📖 使用说明

### 注册账号

1. 启动程序后出现登录窗口
2. 点击「注册」按钮，弹出注册对话框
3. 输入用户名、密码（≥6位）及确认密码
4. 点击「确认注册」，注册成功后返回登录窗口

### 登录

1. 在登录窗口输入已注册的用户名和密码
2. 点击「登录」或按回车键
3. 登录成功后进入主界面

### 管理文件

| 操作 | 方法 |
|------|------|
| 新建文件 | 点击工具栏「📄 新建文件」，输入文件名 |
| 查看/编辑文件 | 单击左侧文件列表中的文件名 |
| 保存文件 | 点击「💾 保存文件」或按 `Ctrl+S` |
| 删除文件 | 选中文件后点击「🗑 删除文件」 |
| 自动保存 | 关闭窗口时自动保存当前文件 |

> 所有文件以 AES-256 加密格式存储在 `data/<用户名>/` 目录下，扩展名为 `.enc`

---

## 📂 项目结构

```
├── README.md                  # 使用说明文档（本文件）
├── requirements.txt           # Python 依赖
├── build.bat                  # Windows 一键打包脚本
├── build.sh                   # Linux/Mac 打包脚本
├── main.py                    # 程序入口
├── app/
│   ├── __init__.py            # 包初始化
│   ├── login_window.py        # 登录/注册窗口
│   ├── main_window.py         # 主界面（左右分栏布局）
│   ├── crypto_manager.py      # 加密/解密管理（AES-256 + PBKDF2）
│   ├── user_manager.py        # 用户注册/登录（SQLite + 密码哈希）
│   └── file_manager.py        # 文件管理（CRUD + 加密存储）
└── data/                      # 加密文件存储目录（运行后自动创建）
    └── <用户名>/              # 每个用户独立目录
        └── *.enc              # 加密后的文件
```

---

## ❓ 常见问题 FAQ

**Q1: 忘记密码怎么办？**  
A: 由于密钥由密码派生，忘记密码将无法解密已有文件。目前版本不支持密码找回，请妥善保管密码。

**Q2: 加密文件可以在其他设备上打开吗？**  
A: 可以，将 `users.db` 和 `data/` 目录一并复制到其他设备，使用相同账号和密码登录即可。

**Q3: 在 Linux 上提示找不到 tkinter？**  
A: 执行 `sudo apt install python3-tk`（Debian/Ubuntu）或 `sudo dnf install python3-tkinter`（Fedora）。

**Q4: 打包后双击 exe 没有反应？**  
A: 可以尝试在命令行中运行 exe 查看错误信息。常见原因是缺少运行时依赖，可以尝试加 `--collect-all cryptography` 参数重新打包。

**Q5: 文件数据存储在哪里？**  
A: 用户数据库存储在程序运行目录下的 `users.db`，加密文件存储在 `data/<用户名>/` 目录下。

---

## 🔐 安全说明

- 密码使用 **PBKDF2-HMAC-SHA256**（480,000 次迭代）+ 随机盐哈希存储，安全性高
- 文件内容使用 **AES-256-CBC**（通过 Fernet 实现）加密，密钥由密码通过 PBKDF2 派生
- 程序不会在任何地方存储明文密码或明文文件内容
