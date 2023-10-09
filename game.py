
import os
import move
import input_parser
from data_types import Board

class Game:
	def __init__(self) -> None:
		self.is_whites_turn: bool = True
		self.move_sequence: list[str] = []
		self.board: Board = Board()


def make_turn(game: Game, move_input: str) -> None | Exception:

	move_steps = input_parser.parse_and_complete(game.board, game.is_whites_turn, move_input)
	if isinstance(move_steps, Exception): return move_steps

	move.execute_a_move(game.board, move_steps)

	game.move_sequence.append(move_input)

	game.is_whites_turn = not game.is_whites_turn


def game_from_moves(moves: list[str], *, debug=False) -> Game | Exception:

	game = Game()

	for move in moves:

		turn = make_turn(game, move)

		if isinstance(turn, Exception):
			
			print(f'ERROR: Invalid move "{move}" ({turn})')
			
			if debug:
				print(f'Board: {game.board}')

			return turn
	
	return game


def run_user_input_game() -> None:

	game = Game()

	print('Input \'q\' at any time to quit')
	input("Press enter to continue: ")

	user_input = ''

	while True:

		print(game.board)

		user_input = input('Input move: ')

		if user_input == 'q':
			break

		turn = make_turn(game, user_input)

		if isinstance(turn, Exception):
			print(turn)
	
	print('Exited')


def read_pgn_file_data(path: str, game_index=0) -> str:
	"Can throw exceptions"

	if not os.path.exists(path):
		raise Exception(f"ERROR: File \"{path}\" does not exist")
	
	if not os.path.isfile(path):
		raise Exception(f"ERROR: \"{path}\" is not a file")

	if not path.endswith('.pgn'):
		raise Exception(f"ERROR: File \"{path}\" is not in the .pgn format")

	with open(path, 'r') as file:

		i = 0
		data = ''
		started_reading_moves = False


		for line in file:
			if line[0] == '[' and started_reading_moves:
				i += 1
				started_reading_moves = False
			elif line[0] == '1':
				started_reading_moves = True
			if i == game_index:
				data += line
		
		if game_index > i:
			raise Exception(f"ERROR: File \"{path}\" contains only {i+1} games")

		if not data:
			raise Exception(f"ERROR: File \"{path}\" is empty")

		return data


def extract_moves(pgn_data: str) -> list[str] | Exception:
	
	mid = pgn_data.rfind(']') + 1
	pgn_data = pgn_data[mid:]

	# removing comments
	while pgn_data.count(';') > 0:
		i = pgn_data.find(';')
		j = pgn_data.find('\n', i)
		pgn_data = pgn_data[:i] + pgn_data[j:]

	while pgn_data.count('{') > 0:
		i = pgn_data.find('{')
		j = pgn_data.find('}', i) + 1
		pgn_data = pgn_data[:i] + ' '  + pgn_data[j:]

	# getting rid of the elipsis, that happenes when a comment cuts a turn in half
	# eg. 1. a3 a5 -> 1. a3 {comment} 1... a5
	while pgn_data.count("...") > 0:
		j = pgn_data.find("...") + 3
		i = pgn_data.rfind(' ', 0, j)
		pgn_data = pgn_data[:i] + ' ' + pgn_data[j:]


	pgn_data = pgn_data.replace('\n', ' ').replace('.', ' ').replace('  ', ' ').strip()

	moves = []

	for i, m in enumerate(pgn_data.split()):
		if i % 3 == 0:
			continue
		moves.append(m)
	
	if len(moves) <= 1:
		return Exception("No valid moves found in file")

	# TODO
	# getting rid of games result (eg. "1-0")
	moves.pop()

	return moves


def game_from_pgn_data(data: str, *, debug=False) -> Game | Exception:

	moves = extract_moves(data)

	if isinstance(moves, Exception):
		return moves
	else:
		return game_from_moves(moves, debug=debug)
