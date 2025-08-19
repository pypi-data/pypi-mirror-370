import os
import h5py
import pytest
from contextlib import ExitStack

from ..tasks.utils import data_utils


@pytest.mark.parametrize("relative", [True, False], ids=["relative", "absolute"])
def test_hdf5_external_link(tmp_path, relative):
    topdir = tmp_path / "rootdir"
    middir = topdir / "middir"
    lowdir = middir / "lowdir"
    lowdir.mkdir(parents=True)

    with ExitStack() as stack:
        external_up = stack.enter_context(
            h5py.File(str(topdir / "external_up.h5"), mode="a")
        )
        master = stack.enter_context(h5py.File(str(middir / "master.h5"), mode="a"))
        external_down = stack.enter_context(
            h5py.File(str(lowdir / "external_down.h5"), mode="a")
        )

        external_up["external_data"] = 1
        master["/1.1/instrument/diode2/data"] = 2
        external_down["external_data"] = 3

        # Down-link to external data
        link = data_utils.hdf5_link_object(
            master.filename,
            "/1.1/instrument/diode3",
            "data",
            external_down.filename,
            "external_data",
            relative=relative,
        )
        assert type(link) is h5py.ExternalLink
        assert link.path == "external_data"
        if relative:
            assert link.filename == os.path.join("lowdir", "external_down.h5")
        else:
            assert link.filename == external_down.filename

        data_utils.create_hdf5_link(
            master,
            "/1.1/instrument/diode3/data",
            external_down["external_data"],
            relative=relative,
            raise_on_exists=True,
        )

        # Up-link to external data
        link = data_utils.hdf5_link_object(
            master.filename,
            "/1.1/instrument/diode1",
            "data",
            external_up.filename,
            "external_data",
            relative=relative,
        )
        assert type(link) is h5py.ExternalLink
        assert link.path == "external_data"
        if relative:
            assert link.filename == os.path.join("..", "external_up.h5")
        else:
            assert link.filename == external_up.filename

        data_utils.create_hdf5_link(
            master,
            "/1.1/instrument/diode1/data",
            external_up["external_data"],
            relative=relative,
            raise_on_exists=True,
        )

        # Create external link again
        data_utils.create_hdf5_link(
            master,
            "/1.1/instrument/diode3/data",
            external_down["external_data"],
            relative=relative,
        )
        with pytest.raises(Exception, match="name already exists"):
            data_utils.create_hdf5_link(
                master,
                "/1.1/instrument/diode3/data",
                external_down["external_data"],
                relative=relative,
                raise_on_exists=True,
            )

        # Check whether links resolve
        assert master["/1.1/instrument/diode1/data"][()] == 1
        assert master["/1.1/instrument/diode2/data"][()] == 2
        assert master["/1.1/instrument/diode3/data"][()] == 3

    # Check whether links after moving the files
    topdir.rename(tmp_path / "newname")
    topdir = tmp_path / "newname"
    middir = topdir / "middir"
    lowdir = middir / "lowdir"

    with h5py.File(str(middir / "master.h5"), mode="r") as master:
        assert master["/1.1/instrument/diode2/data"][()] == 2
        if relative:
            assert master["/1.1/instrument/diode1/data"][()] == 1
            assert master["/1.1/instrument/diode3/data"][()] == 3
        else:
            with pytest.raises(KeyError):
                master["/1.1/instrument/diode1/data"]
            with pytest.raises(KeyError):
                master["/1.1/instrument/diode3/data"]


@pytest.mark.parametrize("relative", [True, False], ids=["relative", "absolute"])
def test_hdf5_internal_link(tmp_path, relative):

    with h5py.File(str(tmp_path / "master.h5"), mode="a") as root:
        root["data"] = 1
        root["midgroup/data2"] = 2
        root["midgroup/lowgroup/data"] = 3
        internal_up = root
        master = root["midgroup"]
        internal_down = root["midgroup/lowgroup"]

        # Link to self
        link = data_utils.hdf5_link_object(
            root.filename, "", "data", root.filename, "/data", relative=relative
        )
        assert link is None
        link = data_utils.hdf5_link_object(
            root.filename, "/", "data", root.filename, "/data", relative=relative
        )
        assert link is None
        link = data_utils.hdf5_link_object(
            root.filename, "/", "data", root.filename, "data", relative=relative
        )
        assert link is None
        link = data_utils.hdf5_link_object(
            root.filename, "", "data", root.filename, "data", relative=relative
        )
        assert link is None
        data_utils.create_hdf5_link(
            root, "/data", root["data"], relative=relative, raise_on_exists=True
        )

        # Down-link to internal data
        link = data_utils.hdf5_link_object(
            root.filename,
            "/midgroup",
            "data3",
            root.filename,
            "/midgroup/lowgroup/data",
            relative=relative,
        )
        assert type(link) is h5py.SoftLink
        if relative:
            assert link.path == "lowgroup/data"
        else:
            assert link.path == "/midgroup/lowgroup/data"

        data_utils.create_hdf5_link(
            master,
            "/midgroup/data3",
            internal_down["data"],
            relative=relative,
            raise_on_exists=True,
        )

        # Up-link to internal data
        link = data_utils.hdf5_link_object(
            root.filename,
            "/midgroup/data1",
            "data",
            root.filename,
            "data",
            relative=relative,
        )
        assert type(link) is h5py.SoftLink
        assert link.path == "/data"

        data_utils.create_hdf5_link(
            master,
            "/midgroup/data1",
            internal_up["data"],
            relative=relative,
            raise_on_exists=True,
        )

        # Create internal link again
        data_utils.create_hdf5_link(
            master, "/midgroup/data3", internal_down["data"], relative=relative
        )
        with pytest.raises(Exception, match="name already exists"):
            data_utils.create_hdf5_link(
                master,
                "/midgroup/data3",
                internal_down["data"],
                relative=relative,
                raise_on_exists=True,
            )

        # Check whether links resolve
        assert master["/midgroup/data1"][()] == 1
        assert master["/midgroup/data2"][()] == 2
        assert master["/midgroup/data3"][()] == 3
