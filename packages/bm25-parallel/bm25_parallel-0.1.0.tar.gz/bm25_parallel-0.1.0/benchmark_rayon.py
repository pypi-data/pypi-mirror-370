# benchmark_rayon.py
import time
import random
from typing import List, Tuple
from tqdm import tqdm

from rank_bm25 import BM25Okapi
import bm25_parallel   # ← 我们自己编译的扩展

# ---------- 生成数据 ----------
def generate_docs(n: int, min_w: int, max_w: int) -> List[str]:
    vocab = ["the", "and", "for", "are", "but", "not", "you", "all", "can",
             "her", "was", "one", "our", "out", "day", "get", "has", "him",
             "his", "how", "its", "may", "new", "now", "old", "see", "two",
             "who", "boy", "did", "let", "put", "say", "she", "too", "use",
             "data", "system", "algorithm", "performance", "rust", "python",
             "benchmark", "search", "information", "retrieval", "token",
             "index", "query", "relevance", "score", "library", "implementation",
             "optimization"]
    docs = []
    for _ in tqdm(range(n), desc="Generating"):
        docs.append(" ".join(random.choices(vocab, k=random.randint(min_w, max_w))))
    return docs

# ---------- Python rank_bm25 ----------
def py_bm25(corpus: List[str], queries: List[str]) -> Tuple[float, float]:
    tok = [d.split() for d in corpus]
    t0 = time.perf_counter()
    engine = BM25Okapi(tok)
    t_idx = time.perf_counter() - t0

    t0 = time.perf_counter()
    for q in tqdm(queries, desc="Python querying"):
        engine.get_scores(q.split())
    t_qry = time.perf_counter() - t0
    return t_idx, t_qry

# ---------- Rust + Rayon ----------
def rs_bm25(corpus: List[str], queries: List[str]) -> Tuple[float, float]:
    t0 = time.perf_counter()
    # build 阶段已经并行，返回的是纯 Rust 句柄
    _ = bm25_parallel.build_and_search(corpus, queries[:1], 10)  # warm-up
    t_idx = time.perf_counter() - t0

    t0 = time.perf_counter()
    _ = bm25_parallel.build_and_search(corpus, queries, 10)
    t_qry = time.perf_counter() - t0
    return t_idx, t_qry

# ---------- 主流程 ----------
if __name__ == "__main__":
    N, MIN_W, MAX_W = 100_000, 50, 300
    N_Q = 1_000

    docs = generate_docs(N, MIN_W, MAX_W)
    vocab = [w for d in docs for w in d.split()]
    queries = [" ".join(random.choices(vocab, k=random.randint(5, 12)))
               for _ in range(N_Q)]

    print("=" * 60)
    print(f"数据集：{N} 篇文档，{N_Q} 条查询")

    py_idx, py_qry = py_bm25(docs, queries)
    rs_idx, rs_qry = rs_bm25(docs, queries)

    print("\n结果（秒）")
    print("-" * 60)
    print(f"{'':<12} {'Python':<12} {'Rust+Rayon':<12} {'Speedup':<12}")
    print(f"{'Indexing':<12} {py_idx:<12.3f} {rs_idx:<12.3f} {py_idx/rs_idx:<12.1f}x")
    print(f"{'Querying':<12} {py_qry:<12.3f} {rs_qry:<12.3f} {py_qry/rs_qry:<12.1f}x")