---
name: seo-opportunity-mapper
description: Maps SEO opportunities into a keyword opportunity table (intent, page_type, priority, stage, source, action_type) using product/ICP/site/competitor/GSC/Ahrefs/trend inputs without writing page content. Use when triaging keywords, building SEO backlog, or running the local Ahrefs/trends/competitor scripts in this repository.
---

# SEO Opportunity Mapper（项目技能）

## 范围

- **做**：归并输入 → 判断意图/页面类型/阶段/动作 → 输出机会表；可调用本目录下脚本拉取 Ahrefs、Google Trends、竞品页面结构。
- **不做**：不写落地页正文；完整增长执行请配合其他 SEO 流程。

## 输入

产品定位、ICP、站点已有页面、竞品列表、GSC 数据、Ahrefs 数据、外部趋势信号（与全局版一致）。

## 输出表字段

| keyword | intent | page_type | priority | stage | source | action_type |
|---------|--------|-----------|----------|-------|--------|-------------|

`action_type`: `new` | `refresh` | `consolidate` | `ignore`

## 本地脚本（数据拉取）

脚本路径：`.cursor/skills/seo-opportunity-mapper/scripts/`

| 脚本 | 作用 |
|------|------|
| `ahrefs_keyword_overview.py` | Keywords Explorer：官方 SDK `keywords_explorer_overview` |
| `ahrefs_competitor_organic_keywords.py` | Site Explorer：官方 SDK `site_explorer_organic_keywords`（需 API units） |
| `competitor_page_analyze.py` | 无 Ahrefs 时：抓取竞品 URL 的 title/meta/H 标签/链接等 |
| `google_trends_query.py` | Google Trends：兴趣随时间、相关查询 |

安装依赖：

```bash
cd /path/to/skillagent
python3 -m venv .venv
source .venv/bin/activate
pip install -r .cursor/skills/seo-opportunity-mapper/scripts/requirements.txt
```

复制环境变量：`cp .cursor/skills/seo-opportunity-mapper/.env.example .env` 并填入 `AHREFS_API_KEY`（Ahrefs 脚本需要）。

**详细参数、示例命令、API 注意点**：见 [reference.md](reference.md)。

## 判断规则摘要

- **intent**：高意图 vs 教育词 vs mixed（见 reference 中维度说明）。
- **page_type**：`tool` | `case_study` | `template` | `blog` | `comparison`。
- **stage**：`acquisition` | `activation` | `mixed_stage`。
- **source**：脚本输出可记为 `ahrefs_keyword`、`ahrefs_competitor`、`google_trends`、`competitor_page` 等。

将脚本导出的 CSV/JSON 作为证据行写入 `source` 或附件文件名，便于复盘。
