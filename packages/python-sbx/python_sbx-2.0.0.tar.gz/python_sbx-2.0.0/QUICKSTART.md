# 快速开始指南

## 🚀 5分钟发布你的Python包

### 第一步：修改个人信息

编辑以下文件，将示例信息替换为你的真实信息：

1. **setup.py** - 修改作者名、邮箱、项目URL
2. **pyproject.toml** - 修改作者信息和项目URL
3. **LICENSE** - 修改版权信息

### 第二步：测试配置

```bash
python test_build.py
```

确保所有测试都通过。

### 第三步：发布包

#### 选项A：使用自动化脚本（推荐）

```bash
python publish.py
```

#### 选项B：手动发布

```bash
# 1. 安装必要工具
pip install build twine

# 2. 构建包
python -m build

# 3. 检查包
python -m twine check dist/*

# 4. 上传到测试PyPI
python -m twine upload --repository testpypi dist/*

# 5. 测试安装
pip install -i https://testpypi.python.org/simple/ python-sbx

# 6. 上传到正式PyPI
python -m twine upload dist/*
```

### 第四步：验证发布

```bash
# 从正式PyPI安装
pip install python-sbx

# 运行你的包
python-sbx
```

## 📁 项目文件结构

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
└── QUICKSTART.md         # 本文件
```

## ⚠️ 重要提醒

1. **包名唯一性**: 确保你的包名在PyPI上是唯一的
2. **版本管理**: 每次发布都要更新版本号
3. **测试先行**: 先在TestPyPI上测试，再发布到正式PyPI
4. **文档完整**: 提供清晰的README和使用说明

## 🔧 常见问题

**Q: 包名已被占用怎么办？**
A: 修改 `setup.py` 和 `pyproject.toml` 中的包名

**Q: 如何更新包？**
A: 修改版本号后重新构建和上传

**Q: 发布失败怎么办？**
A: 检查网络连接、认证信息和包配置

## 📚 更多帮助

- 查看 `PUBLISH_GUIDE.md` 获取详细说明
- 访问 [PyPI官方文档](https://packaging.python.org/)
- 运行 `python test_build.py` 检查配置

---

**祝你发布成功！** 🎉
