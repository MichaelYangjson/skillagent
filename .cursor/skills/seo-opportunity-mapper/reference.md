# SEO Opportunity Mapper — 脚本与 API 参考

## 环境准备

```bash
cd /path/to/skillagent
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r .cursor/skills/seo-opportunity-mapper/scripts/requirements.txt
```

在仓库根目录或当前 shell 中加载密钥（推荐 [direnv](https://direnv.net/) 或手动 `export`）：

```bash
export AHREFS_API_KEY="你的密钥"
# 可选：从文件加载
# set -a && source .cursor/skills/seo-opportunity-mapper/.env && set +a
```

### Ahrefs 说明

本仓库 Ahrefs 脚本使用 **官方 [Ahrefs Python SDK](https://github.com/ahrefs/ahrefs-python)**（与 [ahrefs-api-skills](https://github.com/ahrefs/ahrefs-api-skills) 推荐方式一致）：类型化 `AhrefsClient`、Pydantic 响应、内置重试与 `AhrefsError` 异常类型。

- 安装：`pip install -r .../scripts/requirements.txt`（已包含 `git+https://github.com/ahrefs/ahrefs-python.git`）。
- 若在 Cursor / Claude Code 中希望 Agent 熟悉全部 SDK 方法，可额外安装官方技能：`npx skills add ahrefs/ahrefs-api-skills --skill ahrefs-python --global`（可选）。
- HTTP 文档：[API v3 Introduction](https://docs.ahrefs.com/api/docs/introduction)、[Keyword overview](https://docs.ahrefs.com/api/reference/keywords-explorer/get-overview)、[Organic keywords](https://docs.ahrefs.com/api/reference/site-explorer/get-organic-keywords)。
- 鉴权：SDK 读取环境变量 `AHREFS_API_KEY`（等价于 `Authorization: Bearer ...`）。
- 非免费请求会消耗 **API units**；开发期请用 [free test queries](https://docs.ahrefs.com/api/docs/free-test-queries) 并限制 `limit` / `select`。
- 客户端默认对可恢复错误重试；仍可能遇 **429**，需退避。

### Google Trends 说明

- 脚本使用 **pytrends**（非官方），结果受区域/时间窗影响，适合趋势对比，不宜作为精确搜索量。
- 若频繁请求可能被限流；脚本已设较短延迟，仍建议不要高频批量跑。

### 竞品网页分析

- `competitor_page_analyze.py` 为静态 HTML 解析，**不执行 JavaScript**。SPA 或强依赖前端渲染的页面可能信息不全，需配合 Ahrefs 站内数据或手动查看。

---

## 1. Ahrefs — 关键词概览

**脚本**：`scripts/ahrefs_keyword_overview.py`

对一批关键词调用 SDK 方法 `keywords_explorer_overview`（对应 REST `keywords-explorer/overview`）。

```bash
export AHREFS_API_KEY="..."
python .cursor/skills/seo-opportunity-mapper/scripts/ahrefs_keyword_overview.py \
  --keywords "crm software,best crm for small business" \
  --country us \
  --out ahrefs_keywords.json
```

常用参数：

| 参数 | 说明 |
|------|------|
| `--keywords` | 逗号分隔；或与 `--keywords-file` 每行一词 |
| `--country` | ISO 3166-1 alpha-2，如 `us`、`gb`、`cn` |
| `--select` | 覆盖默认返回列（逗号分隔，需符合 API 文档字段名） |
| `--out` | 可选；默认打印 JSON 到 stdout |

输出含 `volume`、`difficulty`、`intents`、`traffic_potential` 等（取决于 API 与 `select`）。

---

## 2. Ahrefs — 竞品域名自然关键词

**脚本**：`scripts/ahrefs_competitor_organic_keywords.py`

调用 `site_explorer_organic_keywords`（对应 REST `site-explorer/organic-keywords`）。**消耗 API units**，请先用小 `limit`。

```bash
python .cursor/skills/seo-opportunity-mapper/scripts/ahrefs_competitor_organic_keywords.py \
  --target competitor.com \
  --mode subdomains \
  --country us \
  --date 2026-01-01 \
  --limit 50 \
  --out competitor_kw.json
```

| 参数 | 说明 |
|------|------|
| `--target` | 域名或 URL |
| `--mode` | `exact` / `prefix` / `domain` / `subdomains`（默认 `subdomains`） |
| `--date` | 指标日期 `YYYY-MM-DD`；省略则使用当天日期 |
| `--country` | 可选；不填则由 API 行为决定（建议显式指定市场） |
| `--select` | 列选择，默认含 keyword、排名、volume、url 等 |
| `--limit` | 行数上限 |

---

## 3. Google Trends

**脚本**：`scripts/google_trends_query.py`

```bash
python .cursor/skills/seo-opportunity-mapper/scripts/google_trends_query.py \
  --keywords "notion,ai workspace" \
  --geo US \
  --timeframe "today 12-m" \
  --out-prefix trends_out
```

生成（`--out-prefix` 为 `reports/trends` 时）：

- `reports/trends_interest_over_time.csv`
- `reports/trends_related_queries.json`

| 参数 | 说明 |
|------|------|
| `--keywords` | 最多约 5 个（Google 限制），逗号分隔 |
| `--geo` | 如 `US`、`CN`、空字符串表示全球 |
| `--timeframe` | 如 `today 3-m`、`today 12-m`、`2024-01-01 2024-12-31` |
| `--out-prefix` | 输出文件前缀 |

---

## 4. 竞品网页静态分析

**脚本**：`scripts/competitor_page_analyze.py`

```bash
python .cursor/skills/seo-opportunity-mapper/scripts/competitor_page_analyze.py \
  --url "https://competitor.com/landing" \
  --out page.json
```

| 参数 | 说明 |
|------|------|
| `--insecure` | 跳过 TLS 证书校验（仅调试或本机 CA 异常时使用） |

输出 JSON：状态码、`title`、meta description、canonical、`h1`–`h3`、内外链数量、正文词数估算等，用于判断页面类型与内容深度（配合机会表 `page_type` / `refresh`）。

---

## 将脚本结果并入机会表

1. Ahrefs / GSC 导出统一「主题级」去重后的 `keyword`。
2. `source` 列标注：`ahrefs_keyword`、`ahrefs_competitor`、`google_trends`、`competitor_page`、`gsc` 等。
3. Trends 仅作「是否上升/季节」信号，不替代搜索量；搜索量以 Ahrefs/GSC 为准。

---

## 故障排查

| 现象 | 处理 |
|------|------|
| Ahrefs `401` | 检查 `AHREFS_API_KEY`、密钥是否过期 |
| Ahrefs `429` | 降低 QPS；`sleep` 后重试 |
| Trends 空数据 | 换短 timeframe、减少关键词数、换 `geo` |
| 竞品页字段空 | 页面可能是 SPA；换 Ahrefs URL 级数据或手动查看 |
