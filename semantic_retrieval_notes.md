# Day 40：语义检索整合

## 数据流

原始资料及 metadata
→ 使用 Embedding 模型生成向量
→ 组装 VectorRecord
→ 保存到 vectors.json
→ 新建 Repository 并重新加载
→ 查询生成向量
→ metadata 过滤、余弦相似度排序、取 Top-K
→ 使用记录 ID 计算 Recall@K

## 运行方式

在项目根目录依次执行：

```bash
uv run python -m ai_engineer_roadmap.build_vector_index
uv run python -m ai_engineer_roadmap.retrieval_evaluation
```

第一条命令会用脚本中的两条资料覆盖 vectors.json。

模型使用 sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2，
运行设备为 CPU。资料与查询使用同一个模型生成向量。
模型未缓存时需要下载。

## 2026-11-06 验证结果

- 两条资料分别生成 384 维向量。
- 保存后重新加载，完整记录比较通过。
- 限定 category=background、top_k=2，仅返回 memory-1。
- 不设置过滤条件时，复现 Day 39 基线：
  三个查询的 Recall@1 分别为 100%、100%、50%，平均 83.33%。

## 已知边界

- 仅使用两条教学资料，不能代表真实检索质量。
- metadata 过滤条件由程序提供，不会从自然语言自动推断。
- 当前完成检索与评测，尚未接入 LLM 回答。
