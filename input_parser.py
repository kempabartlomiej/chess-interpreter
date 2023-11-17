from data_types import Piece, Board, Mask, Position, Meta, MetaTag

import move
from move import MoveSteps

from typing import Optional


def separate_from_meta(user_input: str, *, ignore_hyphens=False) -> tuple[str, list[MetaTag]]:
	# returns (stripped_user_input: str, meta: list)

	INFIXES: dict = {
		Meta.TAG_CAPTURE: (":", "x",),
	}
	if not ignore_hyphens:
		INFIXES[Meta.TAG_MOVE] = ("-",)

	SUFFIXES: dict = {
		# ordering matters, when it comes to iterating over this dict
		Meta.TAG_CHECKMATE: ("#", "mate", "++", "X", "x",), # "++" can also mean doubble check, but the program doesn't check for those
		Meta.TAG_CHECK: ("+", "ch",), # is always the last suffix, when in tandem with pawn promotion or en passant
		Meta.TAG_PAWN_PROMOTION: ("=Q", "(Q)", "/Q", "Q",),
		Meta.TAG_EN_PASSANT: ("e.p.", "(e.p.)",),
	}

	meta = []

	for key, value in SUFFIXES.items():
		for suffix in value:
			if user_input.endswith(suffix):
				meta.append(key)
				user_input = user_input.removesuffix(suffix)
				user_input = user_input.strip()
				break
	
	for key, value in INFIXES.items():
		for symbol in value:
			if symbol in user_input:
				meta.append(key)
				user_input = user_input.replace(symbol, '', 1)

	user_input = user_input.strip()

	return (user_input, meta)


def verify_meta(board: Board, is_white: bool, completed_input: MoveSteps, meta: list[MetaTag]) -> Optional[Exception]:

	assert tuple(filter(
		lambda tag: not tag in [Meta.TAG_CAPTURE, Meta.TAG_MOVE, Meta.TAG_EN_PASSANT, Meta.TAG_PAWN_PROMOTION, Meta.TAG_CHECK, Meta.TAG_CHECKMATE], meta)
	) == (), "Invalid meta tag"

	# WARNING: it only checks one piece's movement (the rook if it's castling)
	x, y, x2, y2 = completed_input[-1]

	destination_piece_type = board.fields[x2][y2].type

	if Meta.TAG_CAPTURE in meta and destination_piece_type == Piece.TYPE_NONE:
		if not move.create_piece_mask(board, x, y).fields[x2][y2] & Mask.FLAG_EN_PASSANT:
			return Exception("Not a capture")
	
	# if Meta.TAG_MOVE in meta and destination_piece_type != Piece.TYPE_NONE:
	# 	return Exception("Not a move ()")

	if Meta.TAG_EN_PASSANT in meta and not move.create_piece_mask(board, x, y, False).fields[x2][y2] & Mask.FLAG_EN_PASSANT:
		return Exception("Not an en passant")

	if Meta.TAG_PAWN_PROMOTION in meta:
		promotion_y = 0 if is_white else (Board.SIZE - 1)
		if promotion_y != y2:
			return Exception("Not a pawn promotion")
	
	if Meta.TAG_CHECK in meta and not move.would_result_in(board, is_white, completed_input, Meta.TAG_CHECK):
		return Exception(f"Not a check")

	if Meta.TAG_CHECKMATE in meta and not move.would_result_in(board, is_white, completed_input, Meta.TAG_CHECKMATE):
		return Exception("Not a checkmate")

	return None


ParsedInput = tuple[int, (int | None), (int | None), int, int]

def parse_simple_move(user_input: str) -> ParsedInput | Exception:

	if len(user_input) > 5:
		return Exception(f"Wrong input (too many symbols or a typo {user_input})")
	
	piece_type = None
	x = None
	y = None
	x2 = None
	y2 = None

	# Ka1-b2 - example (user_intput SHOULDN'T contain '-' at this point, it's only there for visualisation)

	# K__-__
	if user_input[0].isupper():
		if user_input[0].lower() in Piece.get_valid_piece_chars():
			piece_type = Piece.CHAR_TO_TYPE[user_input[0].lower()]
			user_input = user_input[1:]
		else:
			return Exception(f"Wrong input (invalid piece symbol \"{user_input[0]}\")")
	else:
		piece_type = Piece.TYPE_PAWN
	
	# ___-_2
	if user_input[-1] in Board.RANK_SYMBOLS:
		# y2 = rank_to_y(user_input[-1])
		y2 = Board.rank_to_y(user_input[-1])
		user_input = user_input[:-1]
	else:
		return Exception(f"Wrong input (invalid destination rank label \"{user_input[-1]}\")")

	if not user_input:
		RuntimeError(f"Wrong input (no destination file)")

	# ___-b_
	if user_input[-1] in Board.FILE_SYMBOLS:
		# x2 = file_to_x(user_input[-1])
		x2 = Board.file_to_x(user_input[-1])
		user_input = user_input[:-1]
	else:
		return Exception(f"Wrong input (invalid destination file label \"{user_input[-1]}\")")
	
	# _a_-__
	if user_input and user_input[0] in Board.FILE_SYMBOLS:
		x = Board.file_to_x(user_input[0])
		user_input = user_input[1:]
	
	# __1-__
	if user_input:
		if user_input[0] in Board.RANK_SYMBOLS:
			y = Board.rank_to_y(user_input[0])
			user_input = user_input[1:]
		else:
			return Exception(f"Wrong input (invalid departure file label \"{user_input[0]}\")")

	return (piece_type, x, y, x2, y2)


