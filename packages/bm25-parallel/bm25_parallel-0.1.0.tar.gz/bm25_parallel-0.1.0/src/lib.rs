use bm25::{Language, SearchEngineBuilder};
use pyo3::prelude::*;

#[pyfunction]
fn build_and_search(
    docs: Vec<String>,
    queries: Vec<String>,
    top_k: usize,
) -> Vec<Vec<(u32, f64)>> {                 // ① 改成 u32
    // ② 泛型也换成 u32
    let engine = SearchEngineBuilder::<u32>::with_corpus(Language::English, &docs).build();

    queries
        .into_iter()
        .map(|q| {
            engine
                .search(&q, top_k)
                .into_iter()
                .map(|r| (r.document.id, r.score as f64))
                .collect()
        })
        .collect()
}

#[pymodule]
fn bm25_parallel(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_and_search, m)?)?;
    Ok(())
}