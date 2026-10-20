# Questioner

通用刷题练习 Web 应用：单文件前端引擎 + 轻量 Python 静态服务，题库以 JSON 描述，开箱即用。

> 本仓库不包含真题等受版权保护的内容，仅附带一个演示格式的 `question/sample.json`。请自行将题库 JSON 放入 `question/` 目录。

## 功能

- **每日一练**：每天固定 10 题，跨天自动换新
- **随机刷题**：10 / 20 / 50 题可选
- **按年份顺序刷**：按题库内年份分组，按原卷顺序作答
- **按分类练习**：基于题库 JSON 的 tags 字段筛选
- **混合做题**：多选题库后随机抽取作答
- **错题本 / 收藏夹**：错题自动收录（带分类），可随时重练
- **解析模式**：每个题库可开关，答完一题立即显示解析
- **进度持久化**：做题进度、错题、收藏全部落盘到 `userdata/`，误删题库后重新放入（同 id）进度自动恢复

## 快速开始

```
双击 server.bat        # 启动本地服务并打开页面
```

或手动：

```
python serve.py        # 默认 http://127.0.0.1:8123
```

## 添加自己的题库

1. 在 `question/` 下放入符合格式的 JSON 文件，服务会自动发现，无需改代码
2. 字段说明见 [manual.md](manual.md)，仓库自带 `question/sample.json` 示例（三种题型各一）

## 目录结构

```
question/    题库 JSON（可随意增删）
userdata/    用户数据（proc.json 进度 / flaw.json 错题 / favor.json 收藏），删除后自动重建
index.html   前端引擎（单文件，无依赖）
serve.py     本地静态服务 + 用户数据写入 API
```

## License

[MIT](LICENSE) © 2026 Ayaka7452
