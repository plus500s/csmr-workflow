from django.test import TestCase
from unittest import mock

from workflow.utils import CheckFileHash

ITEMS_FILE_HASH = 'be7e1b8b667cf6efbd702b3e691015aa44065d11a3d8a104372c4e33e4729843'
WORKFLOWS_FILE_HASH = 'd63b73ad14d754dc446fd83446049ac86762fad8c21071c90a0ceef2fc7f780d'
PREVIOUS_DIFFERENT_HASH = 'previous_different_hash'

FILE_HASHES = {
    'items_file': '.items_hash',
    'workflows_file': '.workflows_hash',
}
FILE_PATHS = {
    'items_file': 'tests/test_files/items.csv',
    'workflows_file': 'tests/test_files/workflow_updates.json',
}


class TestCheckFileHash(TestCase):
    CheckFileHash.FILE_HASHES = FILE_HASHES
    CheckFileHash.FILE_PATHS = FILE_PATHS

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_create_hash(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        items_test_hash = check_file_hash._create_hash(FILE_PATHS.get('items_file'))
        workflows_test_hash = check_file_hash._create_hash(FILE_PATHS.get('workflows_file'))
        self.assertEqual(items_test_hash, ITEMS_FILE_HASH)
        self.assertEqual(workflows_test_hash, WORKFLOWS_FILE_HASH)

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_check_hash_without_previous_file(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        items_test_check = check_file_hash.check_hash('items_file')
        workflows_test_check = check_file_hash.check_hash('workflows_file')
        self.assertEqual(items_test_check, True)
        self.assertEqual(workflows_test_check, True)

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_check_hash_workflows_with_previous_hash(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        setattr(check_file_hash, 'workflows_file', WORKFLOWS_FILE_HASH)

        workflows_test_check = check_file_hash.check_hash('workflows_file')
        self.assertEqual(workflows_test_check, False)

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_check_hash_items_with_previous_hash(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        setattr(check_file_hash, 'items_file', ITEMS_FILE_HASH)
        items_test_check = check_file_hash.check_hash('items_file')
        self.assertEqual(items_test_check, False)

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_check_hash_workflows_with_previous_different_hash(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        setattr(check_file_hash, 'workflows_file', PREVIOUS_DIFFERENT_HASH)

        workflows_test_check = check_file_hash.check_hash('workflows_file')
        self.assertEqual(workflows_test_check, True)

    @mock.patch.object(CheckFileHash, '_create_file')
    def test_check_hash_items_with_previous_different_hash(self, mocked_created_file):
        check_file_hash = CheckFileHash()
        setattr(check_file_hash, 'items_file', PREVIOUS_DIFFERENT_HASH)
        items_test_check = check_file_hash.check_hash('items_file')
        self.assertEqual(items_test_check, True)
