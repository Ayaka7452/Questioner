# 每日一练题库 · 数据格式说明（manual）

本文件描述题库软件的数据文件格式。软件本身不限定题库内容——任何符合下述结构的 JSON 都可以作为题库放入。

## 目录结构

```
管综题库/
├── index.html        前端（引擎，无需改动）
├── serve.py          本地服务（静态 + 写接口），python serve.py 启动
├── question/         题库目录：只放题库 json（自动发现，无需改码）
│   ├── guanzong.json 管综真题（单文件维度化题库）
│   └── sample.json   示例题库
└── userdata/         用户数据目录（自动生成，可定期备份）
    ├── flaw.json     错题本
    ├── favor.json    收藏夹
    ├── proc.json     做题进度
    └── merge.json    合并做题范围
```

## 一、题库文件（question/*.json）

一个 JSON 文件 = 一个题库。一个题库内可以混合任意「类型」的题目（如数学/逻辑/写作），类型通过**自定义维度字段**区分，引擎动态识别，不写死。

### 顶层结构

```json
{
  "name": "管综真题",
  "desc": "2009-2025 管理类综合能力真题",
  "dims": [
    {"key": "year", "label": "年份"},
    {"key": "subject", "label": "科目"},
    {"key": "tags", "label": "分类"}
  ],
  "questions": [ ... ]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 题库名，显示在首页卡片 |
| `desc` | 否 | 副标题描述 |
| `dims` | 否 | 维度声明：`key` 对应题目里的自定义字段名，`label` 是界面显示名。只影响显示文案与排序，**不声明也能用**（引擎自动从题目字段发现维度，label 直接用字段名） |
| `questions` | 是 | 题目数组。**数组顺序即「套卷顺序」**——勾选「套卷顺序」时按此顺序作答 |

### 题目字段

题目 = **核心字段**（引擎认识）+ **自定义维度字段**（引擎不认识、动态发现）。

核心字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 全局唯一标识，进度/错题/收藏都挂在它上面，**建档后不可更改** |
| `type` | 是 | `single` 单选 / `suff` 条件充分性判断 / `browse` 浏览（无选项，只看解析） |
| `stem` | 是 | 题干（HTML，可用 `<p>` 等） |
| `options` | single/suff 必填 | `{ "A": "选项文本", ... }` |
| `answer` | 是 | 正确答案字母（browse 可空） |
| `analysis` | 是 | 解析（HTML） |
| `no` | 否 | 卷面题号，显示用 |
| `cond` | 否 | suff 题的条件列表（字符串数组） |
| `QuestionHint` | 否 | 选项含义提示（字符串数组，折叠显示） |
| `No_Option_Details` | 否 | `true` 时选项只显示字母不显示文本 |

自定义维度字段（示例，**完全自由**，可以没有、也可以叫别的名字）：

| 示例字段 | 取值 | 引擎行为 |
|---|---|---|
| `year` | `2015`（标量） | 出现为「年份」筛选项；数值自动降序排列 |
| `subject` | `"管综数学"` | 出现为「科目」筛选项；做题页显示为标签 |
| `tags` | `["数列","函数"]`（数组） | 多值维度：同维度多选=并集，跨维度=交集 |

- 维度取值支持标量或字符串数组，引擎统一按字符串比较。
- 想加新维度（如 `chapter`、`difficulty`）直接在题目上加字段即可，界面自动出现对应筛选，无需改代码。
- 避免使用核心字段名。

### HTML 书写速查

| 写法 | 效果 |
|---|---|
| `<p>...</p>` | 段落 |
| `<span class="frac"><span>a</span><span>b</span></span>` | 分数 a/b |
| `<span class="rt">x</span>` | 根号 |
| `<table class="qtbl">...</table>` | 紧凑表格 |
| `x<sup>2</sup>` | 上标 |

## 二、用户数据（userdata/*.json）

- `proc.json`：`{"daily":{题库键:当日状态},"sessions":{题库键_模式键:会话}}`。进度绑定「题库文件路径 + 题目 id」——题库删除后重新放入（同 id），进度自动恢复。
- `flaw.json` / `favor.json`：`{"name","desc","questions":[...]}`，每条含 `subject`（题库路径）、`subjectName`（题库名）、`id` 及题目快照。
- `merge.json`：`{"banks":[...]}` 合并做题的题库范围，自动保存。
- `userdata/` 整目录删除后，服务会在下次写入时自动重建；浏览器 localStorage 有同内容兜底缓存。

## 三、添加新题库（3 步）

1. 按上述结构写一个 JSON，放进 `question/`
2. 刷新页面，服务通过 `/api/list` 自动发现，无需改代码
3. 题目里的自定义字段会自动变成筛选项；建议在顶层 `dims` 里声明中文 label

## 四、serve.py API

- `GET /api/list`：列出 `question/` 下全部 .json
- `POST /api/flaw|favor|proc|merge`：写入对应 userdata 文件（原子替换；userdata 缺失自动重建；proc/merge 免 `questions` 结构检查）
- 必须通过 `python serve.py` 启动；直接双击 index.html（file:// 打开）时写接口不可用，自动降级为浏览器 localStorage 暂存
