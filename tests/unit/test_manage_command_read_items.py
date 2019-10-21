from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from workflow.models import Item


class ReadItemsFromCsvTest(TestCase):
    def test_created_all_items_from_file(self):
        Item.objects.create(url='preexisting_url1')
        self.assertEqual(Item.objects.all().count(), 1)
        call_command('read_items_from_csv', 'tests/test_files/items.csv')
        self.assertTrue(Item.objects.get(url='preexisting_url1'))
        self.assertTrue(Item.objects.get(url='http://googlefromfile1.com'))
        self.assertTrue(Item.objects.get(url='http://googlefromfile2.com'))
        self.assertTrue(Item.objects.get(url='http://googlefromfile3.com'))
        self.assertEqual(Item.objects.all().count(), 4)


class ReadItemsFromUnExistedCsvTest(TestCase):
    def test_unexisted_file(self):
        self.assertEqual(Item.objects.all().count(), 0)
        with self.assertRaises(CommandError):
            call_command('read_items_from_csv', 'tests/test_files/unexisted_file.csv')
        self.assertEqual(Item.objects.all().count(), 0)


class RepeatingReadingItemsFromCsvTest(TestCase):
    def test_created_all_items_from_file(self):
        self.assertEqual(Item.objects.all().count(), 0)
        call_command('read_items_from_csv', 'tests/test_files/items.csv')
        self.assertEqual(Item.objects.all().count(), 3)
        call_command('read_items_from_csv', 'tests/test_files/items.csv')
        self.assertTrue(Item.objects.get(url='http://googlefromfile1.com'))
        self.assertTrue(Item.objects.get(url='http://googlefromfile2.com'))
        self.assertTrue(Item.objects.get(url='http://googlefromfile3.com'))
        self.assertEqual(Item.objects.all().count(), 3)
