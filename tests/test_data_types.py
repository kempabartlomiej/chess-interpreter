
import unittest

import questionable_import
import move
from data_types import Board, mask_from_list

# class TestDataTypes(unittest.TestCase):

	# def test_board_from_list(self):
	# 	pass
		



if __name__ == '__main__':
	# unittest.main()
	print(Board([
		'rnbqkbnr',
		'pppppppp',
		'________',
		'________',
		'________',
		'________',
		'PPPPPPPP',
		'RNBQKBNR',
	]))

	print(mask_from_list([
		"________",
		"________",
		"___.____",
		"________",
		"_____-__",
		"_____x__",
		"________",
		"________",
	]))