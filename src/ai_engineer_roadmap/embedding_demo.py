from math import sqrt

from sentence_transformers import SentenceTransformer


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        raise ValueError("零向量无法计算余弦相似度")

    return float(dot / (norm_a * norm_b))


model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu"
)

sentences = [
    "我有 Android 开发经验",
    "我做过安卓应用开发",
    "今天晚上吃火锅",
]

embeddings = model.encode(sentences)

print("向量数组的形状：", embeddings.shape)
print("第一句向量的前 5 个数：", embeddings[0][:5])

similarities = model.similarity(embeddings, embeddings)

print("Android 与安卓：", similarities[0, 1].item())
print("Android 与火锅：", similarities[0, 2].item())


memory_texts = [
    "用户有 Android 开发经验",
    "用户喜欢吃火锅",
]
query = "如何利用我的安卓开发背景学习 AI？"

memory_vectors = model.encode(memory_texts)
query_vector = model.encode([query])

scores = model.similarity(query_vector, memory_vectors)[0]
best_index = scores.argmax().item()

print("候选记忆的分数：", scores.tolist())
print("检索结果：", memory_texts[best_index])


manual_score = cosine_similarity(embeddings[0], embeddings[1])
library_score = similarities[0, 1].item()

print("手动计算：", manual_score)
print("库函数计算：", library_score)
