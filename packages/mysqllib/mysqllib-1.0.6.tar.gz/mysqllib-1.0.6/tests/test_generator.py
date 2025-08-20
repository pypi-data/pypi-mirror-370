import unittest
from mysqllib.generator import condition_generator

class TestGenerator(unittest.TestCase):
    def test_generator(self):
        string, values = condition_generator({})
        self.assertEqual(string, '')
        self.assertEqual(values, [])
        string, values = condition_generator({'a': 'b', 'c': 'd', 'e': ['IN', ('a', 'b', 'c')]})
        self.assertEqual(string, 'a = %s AND c = %s AND e IN %s')
        self.assertEqual(values, ['b', 'd', ('a', 'b', 'c')])
        string, values = condition_generator({'a': 'b', 'c': ['>', 12]})
        self.assertEqual(string, 'a = %s AND c > %s')
        self.assertEqual(values, ['b', 12])
        string, values = condition_generator({
            'a': 'b',
            'OR': {
                'b': ['=', 'c'],
                'c': ['=', 'd']
            }
        })
        self.assertEqual(string, 'a = %s AND (b = %s OR c = %s)')
        self.assertEqual(values, ['b', 'c', 'd'])
        string, values = condition_generator({
            'a': 'b',
            'OR': [
                {'b': ['=', 'c']},
                {'c': ['=', 'd']},
                {'OR': [
                    {'e': ['>', 5]},
                    {'f': ['<', 10]}
                ]}
            ]
        })
        self.assertEqual(string, 'a = %s AND ((b = %s) OR (c = %s) OR (((e > %s) OR (f < %s))))')
        self.assertEqual(values, ['b', 'c', 'd', 5, 10])
        string, values = condition_generator([
            {
                'OR': [
                    {'a': 'b'},
                    {'a': 'c'}
                ],
                'b': 'c'
            },
            {
                'OR': [
                    {'a': 'd'},
                    {'a': 'e'}
                ],
                'b': 'd'
            }
        ])
        self.assertEqual(string, '(((a = %s) OR (a = %s)) AND b = %s) OR (((a = %s) OR (a = %s)) AND b = %s)')
        self.assertEqual(values, ['b', 'c', 'c', 'd', 'e', 'd'])
