# LandPPT 启动指南

## 快速启动

```bash
# 1. 安装依赖
pip install -e .

# 2. 启动服务
python run.py
```

## 可选功能

### PPTX 导出支持

PPTX 导出功能需要 Apryse SDK（需要额外授权）：

```bash
pip install -e ".[pptx]"
```

## 启动后访问

- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **初始账号**: admin / admin123

## 故障排除

### 依赖缺失错误

如果遇到模块导入错误，运行：
```bash
pip install -e .
```

### 环境变量配置

确保 `.env` 文件存在且包含必要的 API 密钥：
