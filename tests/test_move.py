
import unittest

import questionable_import
import move
from data_types import Board, mask_from_list

class TestMove(unittest.TestCase):

	# def setUp(self):
	# 	self.board_1 = board_from_file('tests/data/test_board.txt')
	# 	self.mask_1 = Mask()

	def test_create_piece_mask(self):
		board_q = Board([
			'________',
			'____n___',
			'________',
			'____Q___',
			'___K____',
			'__q_____',
			'________',
			'________',
		])

		mask_q = mask_from_list([
			'_-_____-',
			'__-_x_-_',
			'___---__',
			'----_---',
			'____--__',
			'____-_-_',
			'____-__-',
			'____-___',
		])

		self.assertEqual(move.create_piece_mask(board_q, 4, 3).fields, mask_q.fields)

		board_k = Board([
			'________',
			'_k______',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		mask_k = mask_from_list([
			'---_____',
			'-_-_____',
			'---_____',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.create_piece_mask(board_k, 1, 1).fields, mask_k.fields)


		board_n = Board([
			'________',
			'________',
			'________',
			'___pnP__',
			'___pPP__',
			'___P_p__',
			'________',
			'________',
		])

		mask_n = mask_from_list([
			'________',
			'___-_-__',
			'__-___-_',
			'________',
			'__-___-_',
			'___x____',
			'________',
			'________',
		])


		self.assertEqual(move.create_piece_mask(board_n, 4, 3).fields, mask_n.fields)

		board_p = Board([
			'________',
			'_p______',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		mask_p1 = mask_from_list([
			'________',
			'________',
			'_.______',
			'_.______',
			'________',
			'________',
			'________',
			'________',
		])

		mask_p2 = mask_from_list([
			'________',
			'________',
			'x.x_____',
			'_.______',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.create_piece_mask(board_p, 1, 1).fields, mask_p1.fields)
		self.assertEqual(move.create_piece_mask(board_p, 1, 1, False).fields, mask_p2.fields)


	def test_get_attackers_positions(self):
		board = Board([
			'k___R___',
			'_P______',
			'_N______',
			'________',
			'________',
			'________',
			'R_______',
			'________',
		])

		self.assertEqual(
			move.get_attackers_positions(board, 0, 0, True),
			((0, 6), (1, 1), (1, 2), (4, 0))
		)


	def test_is_checkmate(self):
		board = Board([
			'________',
			'_k______',
			'________',
			'________',
			'________',
			'________',
			'______K_',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)

		board = Board([
			'k_______',
			'_Q______',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)

		board = Board([
			'k__R____',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)

		board = Board([
			'k__R____',
			'_Q______',
			'R_______',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)

		board = Board([
			'k_______',
			'_Q______',
			'__K_____',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), True)

		board = Board([
			'k____R__',
			'ppp_____',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), True)

		board = Board([
			'k____R__',
			'ppp_____',
			'_____r__',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)

		board = Board([
			'k____R__',
			'ppp_____',
			'____r___',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), False)


		board = Board([
			'k____R__',
			'_pp_____',
			'_____r__',
			'________',
			'R_______',
			'________',
			'________',
			'________',
		])

		self.assertEqual(move.is_checkmate(board, False), True)


	def test_is_position_attacked(self):
		board = Board([
			'K______R',
			'______q_',
			'________',
			'________',
			'________',
			'________',
			'________',
			'________',
		])

		results = [
			move.is_position_attacked(board, 0, 0, True),
			move.is_position_attacked(board, 1, 0, True),
			move.is_position_attacked(board, 7, 7, True),
			move.is_position_attacked(board, 7, 0, False),
		]

		answers = [
			False,
			True,
			True,
			True,
		]

		self.assertEqual(results, answers)

	def test_try_promoting_pawn(self):
		board = Board([
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
		])

		answer = Board([
			'ppppQQQQ', 
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'ppppPPPP',
			'qqqqPPPP', # p -> q
		])

		for x in range(8):
			for y in range(8):
				move.try_promoting_pawn(board, x, y)
				self.assertEqual(board.fields[x][y].type, answer.fields[x][y].type)
				self.assertEqual(board.fields[x][y].is_white, answer.fields[x][y].is_white)
		


if __name__ == '__main__':
	unittest.main()
	# t = TestMove()
	# t.test_get_attackers_positions()