import glob

import h5py
import numpy
from ewoksorange.tests.utils import execute_task

from ..tasks.save_images import SaveImages

NUM_IMAGES = 5


def test_sum(tmpdir):
    image_uris = []
    with h5py.File(tmpdir / "output.h5", "w") as h5file:
        for i in range(NUM_IMAGES):
            image = h5file.create_dataset(str(i), data=numpy.random.random((100, 80)))
            image_uris.append(f'{tmpdir / "output.h5"}::{image.name}')

    inputs = {
        "output_dir": tmpdir,
        "image_uris": image_uris,
    }
    outputs = execute_task(
        SaveImages,
        inputs=inputs,
    )

    assert len(outputs["output_paths"]) == NUM_IMAGES
    assert sorted(glob.glob(str(tmpdir / "*.edf"))) == outputs["output_paths"]
