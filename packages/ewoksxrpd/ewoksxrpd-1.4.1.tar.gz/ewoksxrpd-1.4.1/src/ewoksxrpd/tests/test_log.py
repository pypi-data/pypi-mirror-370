import re
import logging

from ..tasks.log import zip_with_progress


def test_zip_with_progress_one_iterator(caplog):
    with caplog.at_level(logging.INFO):
        values = list()
        for value, *_ in zip_with_progress([], message=_MESSAGE_TEMPLATE):
            values.append(value)

    assert not values
    _assert_finished_log(caplog, 0)

    with caplog.at_level(logging.INFO):
        values = list()
        for value, *_ in zip_with_progress([1], message=_MESSAGE_TEMPLATE):
            values.append(value)

    assert values == [1]
    _assert_finished_log(caplog, 1)

    with caplog.at_level(logging.INFO):
        values = list()
        for value, *_ in zip_with_progress([1, 2], message=_MESSAGE_TEMPLATE):
            values.append(value)

    assert values == [1, 2]
    _assert_finished_log(caplog, 2)


def test_zip_with_progress_two_iterators(caplog):
    with caplog.at_level(logging.INFO):
        values = list()
        for value, *_ in zip_with_progress([], [1, 2], message=_MESSAGE_TEMPLATE):
            values.append(value)

    assert not values
    _assert_finished_log(caplog, 0)

    with caplog.at_level(logging.INFO):
        values = list()
        for nr, letter, *_ in zip_with_progress(
            [1, 2], ["a"], message=_MESSAGE_TEMPLATE
        ):
            values.append((nr, letter))

    assert values == [(1, "a")]
    _assert_finished_log(caplog, 1)


_MESSAGE_TEMPLATE = "Integrated %s images of %s"


def _assert_finished_log(caplog, nimages):
    pattern = rf"Integrated {nimages} images of \? \(FINISHED: iteration=\d{{2}}:\d{{2}}:\d{{2}} \(\d{{1,3}}%\), TOTAL=\d{{2}}:\d{{2}}:\d{{2}} \(\d{{1,3}}%\)\)"
    string = str(caplog.text)
    err_msg = f"'{string}' does not match '{pattern}'"
    assert re.search(pattern, string), err_msg
