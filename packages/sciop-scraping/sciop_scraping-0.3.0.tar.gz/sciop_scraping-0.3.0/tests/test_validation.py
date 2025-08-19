import random
from pathlib import Path

import bagit
import pytest

from sciop_scraping.validation import pick_bagit_manifest, validate_bagit_manifest


@pytest.mark.parametrize("algo", ["sha256", "sha512", "md5"])
def test_valid_bagit(tmp_bagit: bagit.Bag, algo: str):
    """a valid bagit archive should be valid..."""
    errors = validate_bagit_manifest(tmp_bagit.path, algo)
    assert len(errors) == 0


@pytest.mark.parametrize("algo", ["sha256", "sha512", "md5"])
def test_invalid_bagit(tmp_bagit: bagit.Bag, algo: str):
    """an invalid bagit archive should not be valid..."""
    path = Path(tmp_bagit.path)
    with open(path / "data" / "regular.txt", "wb") as f:
        f.write(random.randbytes(32 * (2**10)))

    errors = validate_bagit_manifest(tmp_bagit.path, algo)
    assert len(errors) == 1
    assert errors[0].path == Path("data/regular.txt")
    assert errors[0].type_ == "incorrect"


def test_pick_manifest(tmp_path: Path) -> None:
    paths = [
        "manifest-md5.txt",
        "manifest-sha1.txt",
        "manifest-sha2.txt",
        "manifest-sha256.txt",
        "manifest-sha512.txt",
        "manifest-fakealgo.txt",
        "otherfile.txt",
    ]
    priority = ["sha1", "sha256", "sha512", "md5"]
    for path in paths:
        (tmp_path / path).write_text("sup")

    for _ in range(len(priority)):
        last = priority.pop(0)
        priority.append(last)
        manifest = pick_bagit_manifest(tmp_path, priority)
        assert manifest[0] == priority[0]
        assert manifest[0] in str(manifest[1])
        assert manifest[1].exists()


def test_reject_fake_algos(tmp_path: Path) -> None:
    """
    We can specify a custom algorithm priority, but if python doesn't have it in hashlib,
    we still error
    """
    algo = "fakealgo"
    (tmp_path / f"manifest-{algo}.txt").write_text("sup")
    with pytest.raises(FileNotFoundError):
        pick_bagit_manifest(tmp_path, [algo])


def test_detect_unranked_algos(tmp_path: Path) -> None:
    """
    we fall back to algos if prioritized ones aren't found, but ones in hashlib are
    """
    algo = "fakealgo"
    (tmp_path / "manifest-sha512.txt").write_text("sup")
    manifest = pick_bagit_manifest(tmp_path, [algo])
    assert manifest[0] == "sha512"
