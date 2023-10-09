from data_types import Piece, Board, Mask, Position, Meta, MetaTag
from copy import copy


def test_line(board: Board, mask: Mask, x: int, y: int, dx: int, dy: int, length: int) -> None:
	"Mutates the mask, flags its fields for capture, move and en passant in a line from (x, y) in the direction of (x+dx, y+dy)."
	
	assert x in range(0, board.SIZE)
	assert y in range(0, board.SIZE)
	assert dx in (-1, 0, 1)
	assert dy in (-1, 0, 1)
	assert length <= 7

	is_white = board.fields[x][y].is_white

	length_x: int
	length_y: int

	match dx:
		case -1:
			length_x = x
		case 0:
			length_x = length
		case 1:
			length_x = board.SIZE - 1 - x
	
	match dy:
		case -1:
			length_y = y
		case 0:
			length_y = length
		case 1:
			length_y = board.SIZE - 1 - y


	for _ in range(min(length, length_x, length_y)):
		x += dx
		y += dy
		
		assert y in range(0, board.SIZE), "There is an error in this function"
		assert x in range(0, board.SIZE), "There is an error in this function"
		
		if board.is_position_empty(x, y):
			mask.fields[x][y] = Mask.FLAG_MOVE | Mask.FLAG_CAPTURE
		else:
			if board.is_position_enemy(x, y, is_white):
				mask.fields[x][y] = Mask.FLAG_CAPTURE
			break


def test_diagonals(board: Board, mask: Mask, x: int, y: int, length: int) -> None:
	test_line(board, mask, x, y, -1, -1, length)
	test_line(board, mask, x, y, -1, 1, length)
	test_line(board, mask, x, y, 1, -1, length)
	test_line(board, mask, x, y, 1, 1, length)


def test_perpendiculars(board: Board, mask: Mask, x: int, y: int, length: int) -> None:
	test_line(board, mask, x, y, -1, 0, length)
	test_line(board, mask, x, y, 1, 0, length)
	test_line(board, mask, x, y, 0, -1, length)
	test_line(board, mask, x, y, 0, 1, length)


def test_knight(board: Board, mask: Mask, x: int, y: int) -> None:

	assert x in range(0, board.SIZE)
	assert y in range(0, board.SIZE)

	is_white = board.fields[x][y].is_white
	
	# possible moves relative to knight's position
	xy = (
		(-2, -1), (-2, 1),
		(-1, -2), (1, -2),
		(2, -1), (2, 1),
		(1, 2), (-1, 2),
	)

	for p in xy:
		x2 = p[0] + x
		y2 = p[1] + y
		if board.is_position_valid(x2, y2):
			if board.is_position_empty(x2, y2):
				mask.fields[x2][y2] = Mask.FLAG_MOVE | Mask.FLAG_CAPTURE
			elif board.is_position_enemy(x2, y2, is_white):
				mask.fields[x2][y2] = Mask.FLAG_CAPTURE


def test_pawn(board: Board, mask: Mask, x: int, y: int) -> None:
	# WARNING: empty fields might have Mask.FLAG_CAPTURE
	# use test_pawn_cleanup to remove them

	assert x in range(0, board.SIZE)
	assert y in range(0, board.SIZE)
	
	is_white = board.fields[x][y].is_white
	
	xy = ()

	direction = -1 if is_white else 1

	# possible moves relative to pawn's position
	if board.was_piece_moved(x, y):
		xy = ((0, direction),)
	else:
		xy = ((0, direction), (0, 2*direction))

	for p in xy:
		x2 = p[0] + x
		y2 = p[1] + y
		if board.is_position_valid(x2, y2):
			if board.is_position_empty(x2, y2):
				mask.fields[x2][y2] = Mask.FLAG_MOVE
			else:
				break
	
	# possible captures relative to pawn's position
	xy = ((1, direction), (-1, direction))

	for p in xy:
		x2 = p[0] + x
		y2 = p[1] + y
		if board.is_position_valid(x2, y2):
			if board.is_position_empty(x2, y2) or board.is_position_enemy(x2, y2, is_white):
				mask.fields[x2][y2] = Mask.FLAG_CAPTURE
	
	if board.en_passant_position != None:
		px, py = board.en_passant_position
		if mask.fields[px][py] == mask.FLAG_CAPTURE:
			mask.fields[px][py] = mask.FLAG_EN_PASSANT | mask.FLAG_CAPTURE


