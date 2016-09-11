import unittest
import bibcompat

class TestBibCompat(unittest.TestCase):
    def test_convert(self):
        data = '1313823606.10,start all\n' \
        '1313824970.11,3131\n' \
        '1313825001.12,3031\n' \
        '1313825043.13,3201\n' \
        '1313825083.14,3083\n'
        with open('testlog.csv', 'w') as f:
            f.write(data)

        bw = bibcompat.BibWriter('testlog.csv', '.')
        bw.update()

        del bw

        with open('bibtime.txt',  'r') as f:
            self.assertEqual("1313823606\tall\n", f.readline())
            self.assertEqual("1313824970\t3131\n", f.readline())
