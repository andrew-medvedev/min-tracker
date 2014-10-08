__date__ = '08.10.2014'
__author__ = {
    'name': 'a.medvedev'
}

import unittest
import utils


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_chlat_dot_etc(self):
        self.assertTrue(utils.chlat_dot_etc('abc'))

        self.assertTrue(utils.chlat_dot_etc('abc.cba'))

        self.assertTrue(utils.chlat_dot_etc('abc.cba_FFFF'))

        self.assertFalse(utils.chlat_dot_etc('abc.cba_FFFF1'))

        self.assertFalse(utils.chlat_dot_etc('abc-abc-123'))

        self.assertFalse(utils.chlat_dot_etc('守破離'))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(UnitTestCase())
    return suite


if __name__ == '__main__':
    unittest.main()