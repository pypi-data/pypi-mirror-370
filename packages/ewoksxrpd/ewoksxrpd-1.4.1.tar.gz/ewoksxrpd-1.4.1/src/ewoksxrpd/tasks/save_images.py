from typing import List
import h5py
from ewokscore import Task

from .utils.data_utils import save_image


class SaveImages(
    Task,
    input_names=["image_uris", "output_dir"],
    optional_input_names=["ext"],
    output_names=["output_paths"],
):
    """Save images with monitor and other metadata"""

    def run(self):
        image_uris: List[str] = self.inputs.image_uris
        output_dir: str = self.inputs.output_dir
        ext: str = self.get_input_value("ext", "edf")

        output_paths = []

        for image_uri in image_uris:
            image_filename, image_h5path = image_uri.split("::")

            with h5py.File(image_filename, "r") as h5file:
                image_dset = h5file[image_h5path]
                data = image_dset[()]
                monitor_data = image_dset.attrs.get("monitor", None)
                metadata = {k: v for k, v in image_dset.attrs.items() if k != "monitor"}

            output_paths.append(
                save_image(
                    data,
                    output_dir,
                    save_name=image_h5path.split("/")[-1],
                    monitor_data=monitor_data,
                    metadata=metadata,
                    ext=ext,
                )
            )

        self.outputs.output_paths = output_paths
