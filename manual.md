# 每日一练题库 · 数据格式说明（manual）

本文件描述题库软件的数据文件格式。软件本身不限定题库内容——任何符合下述结构的 JSON 都可以作为题库放入。

## 目录结构

```
管综题库/
├── index.html        前端（引擎，无需改动）
├── serve.py          本地服务（静态 + 写接口）
├── serve.py           启动脚本（python serve.py）
├── question/         题库目录：只放题库 json
│   ├── math.json
│   ├── logic.json
│   └── writing.json
└── userdata/         用户数据目录（自动生成，可定期备份）
    ├── flaw.json     错题本
    ├── favor.json    收藏夹
    └── proc.json     做题进度
```

## 一、题库文件（question/*.json）

### 顶层结构

```json
{
  "name": "数学",
  "desc": "管理类联考历年真题",
  "questions": [ ... ]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 科目名，显示在首页卡片 |
| `desc` | 否 | 副标题描述，显示在卡片与模式页 |
| `questions` | 是 | 题目数组 |

### 题目字段

```json
{
  "id": "2009-01",
  "year": 2009,
  "no": 1,
  "type": "single",
  "stem": "<p>题干，支持 HTML</p>",
  "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D", "E": "选项E"},
  "answer": "E",
  "analysis": "<p>解析，支持 HTML</p>",
  "tags": ["应用题"]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | **是（关键）** | 题目唯一标识。**进度、错题、收藏都以它为准**：题库删除后重新放入时，只要 id 不变，进度原样恢复。建议 `年份-序号` 格式 |
| `year` | 否 | 年份（数字）。驱动「按年份练习」模式；缺失则该题不进入年份列表 |
| `no` | 否 | 题号（数字）。年份模式下按它排序，建议从 1 连续 |
| `type` | 是 | `single` 单选题 / `suff` 条件充分性判断 / `browse` 浏览（无选项不判分，用于主观题） |
| `stem` | 是 | 题干，HTML 字符串。支持 `<p>` `<sup>` `<sub>` `<table class="qtbl">` `<span class="frac">` 等 |
| `options` | single 必填 | `{"A".."E": "选项文本"}`，选项文本同样支持 HTML |
| `cond` | suff 必填 | 条件数组：`["（1）……", "（2）……"]` |
| `answer` | single/suff 必填 | 正确答案字母 `A`–`E`。browse 类型不需要 |
| `analysis` | 否 | 解析，HTML 字符串 |
| `tags` | 否 | 分类标签数组，如 `["应用题"]`。驱动「按分类练习」模式；多选标签时取**并集**筛选。缺失或不含 tags 的题目不参与分类练习 |
| `QuestionHint` | 否 | 「选项含义」折叠区的文本数组。缺省时 suff 题使用内置的充分性判断说明，single 题无折叠区 |
| `No_Option_Details` | 否 | `true` 时选项只显示字母圈、隐藏文本（适合选项很长的题型） |

### 题型渲染行为

| type | 渲染 | 判分 |
|---|---|---|
| `single` | 题干 + A–E 选项 | 按 `answer` 判对错 |
| `suff` | 题干 + 条件区（cond）+ 固定 A–E 选项 | 同上；选项区支持 `No_Option_Details` |
| `browse` | 题干 + 「参考分析」折叠 | 不判分；结果页显示「已浏览 N 篇」 |

### HTML 排版速查（stem / options / analysis 内可用）

- `<span class="frac"><span>分子</span><span>分母</span></span>` —— 分数
- `√` 直接用字符；根号覆盖用 `<span class="rt">…</span>`
- `<sup>2</sup>` / `<sub>1</sub>` —— 上下标
- `<table class="qtbl"><tr><th>…</th></tr>…</table>` —— 数据表格

## 二、用户数据文件（userdata/，自动维护，一般不用手改）

### flaw.json（错题本）

答错自动收录（解析模式即时收、普通模式交卷时收），按 `科目+id` 去重并累计错误次数：

```json
{
  "name": "错题本",
  "desc": "答错的题自动收录",
  "questions": [
    {
      "id": "2009-01", "year": 2009, "no": 1, "type": "single",
      "stem": "……", "options": { "A": "……" }, "answer": "E", "analysis": "……",
      "tags": ["应用题"],
      "subject": "question/math.json", "subjectName": "数学",
      "myAnswer": "A", "wrongCount": 2, "lastWrong": "2026-10-20", "source": "daily"
    }
  ]
}
```

条目 = 题目完整快照 + `subject`（来源题库文件）/ `subjectName` / `myAnswer` / `wrongCount` / `lastWrong` / `source`（来源模式：daily/random/year/topic/flaw/favor）。

### favor.json（收藏夹）

```json
{
  "name": "收藏夹",
  "questions": [
    { "id": "2009-01", "……": "题目快照", "subject": "question/math.json", "subjectName": "数学", "favAt": "2026-10-20" }
  ]
}
```

### proc.json（做题进度）

```json
{
  "daily": {
    "question/math.json": {
      "order": ["2009-01", "……"],
      "cursor": 130,
      "date": "2026-10-20",
      "picks": ["……"],
      "ans": { "2009-01": "E" },
      "idx": 3,
      "done": false
    }
  },
  "sessions": {
    "question/math.json_rnd10": { "……": "同 daily 结构 + date" }
  }
}
```

- `daily`：每科目一份「每日一练」状态。`order` 是整库洗牌后的题目 id 序列，`cursor` 是下一次取题的偏移；跨天自动向后取 10 题，取完重新洗牌
- `sessions`：随机 / 年份 / 分类 / 错题重练 / 收藏重练的进行中局，同日刷新页面可续，跨天自动清空
- **进度与「题库文件路径 + 题目 id」绑定**：题库删掉再放回（文件名与 id 不变）即可无损续练

## 三、添加一个新科目

1. 把题库 json 放入 `question/`，例如 `english.json`
2. 打开 `index.html`，在 `DATA_FILES` 数组里加一行路径：
   ```js
   const DATA_FILES=["question/math.json","question/logic.json","question/writing.json","question/english.json"];
   ```
3. 刷新页面。文件不存在或 questions 为空时该科目自动隐藏，无需其他改动

## 四、本地服务与接口（serve.py）

- 默认 `http://127.0.0.1:8123`，仅监听本机回环，局域网无法访问
- `GET` 静态文件：index.html、question/、userdata/
- `POST /api/flaw`、`POST /api/favor`、`POST /api/proc`：分别写 userdata/ 下对应文件（临时文件 + 原子替换，不会写坏）
- 必须通过 serve.py 启动（`python serve.py`，默认 http://127.0.0.1:8123）；直接双击 index.html（file:// 打开）时写接口不可用，自动降级为浏览器 localStorage 暂存