def complete_simple_move(board: Board, is_white: bool, parsed_input: ParsedInput) -> MoveSteps | Exception:
	
	piece_type, x, y, x2, y2 = parsed_input

	positions = board.get_pieces_positions(piece_type, is_white)

	if x is not None:
		positions = filter(lambda position: position[0] == x, positions)

	if y is not None:
		positions = filter(lambda position: position[1] == y, positions)
	
	def is_move_valid(data: Position) -> bool:
		"Checks if move x, y -> x2, y2 is valid"

		assert len(data) == 2

		xx, yy = data

		mask = move.create_piece_mask(board, xx, yy)

		return mask.fields[x2][y2] != Mask.FLAG_NONE

	positions = tuple(filter(is_move_valid, positions))

	possibilities = len(positions)
	
	if possibilities == 0:
		return Exception('Move is not possible')
	elif possibilities > 1:
		return Exception(f'Move is ambiguous ({possibilities} pieces can perform it)')
	else:

		x, y = positions[0]

		completed_input = [(x, y, x2, y2), ]

		if move.would_result_in(board, not is_white, completed_input, Meta.TAG_CHECK):
			return Exception("Move is not possible due to a check")
		
		if board.fields[x2][y2].type == Piece.TYPE_KING:
			# it should not be possible to get this error message
			return Exception("The king cannot be captured")

		return completed_input


def complete_castling(board: Board, is_white: bool, is_kingside: bool) -> MoveSteps | Exception:

	attack_color = not is_white

	king_x, king_y = board.get_pieces_positions(Piece.TYPE_KING, is_white)[0]

	# 0. check if king was moved
	if board.was_piece_moved(king_x, king_y):
		return Exception(f'Castling impossible - king ({board.parse_position(king_x, king_y)}) was moved')

	dist = 3 if is_kingside else -4

	def f(data: Position) -> bool:
		x, y = data
		return board.fields[x][y].type == Piece.TYPE_ROOK \
		and board.fields[x][y].is_white == is_white and (x - king_x) == dist \

	rooks = tuple(filter(f, board.get_all_pieces_positions()))
	
	if len(rooks) == 0:
		return Exception("Castling impossible - no rook found")
	elif len(rooks) == 2:
		# one rook was moved and both are the equal distance away from the king
		rooks = tuple(filter(lambda data: board.was_piece_moved(data[0], data[1]), rooks))
	
	rook_x, rook_y = rooks[0]

	direction = int((rook_x - king_x) / abs(rook_x - king_x)) # sign

	# 1. check if rook was moved
	if board.was_piece_moved(rook_x, rook_y):
		return Exception(f'Castling impossible - rook ({board.parse_position(rook_x, rook_y)}) was moved')
	# 2. check if the king is in check
	elif move.is_position_attacked(board, king_x, king_y, attack_color):
		return Exception(f'Castling impossible - king ({board.parse_position(king_x, king_y)}) is under attack')
	
	# 3. checking if the squares between the king and the rook are:
	for i in range(1, 3):
		# a. empty
		if not board.is_position_empty(king_x+direction*i, king_y):
			return Exception(f'Castling impossible - field {board.parse_position(king_x+direction*i, king_y)} is not empty')
		# b. not attacked
		elif move.is_position_attacked(board, king_x+direction*i, king_y, attack_color):
			return Exception(f'Castling impossible - field {board.parse_position(king_x+direction*i, king_y)} under attack')

	return [
		(king_x, king_y, king_x+direction*2, king_y),
		(rook_x, rook_y, king_x+direction*1, rook_y),
	]


def parse_and_complete(board: Board, is_white: bool, user_input: str) -> MoveSteps | Exception:
	
	if user_input[:3] in ('0-0', 'O-O'):

		result = separate_from_meta(user_input, ignore_hyphens=True)
		if isinstance(result, Exception): return result

		user_input, meta = result 
		
		if not user_input in ('0-0', 'O-O', '0-0-0', 'O-O-O'):
			return Exception('Invalid move')

		is_kingside = user_input in ('0-0', 'O-O')

		completed_input = complete_castling(board, is_white, is_kingside)
		if isinstance(completed_input, Exception): return completed_input

		v = verify_meta(board, is_white, completed_input, meta)
		if isinstance(v, Exception): return v

		return completed_input
	
	else:
		result = separate_from_meta(user_input)
		if isinstance(result, Exception): return result

		user_input, meta = result 

		parsed_input = parse_simple_move(user_input)
		if isinstance(parsed_input, Exception): return parsed_input

		completed_input = complete_simple_move(board, is_white, parsed_input)
		if isinstance(completed_input, Exception): return completed_input

		v = verify_meta(board, is_white, completed_input, meta)
		if isinstance(v, Exception): return v

		return completed_input