def test_pawn_cleanup(board: Board, mask: Mask, x: int, y: int) -> None:
	
	for x2, y2 in ((x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)):
		if board.is_position_valid(x2, y2) and mask.fields[x2][y2] == Mask.FLAG_CAPTURE and board.is_position_empty(x2, y2):
			mask.fields[x2][y2] = Mask.FLAG_NONE


def create_piece_mask(board: Board, x: int, y: int, ignore_empty_tiles=True) -> Mask:
	
	assert x in range(0, board.SIZE)
	assert y in range(0, board.SIZE)
	
	field = board.fields[x][y]
	mask = Mask()

	match field.type:
		case Piece.TYPE_PAWN:
			test_pawn(board, mask, x, y)
			if ignore_empty_tiles:
				test_pawn_cleanup(board, mask, x, y)

		case Piece.TYPE_ROOK:
			test_perpendiculars(board, mask, x, y, board.SIZE - 1)

		case Piece.TYPE_BISHOP:
			test_diagonals(board, mask, x, y, board.SIZE - 1)

		case Piece.TYPE_KNIGHT:
			test_knight(board, mask, x, y)

		case Piece.TYPE_QUEEN:
			test_diagonals(board, mask, x, y, board.SIZE - 1)
			test_perpendiculars(board, mask, x, y, board.SIZE - 1)

		case Piece.TYPE_KING:
			test_diagonals(board, mask, x, y, 1)
			test_perpendiculars(board, mask, x, y, 1)
	
	return mask


def is_position_attacked(board: Board, x: int, y: int, by_white: bool) -> bool:
	color_filter = lambda data: board.fields[data[0]][data[1]].is_white == by_white
	pieces = tuple(filter(color_filter, board.get_all_pieces_positions()))

	for (x2, y2) in pieces:
		mask = create_piece_mask(board, x2, y2, False)
		if mask.fields[x][y] & Mask.FLAG_CAPTURE:
			return True
	
	return False


def get_attackers_positions(board: Board, x: int, y: int, are_white: bool) -> tuple[Position, ...]:

	def f(data: Position) -> bool:
		x2, y2 = data
		mask = create_piece_mask(board, x2, y2)
		return mask.fields[x][y] & Mask.FLAG_CAPTURE and board.fields[x2][y2].is_white == are_white

	return tuple(filter(f, board.get_all_pieces_positions()))


def try_promoting_pawn(board: Board, x: int, y: int) -> None:

	if board.fields[x][y].type == Piece.TYPE_PAWN \
	and ( (board.fields[x][y].is_white and y == 0) 
	or (not board.fields[x][y].is_white and y == board.SIZE-1) ):
		board.fields[x][y].type = Piece.TYPE_QUEEN
	


def en_passant_cleanup(board: Board, x: int, y: int, x2: int, y2: int) -> None:
	"Removes a pawn if it's captured en passant"

	if (x2, y2) == board.en_passant_position and board.fields[x][y].type == Piece.TYPE_PAWN:
		x3, y3 = board.moved_pieces[-1]
		board.fields[x3][y3].type = Piece.TYPE_NONE
	


def move_a_piece(board: Board, x: int, y: int, x2: int, y2: int) -> None:

	board.fields[x2][y2].type = board.fields[x][y].type
	board.fields[x2][y2].is_white = board.fields[x][y].is_white
	board.fields[x][y].type = Piece.TYPE_NONE
	# WARNING: doesn't update is_white on the starting position

	if board.was_piece_moved(x, y):
		board.moved_pieces.remove((x, y))
	
	board.moved_pieces.append((x2, y2))

	# checking for possible en passant
	if board.fields[x2][y2].type == Piece.TYPE_PAWN and abs(y-y2) == 2:
		direction_y = int((y2-y) / abs(y2-y))
		board.en_passant_position = (x, y+direction_y)
	else:
		board.en_passant_position = None


MoveSteps = list[tuple[int, int, int, int]]

