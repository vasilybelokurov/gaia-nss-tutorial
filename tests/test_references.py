"""Every numbered chapter lists all ADS and modern arXiv citations in its final References section."""
import json
import re
from pathlib import Path

import pytest

NOTEBOOKS = sorted(Path(__file__).parent.parent.glob("notebooks/[0-9][0-9]_*.ipynb"))
ADS = re.compile(r"https://ui\.adsabs\.harvard\.edu/abs/([0-9]{4}[A-Za-z&.]+[0-9A-Za-z.]*[0-9A-Z])")
ARXIV = re.compile(r"https://arxiv\.org/abs/(\d{4}\.\d{4,5})")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
def test_chapter_lists_every_cited_paper(path):
    cells = ["".join(c["source"]) for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "markdown"]
    refs = [c for c in cells if c.startswith("## References")]
    assert len(refs) == 1 and cells[-1] is refs[0], "the last markdown cell must be the References section"
    for pattern in (ADS, ARXIV):
        cited = set(pattern.findall("\n".join(cells[:-1])))
        listed = set(pattern.findall(refs[0]))
        assert cited <= listed, f"cited but not listed: {sorted(cited - listed)}"


def test_missing_arxiv_reference_is_rejected(tmp_path):
    path = tmp_path / "chapter.ipynb"
    path.write_text(json.dumps({"cells": [
        {"cell_type": "markdown", "source": ["See https://arxiv.org/abs/2105.11662."]},
        {"cell_type": "markdown", "source": ["## References\n\nNo paper listed."]},
    ]}))
    with pytest.raises(AssertionError, match="cited but not listed"):
        test_chapter_lists_every_cited_paper(path)
