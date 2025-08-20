# 发布说明

本文档说明如何将 `nonebot-plugin-dst-qq` 发布到 PyPI。

## 🚀 发布前准备

### 1. 安装必要工具

```bash
pip install build twine
```

### 2. 配置 PyPI 认证

创建 `.pypirc` 文件（已包含在项目中）：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDRlNjc0MDUxLWJjYjYtNGFiMi1hNjlhLWIzMDVkOTk2Y2E5MwACHVsxLFsibm9uZWJvdC1wbHVnaW4tZHN0LXFxIl1dAAIsWzIsWyIzODY0NDQ1OS0yZjViLTQ4OGMtYjdjOS0wNDBhOTNmMWZkNzkiXV0AAAYg7YSNGAIWwU1Xdsqvg3TcXVuJfz-gbaEbiNy7PgS8voM

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDRlNjc0MDUxLWJjYjYtNGFiMi1hNjlhLWIzMDVkOTk2Y2E5MwACHVsxLFsibm9uZWJvdC1wbHVnaW4tZHN0LXFxIl1dAAIsWzIsWyIzODY0NDQ1OS0yZjViLTQ4OGMtYjdjOS0wNDBhOTNmMWZkNzkiXV0AAAYg7YSNGAIWwU1Xdsqvg3TcXVuJfz-gbaEbiNy7PgS8voM
```

## 📦 发布步骤

### 方法一：使用脚本（推荐）

#### Linux/macOS
```bash
chmod +x publish.sh
./publish.sh
```

#### Windows PowerShell
```powershell
.\publish.ps1
```

#### Windows CMD
```cmd
python publish_to_pypi.py
```

### 方法二：手动发布

#### 1. 清理构建文件
```bash
rm -rf build/ dist/ *.egg-info/
```

#### 2. 构建包
```bash
python -m build
```

#### 3. 检查包
```bash
python -m twine check dist/*
```

#### 4. 上传到 PyPI
```bash
python -m twine upload dist/*
```

## 🔍 发布检查清单

发布前请确认：

- [ ] 版本号已更新（`pyproject.toml` 中的 `version`）
- [ ] 所有敏感信息已移除
- [ ] 依赖列表完整且版本正确
- [ ] 文档已更新
- [ ] 测试通过
- [ ] CHANGELOG.md 已更新

## 📋 发布后验证

发布完成后，验证：

1. **PyPI 页面**：https://pypi.org/project/nonebot-plugin-dst-qq/
2. **安装测试**：
   ```bash
   pip install nonebot-plugin-dst-qq==0.2.6
   ```
3. **功能测试**：确保插件能正常加载

## 🚨 注意事项

1. **版本号**：每次发布必须更新版本号
2. **敏感信息**：确保不包含 API 密钥、数据库文件等
3. **依赖管理**：确保所有依赖都已正确声明
4. **文档同步**：发布后更新 GitHub 仓库的 Release

## 🆘 常见问题

### 构建失败
- 检查 Python 版本是否符合要求
- 确认所有依赖已安装
- 检查 `pyproject.toml` 语法

### 上传失败
- 检查 `.pypirc` 配置
- 确认 PyPI 令牌有效
- 检查网络连接

### 包检查失败
- 检查包结构是否正确
- 确认所有必需文件已包含
- 验证元数据格式

## 📞 获取帮助

如果遇到发布问题，请：

1. 检查本文档的常见问题部分
2. 查看构建和上传的错误信息
3. 在 GitHub Issues 中反馈问题
4. 联系维护者：ui_101@qq.com
