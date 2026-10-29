from math import sqrt


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        raise ValueError("零向量无法计算余弦相似度")

    return float(dot / (norm_a * norm_b))
