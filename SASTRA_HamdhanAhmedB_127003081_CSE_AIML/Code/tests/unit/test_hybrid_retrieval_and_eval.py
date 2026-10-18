import pytest
from backend.services.retrieval_service import BM25Index, tokenize
from backend.services.evaluation_service import run_evaluation_benchmark, load_benchmark_dataset
from backend.database.connection import SessionLocal
from backend.models import domain as models

def test_bm25_tokenization_and_scoring():
    corpus = [
        {"id": "doc1", "text_content": "Powertrain controller handles motor torque and throttle commands."},
        {"id": "doc2", "text_content": "Battery management system monitors cell voltage and temperature."}
    ]
    bm25 = BM25Index(corpus)
    
    # Query matching doc1
    q_tokens1 = tokenize("motor torque throttle")
    scores1 = bm25.score(q_tokens1)
    assert scores1[0] > scores1[1]

    # Query matching doc2
    q_tokens2 = tokenize("battery voltage cell")
    scores2 = bm25.score(q_tokens2)
    assert scores2[1] > scores2[0]

def test_evaluation_dataset_structure():
    dataset = load_benchmark_dataset()
    assert dataset["total_queries"] == 35
    queries = dataset["queries"]
    assert len(queries) == 35
    
    # Check technical queries vs adversarial
    tech_queries = [q for q in queries if not q.get("expected_unanswerable")]
    adv_queries = [q for q in queries if q.get("expected_unanswerable")]
    assert len(tech_queries) == 25
    assert len(adv_queries) == 10

def test_evaluation_benchmark_run():
    db = SessionLocal()
    try:
        # Create a test project with dummy chunk
        proj = models.Project(name="Eval Benchmark Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)

        # Run small 2-query benchmark
        results = run_evaluation_benchmark(
            db=db,
            project_id=proj.id,
            strategy="dense",
            top_k=3,
            max_queries=2
        )
        assert results["total_queries"] == 2
        assert "mrr" in results
        assert "hit_rate_at_1" in results
        assert "avg_latency_ms" in results
        assert len(results["per_query_results"]) == 2

        # Check BenchmarkRun persistence in database
        run_record = db.query(models.BenchmarkRun).filter(models.BenchmarkRun.id == results["run_id"]).first()
        assert run_record is not None
        assert run_record.total_queries == 2

    finally:
        db.close()
