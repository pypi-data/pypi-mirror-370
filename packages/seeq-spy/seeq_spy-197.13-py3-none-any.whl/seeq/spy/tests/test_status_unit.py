import types

import pytest

from seeq import spy
from seeq.spy import Status

EXPECTED_DEFAULT_STATUS_WARNING_LIMIT = 20


@pytest.mark.unit
def test_warnings_limit():
    output = types.SimpleNamespace(lines=list())

    def _display_callback(_str):
        output.lines.append(_str)

    status = Status()
    status._display_callback = _display_callback

    for i in range(25):
        status.warn(f'Warning #{i}')

    status.update('Now what did I warn you about?', Status.RUNNING)
    status._finish()

    assert 'Now what did I warn you about?' in output.lines
    assert f'Warning #{EXPECTED_DEFAULT_STATUS_WARNING_LIMIT - 1}' in output.lines
    assert f'Warning #{EXPECTED_DEFAULT_STATUS_WARNING_LIMIT}' not in output.lines
    assert (f' + {25 - EXPECTED_DEFAULT_STATUS_WARNING_LIMIT} more warning(s) '
            f'[set spy.options.status_warning_limit higher to see more warnings]' in output.lines)

    output.lines.clear()

    spy.options.status_warning_limit = 10
    status = Status()
    status._display_callback = _display_callback

    for i in range(25):
        status.warn(f'Warning #{i}')

    status.update('Now what did I get warned about?', Status.RUNNING)
    status._finish()

    assert 'Now what did I get warned about?' in output.lines
    assert f'Warning #9' in output.lines
    assert f'Warning #10' not in output.lines
    assert (f' + 15 more warning(s) '
            f'[set spy.options.status_warning_limit higher to see more warnings]') in output.lines

    spy.options.status_warning_limit = EXPECTED_DEFAULT_STATUS_WARNING_LIMIT
