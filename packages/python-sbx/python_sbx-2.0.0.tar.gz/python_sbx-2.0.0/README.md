# Python SBX

一个用于网络代理管理的Python项目。

## 功能特性

- 支持多种代理协议（VLESS、VMess、Trojan、Hysteria2、TUIC、Reality）
- 自动节点管理和上传
- 支持哪吒面板监控
- Argo隧道支持
- Telegram机器人推送
- 自动保活功能

## 安装

```bash
pip install python-sbx
```

## 使用方法

### 命令行使用

```bash
python-sbx
```

### 环境变量配置

```bash
# 节点上传地址
export UPLOAD_URL="https://your-domain.com"

# 项目URL（用于自动保活）
export PROJECT_URL="https://your-project.com"

# 自动保活开关
export AUTO_ACCESS="true"

# 哪吒面板配置
export NEZHA_SERVER="nz.serv00.net:8008"
export NEZHA_KEY="your-secret-key"

# Argo隧道配置
export ARGO_DOMAIN="your-domain.com"
export ARGO_AUTH="your-auth-token"

# Telegram配置
export CHAT_ID="your-chat-id"
export BOT_TOKEN="your-bot-token"
```

## 开发

```bash
# 克隆项目
git clone https://github.com/yourusername/python-sbx.git
cd python-sbx

# 安装依赖
pip install -r requirements.txt

# 运行项目
python app.py
```

## 发布为PyPI包

### 🎉 包已成功构建！

项目已配置为可发布的PyPI包。构建文件位于 `dist/` 目录：

- `python_sbx-0.1.0.tar.gz` - 源码分发包
- `python_sbx-0.1.0-py3-none-any.whl` - 轮子分发包

### 下一步操作

1. **修改个人信息**：
   - 编辑 `setup.py` 中的作者名、邮箱、项目URL
   - 编辑 `pyproject.toml` 中的作者信息
   - 编辑 `LICENSE` 中的版权信息

2. **发布到PyPI**：
   ```bash
   # 使用自动化脚本（推荐）
   python publish.py
   
   # 或手动发布
   python -m twine upload dist/*
   ```

3. **测试安装**：
   ```bash
   pip install python-sbx
   python-sbx
   ```

### 发布前检查清单

- [ ] 修改所有配置文件中的个人信息
- [ ] 确保包名在PyPI上是唯一的
- [ ] 测试包是否能正确构建和安装
- [ ] 先在TestPyPI上测试，再发布到正式PyPI

## 项目文件结构

```
python-sbx/
├── app.py                 # 主程序文件
├── requirements.txt       # 依赖列表
├── setup.py              # 包配置（主要）
├── pyproject.toml        # 现代包配置
├── MANIFEST.in           # 包含文件配置
├── README.md             # 项目说明
├── LICENSE               # 许可证
├── publish.py            # 自动化发布脚本
├── test_build.py         # 配置测试脚本
├── PUBLISH_GUIDE.md      # 详细发布指南
└── QUICKSTART.md         # 快速开始指南
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 相关文档

- [发布指南](PUBLISH_GUIDE.md) - 详细的PyPI发布说明
- [快速开始](QUICKSTART.md) - 5分钟发布指南
