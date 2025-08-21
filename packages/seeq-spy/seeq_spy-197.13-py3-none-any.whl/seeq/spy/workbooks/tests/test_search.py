from unittest import mock

import pytest

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions
from seeq.spy.workbooks import Analysis
from seeq.spy.workbooks.tests import test_load


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_non_recursive():
    workbooks = test_load.load_example_export()
    spy.workbooks.push(workbooks, path='Non-Recursive Import', errors='catalog', label='test_non_recursive')
    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*'
    })
    assert len(workbooks_df) == 2, workbooks_df.to_string()
    assert workbooks_df.spy.status.df.at[0, 'Total Processed'] >= 2
    assert workbooks_df.spy.status.df.at[0, 'Total Returned'] == 2

    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*',
        'Name': '*Analysis'
    })
    assert len(workbooks_df) == 1, workbooks_df.to_string()
    assert workbooks_df.iloc[0]['Name'] == 'Example Analysis'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Analysis'

    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*',
        'Workbook Type': 'Topic'
    })
    assert len(workbooks_df) == 1, workbooks_df.to_string()
    assert workbooks_df.iloc[0]['Name'] == 'Example Topic'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Topic'


@pytest.mark.system
def test_recursive():
    workbooks = test_load.load_example_export()
    spy.workbooks.push(workbooks, path='Recursive Import >> Another Folder Level', errors='catalog',
                       label='test_recursive', refresh=False)
    workbooks_df = spy.workbooks.search({
        'Path': 'Recursive I?port'
    })
    assert len(workbooks_df) == 1, workbooks_df.to_string()
    assert workbooks_df.iloc[0]['Name'] == 'Another Folder Level'
    assert workbooks_df.iloc[0]['Type'] == 'Folder'

    workbooks_df = spy.workbooks.search({
        'Path': r'/Recursive\sImport/',
        'Name': '*Analysis'
    }, recursive=True)
    assert len(workbooks_df) == 1, workbooks_df.to_string()
    assert workbooks_df.iloc[0]['Name'] == 'Example Analysis'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Analysis'

    workbooks_df = spy.workbooks.search({
        'Path': r'/^Recursive.*/',
        'Workbook Type': 'Topic'
    }, recursive=True)
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Example Topic'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Topic'


@pytest.mark.system
def test_archived():
    path = f"test_archived_{_common.new_placeholder_guid()}"
    archived_workbook = spy.workbooks.Analysis({'Name': 'An Archived Workbook'})
    archived_workbook.worksheet('Only Worksheet')
    not_archived_workbook = spy.workbooks.Analysis({'Name': 'A Not Archived Workbook'})
    not_archived_workbook.worksheet('Only Worksheet')
    spy.workbooks.push([archived_workbook, not_archived_workbook], path=path)
    items_api = ItemsApi(spy.session.client)
    items_api.set_property(id=archived_workbook.id, property_name='Archived', body=PropertyInputV1(value=True))
    try:
        search_df = spy.workbooks.search({'Path': path}, include_archived=True)
        assert len(search_df) == 2, search_df.to_string()
        assert 'An Archived Workbook' in search_df['Name'].tolist()
        assert 'A Not Archived Workbook' in search_df['Name'].tolist()
        search_df = spy.workbooks.search({'Path': path}, include_archived=False)
        assert len(search_df) == 1, search_df.to_string()
        assert search_df.iloc[0]['Name'] == 'A Not Archived Workbook'
    finally:
        # Unarchive it so we can run this test over and over
        items_api.set_property(id=archived_workbook.id, property_name='Archived', body=PropertyInputV1(value=False))


@pytest.mark.system
def test_content_filters():
    workbook_name = f'test_sections_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')

    def _assert_location(_location, _session):
        # Asserts that workbook appears under a certain content_filter but not others

        for _content_filter in ['owner', 'public', 'shared', 'corporate']:
            _search_df = spy.workbooks.search(
                {'Name': workbook_name}, content_filter=_content_filter, recursive=False, session=_session)
            assert len(_search_df) == (1 if _location == _content_filter else 0), _search_df.to_string()

    # First push to Corporate drive
    spy.workbooks.push(workbook, path=spy.workbooks.CORPORATE)
    _assert_location('corporate', spy.session)

    # Now un-publish from Corporate drive back to user folder
    spy.workbooks.push(workbook, path=spy.PATH_ROOT)
    _assert_location('owner', spy.session)

    # Use admin to make sure it doesn't show up in any (non-ALL) searches
    admin_session = test_common.get_session(Sessions.admin)
    _assert_location('none', admin_session)

    # Make sure it shows up in ALL search
    search_df = spy.workbooks.search({'Name': workbook_name}, content_filter='all', recursive=False,
                                     session=admin_session)
    assert len(search_df) == 1, search_df.to_string()

    # Now share the workbook with the admin so it would appear under Shared on the Home Screen
    items_api = ItemsApi(admin_session.client)
    admin_user = test_common.get_user(admin_session, test_common.ADMIN_USER_NAME)
    acl_output = items_api.add_access_control_entry(
        id=workbook.id,
        body=AceInputV1(identity_id=admin_user.id,
                        permissions=PermissionsV1(read=True)))
    _assert_location('shared', admin_session)

    # Now un-share it with admin and share it with Everyone so it appears as Public
    for ace_id in [ace.id for ace in acl_output.entries if ace.identity.username == 'admin@seeq.com']:
        items_api.remove_access_control_entry(id=workbook.id, ace_id=ace_id)

    everyone_group = test_common.get_group(admin_session, 'Everyone')
    items_api.add_access_control_entry(
        id=workbook.id,
        body=AceInputV1(identity_id=everyone_group.id,
                        permissions=PermissionsV1(read=True)))
    _assert_location('public', admin_session)


