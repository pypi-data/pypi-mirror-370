from __future__ import annotations

import os
import re

import pandas as pd
import pytest

from seeq import spy
from seeq.base import util
from seeq.spy.tests import test_common
from seeq.spy.workbooks import AnalysisWorksheet


def setup_module():
    test_common.initialize_sessions()


def _is_pandas_2_or_greater():
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", pd.__version__)
    major, minor, patch = map(int, match.groups())
    return (major, minor, patch) >= (2, 0, 0)


@pytest.mark.system
def test_csv_migration():
    if not _is_pandas_2_or_greater():
        # (markd 2025-06-23)
        # I'm getting
        # https://stackoverflow.com/questions/74063725/attributeerror-cant-get-attribute-unpickle-block-my-dump-and-load-versions
        # on earlier versions of Pandas and can't figure out why. So just skip this test.
        return

    job_folder = os.path.join(os.path.dirname(__file__), 'job_folder_csv_migration_tests')
    if util.safe_exists(job_folder):
        util.safe_rmtree(job_folder)

    try:
        _test_csv_migration_internal(job_folder)
    finally:
        # We have to remove the folder because it has long filenames, and when pytest scans that folder looking for
        # tests (the second time around), it will fail because it doesn't support long filenames properly.
        # Also, if we test with different versions of Pandas, the pickled files may be incompatible.
        if util.safe_exists(job_folder):
            util.safe_rmtree(job_folder)


def _test_csv_migration_internal(job_folder: str):
    spy.workbooks.job.unzip(f'{job_folder}.zip', overwrite=True)
    spy.workbooks.job.push(job_folder)
    spy.workbooks.job.data.push(job_folder)

    search_df = spy.workbooks.search({'Name': 'CSV Import Migration'})
    workbooks = spy.workbooks.pull(search_df)
    assert len(workbooks) == 1
    workbook = workbooks[0]
    assert len(workbook.worksheets) == 1

    item_inventory_df = workbook.item_inventory_df().set_index('Name', drop=False)
    assert len(item_inventory_df) == 5
    assert len(item_inventory_df[item_inventory_df['Type'] == 'Asset']) == 1
    assert len(item_inventory_df[item_inventory_df['Type'] == 'StoredSignal']) == 3
    assert item_inventory_df.at['Down Hole Data', 'Type'] == 'Asset'

    # noinspection PyTypeChecker
    worksheet: AnalysisWorksheet = workbook.worksheets[0]

    data_df = spy.pull(worksheet.display_items, start='2015-01-01', end='2025-01-01', grid=None)
    assert len(data_df) == 999
    assert sorted(data_df.columns) == sorted(['BLOCKCOMP(ft)', 'BITDEP(ft)', 'DEP_RTN(ft)'])
