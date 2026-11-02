"""Exercise data-build safeguards with tiny files and no database connection."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def builder(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "build_data", Path(__file__).resolve().parents[1] / "scripts/build_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "OUT", tmp_path / "data_build")
    monkeypatch.setattr(module, "MANIFEST", tmp_path / "data/MANIFEST.json")
    # Any unexpected database access fails, even on a machine with WSDB credentials.
    def no_database(*args, **kwargs):
        pytest.fail("unexpected database access")
    monkeypatch.setattr(module.sqlutil, "get", no_database)
    return module


@pytest.mark.parametrize("scan", ["Seq Scan", "Parallel Seq Scan"])
def test_refuses_full_gaia_scan(builder, monkeypatch, scan):
    def explain(query, **kwargs):
        assert query == "EXPLAIN SELECT source_id FROM gaia_dr3.gaia_source"
        return ([f"{scan} on gaia_source g"],)
    monkeypatch.setattr(builder.sqlutil, "get", explain)
    with pytest.raises(RuntimeError, match="sequential scan"):
        builder.check_plan("SELECT source_id FROM gaia_dr3.gaia_source")


def test_accepts_index_plan(builder, monkeypatch):
    monkeypatch.setattr(builder.sqlutil, "get", lambda *a, **k: (
        ["Index Scan using gaia_source_source_id_idx on gaia_source g"],))
    builder.check_plan("SELECT source_id FROM gaia_dr3.gaia_source WHERE source_id = 1")


def test_rejects_checkpoint_from_different_selection(builder, monkeypatch):
    builder.OUT.mkdir()
    checkpoint = builder.OUT / "gcns100.partial.pkl"
    pd.to_pickle({"query": "old selection", "chunks": {}}, checkpoint)
    before = checkpoint.read_bytes()
    monkeypatch.setattr(builder, "check_plan", lambda q: None)
    with pytest.raises(RuntimeError, match="different query"):
        builder.build_scan("gcns100")
    assert checkpoint.read_bytes() == before
    assert not builder.MANIFEST.exists()


def test_save_round_trip_and_identical_rebuild(builder):
    df = pd.DataFrame({"source_id": [1, 2], "ra": [10.1, 20.2]})
    builder.save("sample", df, ["SELECT  source_id, ra FROM example"])
    path = builder.OUT / "sample.parquet"
    pd.testing.assert_frame_equal(pd.read_parquet(path), df)
    manifest = json.loads(builder.MANIFEST.read_text())
    manifest["sample"]["created_utc"] = "2000-01-01T00:00:00+00:00"
    builder.MANIFEST.write_text(json.dumps(manifest))
    before = builder.MANIFEST.read_bytes()
    entry = json.loads(before)["sample"]
    assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert entry["rows"] == 2 and entry["bytes"] == path.stat().st_size
    assert entry["queries"] == ["SELECT source_id, ra FROM example"]
    # Rebuilding identical bytes should also preserve their original provenance.
    builder.save("sample", df, ["SELECT source_id, ra FROM example"])
    assert builder.MANIFEST.read_bytes() == before


@pytest.mark.parametrize("change", ["data", "query"])
def test_existing_name_cannot_change(builder, change):
    df = pd.DataFrame({"source_id": [1]})
    builder.save("sample", df, ["SELECT 1"])
    path = builder.OUT / "sample.parquet"
    before = path.read_bytes(), builder.MANIFEST.read_bytes()
    changed = pd.DataFrame({"source_id": [2]}) if change == "data" else df
    query = "SELECT 2" if change == "query" else "SELECT 1"
    with pytest.raises(FileExistsError, match="new name"):
        builder.save("sample", changed, [query])
    assert (path.read_bytes(), builder.MANIFEST.read_bytes()) == before
    assert not list(builder.OUT.glob("*.tmp"))


def test_interrupted_parquet_write_preserves_previous_files(builder, monkeypatch):
    df = pd.DataFrame({"source_id": [1]})
    builder.save("sample", df, ["SELECT 1"])
    path = builder.OUT / "sample.parquet"
    before = path.read_bytes(), builder.MANIFEST.read_bytes()
    def interrupted(self, target, **kwargs):
        Path(target).write_bytes(b"partial parquet")
        raise OSError("simulated disk failure")
    monkeypatch.setattr(pd.DataFrame, "to_parquet", interrupted)
    with pytest.raises(OSError, match="simulated disk failure"):
        builder.save("sample", df, ["SELECT 1"])
    assert (path.read_bytes(), builder.MANIFEST.read_bytes()) == before
    assert not list(builder.OUT.glob("*.tmp"))


def test_hgca_rejects_changed_source_before_writing(builder, monkeypatch):
    import io
    import urllib.request
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(b'changed catalogue'))
    with pytest.raises(ValueError, match='HGCA source checksum mismatch'):
        builder.build('hgca_edr3')
    assert not builder.MANIFEST.exists()
    assert not builder.OUT.exists()


def test_epoch_extract_keeps_large_ids_precision_and_rejection_flags(builder, monkeypatch):
    import io
    import urllib.request
    ids = [5895765142704352640, 541801332594262912]
    responses = iter([
        pd.DataFrame({'source_id': [sid], 'transit_id': [sid + 1],
                      'g_transit_time': [1830.4415761242763],
                      'variability_flag_g_reject': [True]}).to_csv(index=False).encode()
        for sid in ids
    ])
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(next(responses)))
    builder.build('eb_epoch_examples')
    df = pd.read_parquet(builder.OUT / 'eb_epoch_examples.parquet')
    assert df.source_id.tolist() == ids
    assert df.transit_id.tolist() == [sid + 1 for sid in ids]
    assert df.variability_flag_g_reject.all()  # cleaning belongs in the student analysis, not the extraction
    assert abs(df.g_transit_time.iloc[0] - 1830.4415761242763) < 1e-10
    entry = json.loads(builder.MANIFEST.read_text())['eb_epoch_examples']
    assert entry['rows'] == 2 and len(entry['queries']) == 2


def test_epoch_extract_rejects_wrong_source(builder, monkeypatch):
    import io
    import urllib.request
    wrong = b'source_id,transit_id\n123,456\n'
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: io.BytesIO(wrong))
    with pytest.raises(AssertionError):
        builder.build('eb_epoch_examples')
    assert not builder.MANIFEST.exists()
