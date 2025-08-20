from unittest.mock import patch

import pandas as pd
import pytest

from seeq import spy
from seeq.sdk.rest import ApiException
from seeq.spy import _common, SPyTypeError, SPyValueError, Status
from seeq.spy.tests import test_common


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_archive_metadata_df():
    test_name = f'test_archive_metadata_df_{_common.new_placeholder_guid()}'
    items = create_items(test_name)

    results = spy.archive(items)
    assert len(results) == 4
    # noinspection PyTypeChecker
    assert all(results['Result'] == 'Success')
    assert results.spy.status.df.at[0, 'Count'] == 4
    assert results.spy.status.df.at[0, 'Time'] is not None
    assert results.spy.status.code == Status.SUCCESS
    assert 'Successfully archived 4 of 4 items' in results.spy.status.message

    # Verify the items are actually archived
    re_pull = spy.search(items, all_properties=True)
    assert all(re_pull['Archived'])


@pytest.mark.system
def test_archive_tree_df():
    test_name = f'test_archive_tree_df_{_common.new_placeholder_guid()}'
    sub_items = create_items(test_name)
    tree = spy.assets.Tree(test_name, workbook=test_name)
    tree.insert(sub_items)
    items = tree.push()

    results = spy.archive(tree.df)
    assert len(results) == 5
    # noinspection PyTypeChecker
    assert all(results['Result'] == 'Success')
    assert results.spy.status.df.at[0, 'Count'] == 5
    assert results.spy.status.df.at[0, 'Time'] is not None
    assert results.spy.status.code == Status.SUCCESS
    assert 'Successfully archived 5 of 5 items' in results.spy.status.message

    # Verify the items are actually archived
    re_pull = spy.search(items, all_properties=True)
    assert all(re_pull['Archived'])


@pytest.mark.system
def test_archive_workbooks_df():
    test_name = f'test_archive_workbooks_df_{_common.new_placeholder_guid()}'
    workbook_1 = spy.workbooks.Analysis(f'{test_name}_1')
    workbook_1.worksheet(test_name)
    workbook_2 = spy.workbooks.Analysis(f'{test_name}_2')
    workbook_2.worksheet(test_name)
    spy.workbooks.push([workbook_1, workbook_2])
    items = spy.workbooks.search({'Name': test_name})

    results = spy.archive(items)
    assert len(results) == 2
    # noinspection PyTypeChecker
    assert all(results['Result'] == 'Success')
    assert results.spy.status.df.at[0, 'Count'] == 2
    assert results.spy.status.df.at[0, 'Time'] is not None
    assert results.spy.status.code == Status.SUCCESS

    # Verify the items are actually archived
    re_pull = spy.workbooks.search({'Name': test_name}, include_archived=True)
    assert all(re_pull['Archived'])


@pytest.mark.system
def test_archive_empty_df():
    results = spy.archive(pd.DataFrame(columns=['ID']))
    assert len(results) == 0
    assert results.spy.status.df.at[0, 'Count'] == 0
    assert 'Successfully archived 0 of 0 items' in results.spy.status.message


@pytest.mark.system
def test_archive_invalid_args():
    with pytest.raises(SPyTypeError, match="Argument 'items' should be type DataFrame, but is type str"):
        spy.archive(items='Not a DataFrame')  # type: ignore

    with pytest.raises(SPyValueError, match='The items DataFrame must contain an "ID" column.'):
        invalid_df = pd.DataFrame([{'Name': 'My Name'}])
        spy.archive(items=invalid_df)

    with pytest.raises(SPyValueError, match='ID "Not a GUID" is not a valid GUID'):
        invalid_df = pd.DataFrame([{'ID': 'Not a GUID'}])
        spy.archive(items=invalid_df)

    empty_df = pd.DataFrame(columns=['ID'])
    with pytest.raises(SPyTypeError, match="Argument 'note' should be type str, but is type bool"):
        spy.archive(empty_df, note=True)  # type: ignore

    with pytest.raises(SPyValueError, match="errors argument must be either 'raise' or 'catalog'"):
        spy.archive(empty_df, errors='Something else')

    with pytest.raises(SPyValueError, match="quiet argument must be either True or False"):
        spy.archive(empty_df, quiet='Not a bool')  # type: ignore

    with pytest.raises(SPyTypeError, match="Argument session must be of type Session"):
        spy.archive(empty_df, session='Not a Session')  # type: ignore

    with pytest.raises(SPyTypeError, match="Argument status must be of type Status"):
        spy.archive(empty_df, status='Not a Status')  # type: ignore


@pytest.mark.system
@patch("seeq.sdk.ItemsApi.archive_item")
def test_archive_note_default(mock_archive_item_call):
    # There's not currently a way to verify the note is actually added to the archive_events table.
    # Just verify the note is passed to the API.
    test_name = f'test_archive_note_default_{_common.new_placeholder_guid()}'
    non_admin_session = test_common.get_session(test_common.Sessions.nonadmin)
    items = create_items(test_name, user_session=non_admin_session)

    spy.archive(items.head(1), session=non_admin_session)

    _, kwargs = mock_archive_item_call.call_args
    assert kwargs['note'].startswith(f'Archived from SPy by {non_admin_session.user.username}')


