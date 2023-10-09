from typing import Optional, Generic, TypeVar


class Piece:

	TYPE_NONE: int = 0
	TYPE_PAWN: int = 1
	TYPE_ROOK: int = 2
	TYPE_BISHOP: int = 3
	TYPE_KNIGHT: int = 4
	TYPE_QUEEN: int = 5
	TYPE_KING: int = 6
	TYPE_PLACEHOLDER: int = 7

	TYPE_TO_CHAR: dict = {} # initialised below
	CHAR_TO_TYPE: dict = {} # initialised below

	def __init__(self, type: int, is_white: bool) -> None:
		self.type: int = type
		self.is_white: bool = is_white

	def __repr__(self) -> str:
		char: str = Piece.TYPE_TO_CHAR[self.type]
		
		if self.is_white:
			char = char.upper()
		
		return char

	@classmethod
	def get_valid_piece_chars(cls) -> tuple:
		return tuple(sorted(cls.CHAR_TO_TYPE.keys()))[1:]

Piece.TYPE_TO_CHAR = {
	Piece.TYPE_NONE: '_',
	Piece.TYPE_PAWN: 'p',
	Piece.TYPE_ROOK: 'r',
	Piece.TYPE_BISHOP: 'b',
	Piece.TYPE_KNIGHT: 'n',
	Piece.TYPE_QUEEN: 'q',
	Piece.TYPE_KING: 'k',
}

Piece.CHAR_TO_TYPE = {
	Piece.TYPE_TO_CHAR[k]: k for k in Piece.TYPE_TO_CHAR
}




T = TypeVar('T', Piece, int)

class SquareGrid(Generic[T]):
	
	# WARNING: (0, 0) is in the top-left corner,
	# but the y axis is numbered in reverse, when the grid is printed

	SIZE: int = 8
	RANK_SYMBOLS: str = "12345678"[::-1]	# y 
	FILE_SYMBOLS: str = "abcdefgh"			# x

	@classmethod
	def rank_to_y(cls, number: str) -> int:
		"ex. '1' -> 0"
		return cls.RANK_SYMBOLS.find(number)

	@classmethod
	def file_to_x(cls, letter: str) -> int:
		"ex. 'a' -> 0"
		return cls.FILE_SYMBOLS.find(letter)

	@classmethod
	def parse_position(cls, x: int, y: int) -> str:
		"(0, 0) -> 'a8'"
		return cls.FILE_SYMBOLS[x] + cls.RANK_SYMBOLS[y]

	def __init__(self) -> None:
		self.fields: list[list[T]] = []
	
	def __str__(self) -> str:
		s = '\n  '
		for i in range(self.SIZE):
			s += f'{self.FILE_SYMBOLS[i]} '
		s += '\n'

		for y in range(self.SIZE):
			s += f'{self.RANK_SYMBOLS[y]} '
			# s += f'{self.RANK_SYMBOLS[-y-1]} '
			for x in range(self.SIZE):
				s += f'{self.str_field(self.fields[x][y])} '
			s += '\n'
		return s

	def str_field(self, field) -> str:
		return str(field)




DEFAULT_BOARD_DATA = [
	"rnbqkbnr",
	"pppppppp",
	"________",
	"________",
	"________",
	"________",
	"PPPPPPPP",
	"RNBQKBNR",
]

Position = tuple[int, int]

class Board(SquareGrid[Piece]):
	
	def __init__(self, board_data: list[str] = DEFAULT_BOARD_DATA) -> None:
		assert len(board_data) == self.SIZE

		super().__init__()
		
		for y in range(self.SIZE):
			assert len(board_data[y]) == self.SIZE
			
			self.fields.append([])
		
			for x in range(self.SIZE):
				char = board_data[x][y]
				assert char.lower() in Piece.CHAR_TO_TYPE.keys()
				
				is_white = char.isupper()
				type = Piece.CHAR_TO_TYPE[char.lower()]

				self.fields[y].append(Piece(type, is_white))

		self.moved_pieces: list[Position] = [] # [(x, y), ...]
		self.en_passant_position: Optional[Position] = None
	
	def is_position_valid(self, x: int, y: int) -> bool:
		return x >= 0 and y >= 0 and x < self.SIZE and y < self.SIZE

	def is_position_empty(self, x: int, y: int) -> bool:
		return self.fields[x][y].type == Piece.TYPE_NONE
	
	def is_position_enemy(self, x: int, y: int, of_white: bool) -> bool:
		"WARNING: Tile's is_white property isn't updated, when a piece moves out of it, only check non empty tiles"
		return self.fields[x][y].is_white != of_white

	def was_piece_moved(self, x: int, y: int) -> bool:
		return (x, y) in self.moved_pieces

	def get_all_pieces_positions(self) -> list[Position]:
		ret: list[Position] = []
		
		for x, row in enumerate(self.fields):
			for y, field in enumerate(row):
				if field.type != Piece.TYPE_NONE:
					ret.append((x, y))
		return ret
	
	def get_pieces_positions(self, type: int, is_white: bool) -> tuple[Position, ...]:
		
		def f(data: Position) -> bool:
			x, y = data
			return self.fields[x][y].type == type and self.fields[x][y].is_white == is_white

		return tuple(filter(f, self.get_all_pieces_positions()))


class Mask(SquareGrid[int]):

	FLAG_NONE: int = 1
	FLAG_MOVE: int = 2
	FLAG_CAPTURE: int = 4
	FLAG_EN_PASSANT: int = 8

	FLAG_PAWN_PROMOTION: int = 16 # unused as a field value
	FLAG_CHECK: int = 32 # unused as a field value
	FLAG_CHECKMATE: int = 64 # unused as a field value

	FLAG_TO_CHAR: dict = {} # initialised below

	def __init__(self) -> None:
		super().__init__()
		mask_data = [[self.FLAG_NONE] * self.SIZE] * self.SIZE
		
		for y in range(self.SIZE):
			self.fields.append([])
		
			for x in range(self.SIZE):
				self.fields[y].append(mask_data[x][y])

	def str_field(self, field) -> str:
		return Mask.FLAG_TO_CHAR[field]

Mask.FLAG_TO_CHAR = {
	Mask.FLAG_NONE: '_',
	Mask.FLAG_MOVE: '.',
	Mask.FLAG_CAPTURE: 'x',
	Mask.FLAG_MOVE | Mask.FLAG_CAPTURE: '-',
	Mask.FLAG_EN_PASSANT: '&'
}

# for testing
def mask_from_list(l: list[str]) -> Mask:
	
	CHAR_TO_FLAG = {v: k for k, v in Mask.FLAG_TO_CHAR.items()}
	mask: Mask = Mask()

	for y, line in enumerate(l):
		for x, char in enumerate(line):
			f = CHAR_TO_FLAG[char]
			mask.fields[x][y] = f

	return mask




MetaTag = int

class Meta: # just an enum
	TAG_CAPTURE: MetaTag = 0
	TAG_MOVE: MetaTag = 1
	TAG_EN_PASSANT: MetaTag = 2
	TAG_PAWN_PROMOTION: MetaTag = 3
	TAG_CHECK: MetaTag = 4
	TAG_CHECKMATE: MetaTag = 5
	