"""
Helper methods for validation that might be used in multiple quests
"""

import hashlib
import re
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, cast

from tqdm import tqdm

if TYPE_CHECKING:
    from sciop_scraping.quests.base import ValidationError

BAGIT_MANIFEST = re.compile(r"^manifest-(?P<hash_type>\w+).txt$")
BAGIT_ALGO_PRIORITY = ("sha512", "sha256", "sha1", "md5")


class _BagitManifest(NamedTuple):
    hash_type: str
    path: Path


def pick_bagit_manifest(
    path: Path, algo_priority: tuple[str, ...] | list[str] = BAGIT_ALGO_PRIORITY
) -> _BagitManifest:
    """
    Given a bagit directory and a ranking of hash algorithms,
    pick the highest ranked algo, if any from the priority list are present.
    Otherwise, return any that are present.

    .. note:: Cursed implementation

        the implementation is in honor of a prior code golf implementation,
        and while it works, it should not serve as an indication of the
        attitude of the authors towards the mental health of its readers.

    raises:
        FileNotFoundError if no bagit manifests are present
    """
    manifests: list[_BagitManifest] = sorted(
        [
            _BagitManifest(hash_type=cast(str, match.group("hash_type")), path=p)
            for p in Path(path).iterdir()
            if p.is_file() and (match := BAGIT_MANIFEST.fullmatch(p.name))
        ],
        key=lambda manifest: (
            (in_ranking := manifest[0] in algo_priority),
            algo_priority.index(manifest[0]) if in_ranking else 0,
        ),
    )
    manifests = [m for m in manifests if m[0] in hashlib.algorithms_available]
    if not manifests:
        raise FileNotFoundError(f"No bagit manifests with supported hash algo found in {path}")
    return manifests[0]


def validate_bagit_manifest(
    path: Path, hash_type: str = "md5", remove: bool = False, hash_when_missing: bool = True
) -> list["ValidationError"]:
    """
    Given the base directory of a bagit directory that contains `manifest-{hash_type}.txt`
    and `data/` check the files against the manifest,
    returning ValidationErrors for missing or incorrect files.

    Args:
        path (Path): bagit directory
        hash_type (str): string name of hash algo,
            should match the file name abbreviation and be available by that name in hashlib
        remove (bool): If ``True``, remove invalid files (default False)
        hash_when_missing (bool): If ``False``, when files are missing, skip hash checking.
            If ``True``, hash files even if some are missing
    """
    from sciop_scraping.quests.base import ValidationError

    errors = []
    path = Path(path)
    manifest_path = path / f"manifest-{hash_type}.txt"

    if not manifest_path.exists():
        errors.append(
            ValidationError(
                type="manifest",
                path=manifest_path,
                msg="No manifest file found at expected location!",
            )
        )
        return errors

    with open(manifest_path) as f:
        manifest = f.read()

    lines = manifest.splitlines()
    # split into (hash, path) pairs
    items = [re.split(r"\s+", line.strip(), maxsplit=1) for line in lines]

    # first check for missing files, we know we're invalid if we have missing files
    # and can quit early
    for item in tqdm(items, desc="Checking for missing files"):
        expected_hash, sub_path = item
        abs_path = path / sub_path
        if not abs_path.exists():
            errors.append(
                ValidationError(type="missing", path=Path(sub_path), msg="File not found")
            )

    if not hash_when_missing and len(errors) > 0:
        return errors

    for item in tqdm(items, desc="Validating file hashes"):
        expected_hash, sub_path = item
        abs_path = path / sub_path
        with open(abs_path, "rb") as f:
            file_hash = hashlib.file_digest(f, hash_type).hexdigest()

        if file_hash != expected_hash:
            errors.append(
                ValidationError(type="incorrect", path=Path(sub_path), msg="Hash mismatch")
            )
            if remove:
                abs_path.unlink()
    return errors
