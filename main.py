import game
import sys


def print_usage(sys_argv: list[str]) -> None:
	print(f"Usage:")
	print(f'\t{sys_argv[0]} <file> \t\t (Read the first game from a .pgn file)')
	print(f'\t{sys_argv[0]} <file> <index> \t (Read game from a .pgn file. Indexes start at 1)')
	print(f'\t{sys_argv[0]} --play \t\t (Simulate game from keyboard inputs)')
	# print(f'\t{sys_argv[0]} --length <file> \t (Prints the number of games in a .pgn file)')
	print(f'\t{sys_argv[0]} --help \t\t (Print this message)')


def read_game(sys_argv: list[str]) -> None:
	
	_, path, arg2 = sys_argv

	i: int

	try:
		# WARNING: 1 is substracted to make it more human intuitive
		i = int(arg2) - 1
		if i < 0:
			raise Exception()
	except:
		print("ERROR: The second argument needs to be a positive intiger")
		# print_usage(sys_argv)
		exit(1)
	
	data: list[str]

	try:
		data = game.read_pgn_file_data(path, i)
	except Exception as e:
		print(e)
		# print_usage(sys_argv)
		exit(1)

	g = game.game_from_pgn_data(data, debug=True)

	if isinstance(g, Exception):
		print(g)
		exit(1)
	else:
		print(g.board)


def main(sys_argv: list[str]) -> None:

	match len(sys_argv):
		case 2:
			match sys_argv[1]:
				case "-p" | "--play":
					game.run_user_input_game()
				case "-h" | "--help":
					print_usage(sys_argv)
				case _:
					read_game(sys_argv + ['1'])

		case 3:
			match sys_argv[1]:
				# case "-l" | "--length":
				# 	pass
				case _:
					read_game(sys_argv)
			
		case n:
			if n == 1:
				print('ERROR: No arguments were provided')
			else:
				print("ERROR: Too many arguments")
			print_usage(sys_argv)
			exit(1)


if __name__ == '__main__':
	
	main(sys.argv)

	# errors = {}
	
	# for i in range(3000):
	# 	g = game.game_from_pgn_data(game.read_pgn_file_data('tests/data/Adams.pgn', i), debug=True)
	# 	if isinstance(g, Exception):
	# 		errors[str(g)] = errors.get(str(g), 0) + 1

	# print(errors)



