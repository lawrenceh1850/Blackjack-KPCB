import unittest
from blackjack.blackjackgame import BlackjackGame
from gamepieces.card import Card


class TestStringMethods(unittest.TestCase):
    def test_hand_val(self):
        bj_game = BlackjackGame(1, 4, 2, 500, 500)
        self.assertEqual(max(bj_game._calc_hand_value([Card(1, 2)])), 11)
        self.assertEqual(min(bj_game._calc_hand_value([Card(1, 2)])), 1)

        self.assertEqual(
            min(bj_game._calc_hand_value([Card(1, 2), Card(2, 1)])), 3)
        self.assertEqual(
            max(bj_game._calc_hand_value([Card(1, 2), Card(2, 1)])), 13)

        self.assertEqual(
            max(bj_game._calc_hand_value([Card(13, 2), Card(1, 1)])), 21)
        self.assertEqual(
            max(bj_game._calc_hand_value([Card(13, 2), Card(12, 1)])), 20)
        self.assertEqual(
            max(bj_game._calc_hand_value([Card(13, 2), Card(5, 1)])), 15)

    def test_split_hand(self):
        bj_game = BlackjackGame(1, 4, 2, 500, 500)
        self.assertTrue(bj_game._is_split_hand([Card(1, 2), Card(1, 2)]))
        self.assertTrue(bj_game._is_split_hand([Card(1, 2), Card(1, 3)]))
        self.assertTrue(bj_game._is_split_hand([Card(10, 1), Card(10, 2)]))
        self.assertFalse(bj_game._is_split_hand([Card(1, 2), Card(11, 2)]))
        self.assertFalse(bj_game._is_split_hand([Card(12, 1), Card(11, 2)]))
        self.assertFalse(bj_game._is_split_hand(
            [Card(11, 1), Card(11, 2), Card(11, 2)]))
        self.assertFalse(bj_game._is_split_hand(
            [Card(11, 2), Card(11, 2), Card(11, 2)]))

    def test_double_hand(self):
        bj_game = BlackjackGame(1, 4, 2, 500, 500)
        self.assertTrue(bj_game._is_double_hand([Card(1, 2), Card(8, 2)]))
        self.assertTrue(bj_game._is_double_hand([Card(1, 2), Card(8, 2)]))
        self.assertTrue(bj_game._is_double_hand([Card(2, 2), Card(7, 2)]))
        self.assertTrue(bj_game._is_double_hand([Card(5, 2), Card(5, 2)]))
        self.assertTrue(bj_game._is_double_hand([Card(1, 2), Card(10, 2)]))

        self.assertFalse(bj_game._is_double_hand([Card(1, 2), Card(1, 2)]))
        self.assertFalse(bj_game._is_double_hand([Card(3, 2), Card(9, 2)]))
        self.assertFalse(bj_game._is_double_hand([Card(2, 2), Card(5, 2)]))


if __name__ == '__main__':
    unittest.main()
