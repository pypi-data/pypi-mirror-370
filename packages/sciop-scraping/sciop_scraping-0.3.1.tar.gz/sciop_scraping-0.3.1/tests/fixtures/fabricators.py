import random
from pathlib import Path

import bagit
import pytest


@pytest.fixture()
def tmp_bagit(tmp_path: Path) -> bagit.Bag:
    """
    Make a bagit dataset w
    :param tmp_path:
    :return:
    """
    files = ["noextension", "regular.txt", "filename - with spaces.xml"]
    path = tmp_path / "bagit"
    path.mkdir()
    for file in files:
        with open(path / file, "wb") as f:
            f.write(random.randbytes(random.randint(2**10, 16 * (2**10))))
    bag = bagit.make_bag(str(path), checksums=["sha256", "sha512", "sha1", "md5"])
    return bag