def execute_a_move(board: Board, move_steps: MoveSteps) -> None: 
	
	for x, y, x2, y2 in move_steps:
		# WARNING_TO_MYSELF: effects of all of these 3 functions have to be concidered, when predicting moves effects
		en_passant_cleanup(board, x, y, x2, y2)
		move_a_piece(board, x, y, x2, y2)
		try_promoting_pawn(board, x2, y2)
	

def would_result_in(board: Board, is_white: bool, move_steps: tuple, result: MetaTag) -> bool:
	"is_white = is check/mate done by white. Returns true if performing move_steps would result in result (parameter) MetaTag"
	
	assert result in (Meta.TAG_CHECK, Meta.TAG_CHECKMATE)

	r = False
	
	for x, y, x2, y2 in move_steps:
		
		en_passant_cleanup(board, x, y, x2, y2)
		
		a: Piece = copy(board.fields[x][y])
		b: Piece = copy(board.fields[x2][y2])

		board.fields[x][y].type = Piece.TYPE_NONE
		board.fields[x2][y2] = copy(a)

		try_promoting_pawn(board, x2, y2)

		enemy_king_x, enemy_king_y = board.get_pieces_positions(Piece.TYPE_KING, not is_white)[0]

		is_check = is_position_attacked(board, enemy_king_x, enemy_king_y, is_white)
		
		if is_check:
			if result == Meta.TAG_CHECKMATE:
				r = is_checkmate(board, not is_white)
			else:
				r = result == Meta.TAG_CHECK
			
		# move cleanup
		# and pawn promotion cleanup
		board.fields[x][y] = a
		board.fields[x2][y2] = b

		# en passant cleanup cleanup
		if board.en_passant_position != None:

			epx, epy = board.moved_pieces[-1]

			if board.fields[epx][epy].type == Piece.TYPE_NONE:
				board.fields[epx][epy].type = Piece.TYPE_PAWN

	return r


def is_checkmate(board: Board, is_white: bool) -> bool:

	king_x, king_y = board.get_pieces_positions(Piece.TYPE_KING, is_white)[0]

	# 1. is king in check

	if not is_position_attacked(board, king_x, king_y, not is_white):
		return False

	# 2. can the check be cancelled
	
	# a. can the king move out of the check

	positions = (
		(-1, -1,), (0, -1), (1, -1),
		(-1, 0), (0, 1),
		(-1, 1), (0, 1), (1, 1),
	)

	for x, y in positions:
		if board.is_position_valid(x, y):
			if board.fields[x][y].type == Piece.TYPE_NONE \
			and not is_position_attacked(board, x, y, not is_white):
				# king can move out of the check
				return False

			elif board.fields[x][y].type != Piece.TYPE_NONE \
			and  board.fields[x][y].is_white != is_white:
				t = board.fields[x][y].type

				board.fields[x][y].type = Piece.TYPE_NONE

				is_attacked = is_position_attacked(board, x, y, not is_white)

				board.fields[x][y].type = t
				
				if not is_attacked:
					# king can capture the attacker
					return False

	# b. is number of attackers == 1:
	attackers_positions = get_attackers_positions(board, king_x, king_y, not is_white)
	if len(attackers_positions) == 1:
		
		x, y = attackers_positions[0]

		if is_position_attacked(board, x, y, is_white):

			t = board.fields[x][y].type
			board.fields[x][y].type = Piece.TYPE_NONE

			is_attacked = is_position_attacked(board, x, y, not is_white)

			board.fields[x][y].type = t

			if not is_attacked:
				# attacker can be captured
				return False

		if board.fields[x][y].type != Piece.TYPE_KNIGHT:
			attack_line = Mask()
			dx = int((king_x - x) / abs(king_x - x)) if king_x != x else 0
			dy = int((king_y - y) / abs(king_y - y)) if king_y != y else 0
			test_line(board, attack_line, x, y, dx, dy, board.SIZE - 1)

			for mx, row in enumerate(attack_line.fields):
				for my, flags in enumerate(row):
					if flags & Mask.FLAG_CAPTURE:
						attackers_positions = get_attackers_positions(board, mx, my, is_white)
					if attackers_positions and attackers_positions != ((king_x, king_y),):
						# a piece can move in between the king and the attacker
						# and the attacker isn't a knight
						return False
	
	# checkmate
	return True
