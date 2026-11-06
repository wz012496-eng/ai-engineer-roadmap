# Day 39：检索评估基线

## 评测配置

- 日期：2026-11-05
- 模型：sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 运行设备：CPU
- 资料文件：vectors.json
- 资料数量：2 条
- 相似度：余弦相似度
- K：1
- 查询数量：3 条
- 汇总方式：各查询的 Recall@1 等权平均

## 运行方式

在项目根目录执行：

uv run python -m ai_engineer_roadmap.retrieval_evaluation

## 评测结果

| 查询 | 预期相关 ID | 实际返回 ID | Recall@1 |
|---|---|---|---:|
| 如何利用我的安卓开发背景学习 AI？ | memory-1 | memory-1 | 100% |
| 我有什么饮食偏好？ | memory-2 | memory-2 | 100% |
| 我的开发背景和饮食偏好分别是什么？ | memory-1、memory-2 | memory-1 | 50% |

平均 Recall@1：83.33%。

## 已知局限

- 只有两条资料、三个查询，结果仅作为教学基线。
- Recall@K 不区分前 K 条结果内部的排序。
- 后续比较时，需要固定查询、相关性标注、资料和 K，
  并记录修改了哪项检索条件。
