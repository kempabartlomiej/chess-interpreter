



import questionable_import

import unittest
import input_parser
from data_types import Piece, Board



class TestInputParser(unittest.TestCase):

	def setUp(self):
		self.board_1 = Board()

	# def test_x_conversion(self):
	# 	data = (
	# 		(0, 'a'),
	# 		(3, 'd'),
	# 		(7, 'h'),
	# 	)
	# 	for x, char in data:
	# 		self.assertEqual(input_parser.x_to_file(x), char)
	# 		self.assertEqual(input_parser.file_to_x(char), x)

	# def test_y_conversion(self):
	# 	data = (
	# 		(0, '8'),
	# 		(3, '5'),
	# 		(7, '1'),
	# 	)
	# 	for y, decimal in data:
	# 		self.assertEqual(input_parser.y_to_rank(y), decimal)
	# 		self.assertEqual(input_parser.rank_to_y(decimal), y)
	
	def test_parse_simple_move(self):
		# it fails bc y is 8 - y now
		self.assertEqual(input_parser.parse_simple_move('a3'), (Piece.TYPE_PAWN, None, None, 0, 7-2))
		self.assertEqual(input_parser.parse_simple_move('Ka3'), (Piece.TYPE_KING, None, None, 0, 7-2))
		self.assertEqual(input_parser.parse_simple_move('Kb4a3'), (Piece.TYPE_KING, 1, 7-3, 0, 7-2))
		self.assertEqual(input_parser.parse_simple_move('K4a3'), (Piece.TYPE_KING, None, 7-3, 0, 7-2))
		self.assertEqual(input_parser.parse_simple_move('Kba3'), (Piece.TYPE_KING, 1, None, 0, 7-2))
		self.assertEqual(input_parser.parse_simple_move('Kb4a3'), (Piece.TYPE_KING, 1, 7-3, 0, 7-2))

	# def test_parse_castling(self):

	# 	self.assertEqual(input_parser.parse_castling('0-0'), (True,))
	# 	self.assertEqual(input_parser.parse_castling('0-0-0'), (False,))
	# 	self.assertEqual(input_parser.parse_castling('O-O'), (True,))
	# 	self.assertEqual(input_parser.parse_castling('O-O-O'), (False,))

	# def test_parse(self):
		
	# 	self.assertEqual(input_parser.parse('a3'), (Piece.TYPE_PAWN, None, None, 0, 2))
	# 	self.assertEqual(input_parser.parse('Ka3'), (Piece.TYPE_KING, None, None, 0, 2))
	# 	self.assertEqual(input_parser.parse('Kb4a3'), (Piece.TYPE_KING, 1, 3, 0, 2))
	# 	self.assertEqual(input_parser.parse('K4a3'), (Piece.TYPE_KING, None, 3, 0, 2))
	# 	self.assertEqual(input_parser.parse('Kba3'), (Piece.TYPE_KING, 1, None, 0, 2))
	# 	self.assertEqual(input_parser.parse('Kb4xa3'), (Piece.TYPE_KING, 1, 3, 0, 2))
	# 	self.assertEqual(input_parser.parse('0-0'), (True,))
	# 	self.assertEqual(input_parser.parse('0-0-0'), (False,))
	# 	self.assertEqual(input_parser.parse('O-O'), (True,))
	# 	self.assertEqual(input_parser.parse('O-O-O'), (False,))

	def test_complete_simple_move(self):
		print("TEST SIMPLE MOVE")

		
		self.assertEqual(
			str(input_parser.complete_simple_move(self.board_1, False, input_parser.parse_simple_move('a4'))),
			"Move is not possible"
		)
		
	# def test_complete_castling(self):
	# 	print("TEST CASTLING")
	# 	a = None
	# 	try:
	# 		a =	input_parser.complete_castling(self.board_1, False, False)
	# 		print(a)
	# 	except ValueError:
	# 		print(f'ERRRORRR: {e}')


if __name__ == '__main__':
	unittest.main()