@pytest.mark.system
def test_root_directories():
    workbook_name = f'test_root_directories_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')
    folders_to_test = [spy.workbooks.ALL, spy.workbooks.CORPORATE, spy.workbooks.MY_FOLDER, spy.workbooks.SHARED,
                       spy.workbooks.USERS]

    def _assert_root_dir(_location, _content_filter):
        # Asserts that when the path contains the root directory, the workbook is found in the correct root directory
        for _root_dir in folders_to_test:
            _search_df = spy.workbooks.search({'Name': workbook_name, 'Path': f'{_root_dir}'},
                                              recursive=False, content_filter=_content_filter)
            if _root_dir == spy.workbooks.ALL:
                expected_length = 1
            elif _location == _root_dir:
                expected_length = 1
            else:
                expected_length = 0

            assert len(_search_df) == expected_length, _search_df.to_string()

    # push to corporate, search with different root directories and matching and non-matching content_filters
    spy.workbooks.push(workbook, path=spy.workbooks.CORPORATE)
    _assert_root_dir(spy.workbooks.CORPORATE, 'corporate')
    _assert_root_dir(spy.workbooks.CORPORATE, 'owner')

    # push to user directory, search with different root directories and matching and non-matching content_filters
    spy.workbooks.push(workbook, path=spy.workbooks.MY_FOLDER)
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'owner')
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'public')
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'corporate')


@pytest.mark.system
def test_redacted_search_get_workbook():
    workbooks = test_load.load_example_export()
    path = f'Search Folder get_workbook {_common.new_placeholder_guid()}'
    push_results = spy.workbooks.push(workbooks, path=path, label=path, errors='catalog')
    workbook_id = push_results[push_results['Workbook Type'] == 'Analysis'].at[0, 'Pushed Workbook ID']

    reason = 'What workbook'
    mock_exception_thrower = mock.Mock(side_effect=ApiException(status=404, reason=reason))
    with mock.patch('seeq.sdk.WorkbooksApi.get_workbook', new=mock_exception_thrower):
        with pytest.raises(ApiException, match=reason):
            spy.workbooks.search({'ID': workbook_id})

        status = spy.Status(errors='catalog')
        workbooks_df = spy.workbooks.search({'ID': workbook_id}, status=status)
        assert len(workbooks_df) == 0, \
            f'No Workbook Search results should have been found when querying {workbook_id}: {workbooks_df.to_string()}'
        assert len(status.warnings) >= 1, f'No warnings found in status {status}'
        warning_matches = [w for w in status.warnings if reason in w]
        assert warning_matches, f'Expected warning "{reason}" not found in {status.warnings}'


@pytest.mark.system
def test_redacted_search_get_folder():
    workbooks = test_load.load_example_export()
    path = f'Search Folder get_folder {_common.new_placeholder_guid()}'
    spy.workbooks.push(workbooks, path=path, label=path, errors='catalog')

    reason = 'something'
    mock_exception_thrower = mock.Mock(side_effect=ApiException(status=500, reason=reason))
    with mock.patch('seeq.sdk.FoldersApi.get_folders', new=mock_exception_thrower):
        with pytest.raises(ApiException, match=reason):
            spy.workbooks.search({'Path': path})

        status = spy.Status(errors='catalog')
        workbooks_df = spy.workbooks.search({'Path': path}, status=status)
        assert len(workbooks_df) == 0, \
            f'No Workbook Search results should have been found when querying {path}: {workbooks_df.to_string()}'
        assert len(status.warnings) >= 1, f'No warnings found in status {status}'
        expected_warning = 'Failed to get Folders using filter OWNER because an internal server error occurred'
        warning_matches = [w for w in status.warnings if expected_warning in w]
        assert warning_matches, f'Expected warning "{expected_warning}" not found in {status.warnings}'


@pytest.mark.system
def test_vantage():
    if not spy.utils.is_server_version_at_least(66, 30, 1):
        pytest.skip('Server version does not support /folders returning Vantage rooms by default')

    test_name = f'test_vantage_{_common.new_placeholder_guid()}'
    workbooks_api = WorkbooksApi(spy.session.client)
    workbooks_output = workbooks_api.create_workbook(
        body=WorkbookInputV1(name=test_name, type='Vantage')
    )
    workbook_id = workbooks_output.id
    assert workbook_id is not None

    try:
        search_df = spy.workbooks.search({'Name': test_name})
        assert len(search_df) == 1

        search_df_with_type = spy.workbooks.search({'Name': test_name, 'Workbook Type': 'Vantage'})
        assert len(search_df_with_type) == 1
    finally:
        workbooks_api.archive_workbook(id=workbook_id)
