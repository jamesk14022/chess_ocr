import subprocess 
out_lines = subprocess.run(['./pgn-extract', '-r', 'test.pgn'], capture_output=True).stderr.decode('UTF-8').split("\n")

print(out_lines)

for line in out_lines:
	if "Unknown character" in line:
		print(f"unknown char: {line.split(' ')[2].strip()}")
	if "Unknown move text" in line:
		print(f"unknown move text: {line.split(' ')[3].strip()}") 


class Turn():
	def __init__(self, moves):
		self.moves = moves

class Move():
	def __init__(self, text, sus):
		self.text = text
		self.sus = sus	

		
	
