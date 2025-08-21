import unittest

from mb_cruise_migration.framework.paginator import Paginator


class TestPaginator(unittest.TestCase):
    def test_likely_pagination(self):

        paginator = Paginator(pagesize=10, table_size=99)

        skip, limit = paginator.paginate()
        self.assertEqual(0, skip)
        self.assertEqual(10, limit)

        skip, limit = paginator.paginate()
        self.assertEqual(10, skip)
        self.assertEqual(10, limit)

        paginator.paginate()
        paginator.paginate()
        paginator.paginate()
        paginator.paginate()
        paginator.paginate()
        paginator.paginate()
        paginator.paginate()
        skip, limit = paginator.paginate()
        self.assertEqual(90, skip)
        self.assertEqual(9, limit)

        self.assertTrue(paginator.done())
        self.assertRaises(StopIteration, paginator.paginate)

    def test_edge_case_pagination(self):

        paginator = Paginator(pagesize=10, table_size=4)

        skip, limit = paginator.paginate()
        self.assertEqual(0, skip)
        self.assertEqual(4, limit)

        self.assertTrue(paginator.done())
        self.assertRaises(StopIteration, paginator.paginate)


if __name__ == '__main__':
    unittest.main()
