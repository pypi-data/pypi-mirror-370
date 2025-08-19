import unittest

import pygambit


class TestGambitEfgFile(unittest.TestCase):
    def setUp(self):
        with open("contrib/games/e02.efg") as f:
            self.file_text = f.read()

    def tearDown(self):
        pass

    def test_parse_string_empty(self):
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game("")
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: Empty file or string provided"
        )

    def test_parse_string_no_newline_end(self):
        pygambit.Game.parse_game(
            'NFG 1 R "prisoners dilemma"\n {"Player 1" "Player 2"} {2 2}\n'
            ' -6 -6 -10 0 0 -10 -1 -1.0'
        )

    def test_parse_string_wrong_magic(self):
        ft = self.file_text.replace("EFG", "")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 1:3: Expecting file type"
        )

    def test_parse_string_wrong_version(self):
        ft = self.file_text.replace("EFG 2", "EFG 1")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 1:6: Accepting only EFG version 2"
        )

    def test_parse_string_wrong_precision(self):
        ft = self.file_text.replace("EFG 2 R", "EFG 2 X")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 1:9: "
            "Accepting only EFG R or D data type"
        )

    def test_parse_string_node_type(self):
        ft = self.file_text.replace('p "" 1 1', 'x "" 1 1')
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 4:3: Invalid type of node"
        )

    def test_parse_string_removed_player(self):
        ft = self.file_text.replace('"Player 2"', "")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 5:26: Expecting '}' after outcome"
        )

    def test_parse_string_extra_payoff(self):
        ft = self.file_text.replace("1, 1", "1, 2, 3")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 5:29: Expecting '}' after outcome"
        )

    def test_write_game_gte_sanity(self):
        g = pygambit.Game.parse_game(self.file_text)
        g.write("gte")


class TestGambitNfgFile(unittest.TestCase):
    def setUp(self):
        with open("contrib/games/e02.nfg") as f:
            self.file_text = f.read()

    def tearDown(self):
        pass

    def test_parse_string_removed_title(self):
        ft = self.file_text.replace(
            '"Selten (IJGT, 75), Figure 2, normal form"', ""
        )
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 1:11: Game title missing"
        )

    def test_parse_string_removed_player(self):
        ft = self.file_text.replace('"Player 2"', "")
        with self.assertRaises(ValueError) as e:
            pygambit.Game.parse_game(ft)
        self.assertEqual(
            str(e.exception),
            "Parse error in game file: line 1:73: "
            "Not enough players for number of strategy entries"
        )
