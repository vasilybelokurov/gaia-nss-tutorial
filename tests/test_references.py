"""Every chapter ends with a References section that lists every ADS paper cited in its text."""
import json
import re
from pathlib import Path

import pytest

NOTEBOOKS = sorted(Path(__file__).parent.parent.glob("notebooks/0*.ipynb"))
ADS = re.compile(r"https://ui\.adsabs\.harvard\.edu/abs/([0-9]{4}[A-Za-z&.]+[0-9A-Za-z.]*[0-9A-Z])")


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
def test_chapter_lists_every_cited_paper(path):
    cells = ["".join(c["source"]) for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "markdown"]
    refs = [c for c in cells if c.startswith("## References")]
    assert len(refs) == 1 and cells[-1] is refs[0], "the last markdown cell must be the References section"
    cited = set(ADS.findall("\n".join(cells[:-1])))
    listed = set(ADS.findall(refs[0]))
    assert cited <= listed, f"cited but not listed: {sorted(cited - listed)}"
