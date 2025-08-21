from contextlib import contextmanager
from typing import Iterator, Union
from packaging.version import Version
from importlib.metadata import version

import numpy
import h5py
from silx.io.url import DataUrl
from silx.io import h5py_utils
from ewokscore import TaskWithProgress
from ewoksdata.data import nexus
from ewoksdata.data import bliss
from ewoksdata.data.contextiterator import contextiterator

from .utils import data_utils


_LIMA_TEMPLATE_SUPPORTED = Version(version("blissdata")) >= Version("1.1.0")
_PRIORITIZE_NONNATIVEH5ITEMS_SUPPORTED = Version(version("blissdata")) >= Version(
    "2.0.0"
)


class TaskWithDataAccess(
    TaskWithProgress,
    optional_input_names=[
        "retry_timeout",
        "retry_period",
        "lima_url_template",
        "lima_url_template_args",
        "prioritize_non_native_h5items",
    ],
    register=False,
):
    def get_retry_options(self):
        retry_timeout = self.get_input_value("retry_timeout", None)
        retry_period = self.get_input_value("retry_period", None)
        return {"retry_timeout": retry_timeout, "retry_period": retry_period}

    def _get_blissdata_options(self):
        lima_url_template = self.get_input_value("lima_url_template", None)
        lima_url_template_args = self.get_input_value("lima_url_template_args", None)
        prioritize_non_native_h5items = self.get_input_value(
            "prioritize_non_native_h5items", False
        )
        if _LIMA_TEMPLATE_SUPPORTED:
            blissdata_options = {
                "lima_url_template": lima_url_template,
                "lima_url_template_args": lima_url_template_args,
                **self.get_retry_options(),
            }
            if _PRIORITIZE_NONNATIVEH5ITEMS_SUPPORTED:
                blissdata_options["prioritize_non_native_h5items"] = (
                    prioritize_non_native_h5items
                )
            return blissdata_options
        if lima_url_template:
            raise ValueError("'lima_url_template' requires blissdata>=1.1.0")
        if lima_url_template_args:
            raise ValueError("'lima_url_template_args' requires blissdata>=1.1.0")
        if prioritize_non_native_h5items:
            raise ValueError(
                "'prioritize_non_native_h5items' requires blissdata>=2.0.0"
            )
        return self.get_retry_options()

    @contextmanager
    def open_h5item(
        self,
        url: Union[str, DataUrl],
        create: bool = False,
        overwrite: bool = False,
        **openoptions,
    ) -> Iterator[Union[h5py.Group, h5py.Dataset, numpy.ndarray]]:
        if not isinstance(url, DataUrl):
            url = DataUrl(url)
        retryoptions = self.get_retry_options()
        if create:
            url = nexus.create_url(url, overwrite=overwrite, **retryoptions)
        with h5py_utils.open_item(
            url.file_path(), url.data_path(), **retryoptions, **openoptions
        ) as item:
            idx = url.data_slice()
            if idx is None:
                yield item
            else:
                yield item[idx]

    def get_data(self, *args, **kw):
        kw.update(self.get_retry_options())
        return bliss.get_data(*args, **kw)

    def get_image(self, *args, **kw):
        kw.update(self.get_retry_options())
        return bliss.get_image(*args, **kw)

    @contextiterator
    def iter_bliss_data(self, *args, **kw):
        kw.update(self._get_blissdata_options())
        with bliss.iter_bliss_scan_data(*args, **kw) as iterator:
            yield from iterator

    def iter_bliss_data_from_memory(self, *args, **kw):
        kw.update(self.get_retry_options())
        yield from bliss.iter_bliss_scan_data_from_memory(*args, **kw)

    def iter_bliss_scan_data_from_memory_slice(self, *args, **kw):
        kw.update(self.get_retry_options())
        yield from bliss.iter_bliss_scan_data_from_memory_slice(*args, **kw)

    def link_bliss_scan(self, *args, **kw):
        kw.update(self._get_blissdata_options())
        return data_utils.link_bliss_scan(*args, **kw)