@pytest.mark.system
@patch("seeq.sdk.ItemsApi.archive_item")
def test_archive_note_custom(mock_archive_item_call):
    # There's not currently a way to verify the note is actually added to the archive_events table.
    # Just verify the note is passed to the API.
    test_name = f'test_archive_note_custom_{_common.new_placeholder_guid()}'
    non_admin_session = test_common.get_session(test_common.Sessions.nonadmin)
    items = create_items(test_name, user_session=non_admin_session)

    spy.archive(items.head(1), session=non_admin_session, note='Custom note')

    _, kwargs = mock_archive_item_call.call_args
    assert kwargs['note'] == 'Custom note'


@pytest.mark.system
def test_archive_catalog_errors():
    admin_session = test_common.get_session(test_common.Sessions.admin)
    non_admin_session = test_common.get_session(test_common.Sessions.nonadmin)

    test_name = f'test_archive_catalog_errors_{_common.new_placeholder_guid()}'
    items = create_items(test_name, user_session=admin_session)
    spy.acl.push(items, acl=[], replace=True, disable_inheritance=True, session=admin_session)

    # The non-admin user should not have permission to the items so the request should 403.
    with pytest.raises(ApiException, match='does not have access'):
        spy.archive(items, errors='raise', session=non_admin_session)
    results = spy.archive(items, errors='catalog', session=non_admin_session)
    assert results['Result'].str.contains('does not have access').all()
    assert results.spy.status.code == Status.SUCCESS
    assert results.spy.status.df.at[0, 'Count'] == 4
    assert 'Successfully archived 0 of 4 items' in results.spy.status.message

    # The admin user can archive the items, but not the random UUID that's appended.
    items_with_extra = pd.concat([pd.DataFrame([{'ID': _common.new_placeholder_guid()}]), items],
                                 ignore_index=True).reset_index(drop=True)
    with pytest.raises(ApiException, match='Not Found'):
        spy.archive(items_with_extra, errors='raise', session=admin_session)
    results = spy.archive(items_with_extra, errors='catalog', session=admin_session)
    assert len(results[results['Result'].str.contains('Not Found')]) == 1
    assert len(results[results['Result'] == 'Success']) == 4
    assert results.spy.status.code == Status.SUCCESS
    assert results.spy.status.df.at[0, 'Count'] == 5
    assert 'Successfully archived 4 of 5 items' in results.spy.status.message


@pytest.mark.system
def test_unarchive():
    test_name = f'test_unarchive_{_common.new_placeholder_guid()}'
    items = create_items(test_name)

    # Archive the items first
    results = spy.archive(items)

    # noinspection PyTypeChecker
    assert all(results['Result'] == 'Success')

    # Now unarchive them
    unarchive_results = spy.archive(items, undo=True)

    assert len(unarchive_results) == 4

    # noinspection PyTypeChecker
    assert all(unarchive_results['Result'] == 'Success')
    assert unarchive_results.spy.status.df.at[0, 'Count'] == 4
    assert unarchive_results.spy.status.df.at[0, 'Time'] is not None
    assert unarchive_results.spy.status.code == Status.SUCCESS
    assert 'Successfully unarchived 4 of 4 items' in unarchive_results.spy.status.message

    # Verify the items are actually unarchived
    re_pull = spy.search(items, all_properties=True)
    assert not any(re_pull['Archived'])


# Used to manually test that parallelization is working as expected. Concurrent run times should be noticeably faster
# than running with only one worker.
@pytest.mark.performance
def test_archive_parallelization():
    non_admin_session = test_common.get_session_copy(test_common.Sessions.nonadmin)
    test_name = f'test_archive_parallelization_{_common.new_placeholder_guid()}'
    item_count = 10_000
    items = create_items(test_name, item_count=item_count, user_session=non_admin_session)

    tests_per_config = 5
    worker_configs = [8, 1]

    outputs = list()
    for worker_config in worker_configs:
        non_admin_session.options.max_concurrent_requests = worker_config
        print(f'Running {tests_per_config} tests with {worker_config} workers.')
        for _ in range(tests_per_config):
            results = spy.archive(items, session=non_admin_session)
            time = results.spy.status.df.at[0, 'Time']
            output = f'Archival with {worker_config} workers took {time}.'
            outputs.append(output)
            print(output)
    print('Test complete:')
    for output in outputs:
        print(output)


def create_items(test_name, item_count=None, user_session=None):
    metadata_df = pd.DataFrame([{
        'Type': 'Signal',
        'Name': f'{test_name}_signal',
        'Formula': 'sinusoid()'
    }, {
        'Type': 'Scalar',
        'Name': f'{test_name}_scalar',
        'Formula': '1'
    }, {
        'Type': 'Condition',
        'Name': f'{test_name}_condition',
        'Formula': 'days()'
    }, {
        'Type': 'Asset',
        'Name': f'{test_name}_asset'
    }])
    if item_count and item_count > 4:
        additional_items = pd.DataFrame([{
            'Type': 'Signal',
            'Name': f'{test_name}_signal_{i}',
            'Formula': 'sinusoid()'
        } for i in range(4, item_count)])
        metadata_df = pd.concat([metadata_df, additional_items], ignore_index=True)
    push_result = spy.push(metadata=metadata_df, workbook=test_name, session=user_session)
    # Drop the 'Push Result' column so it's not present for the archive test assertions
    return push_result.drop('Push Result', axis=1)
