import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
RENDERING_PATH = os.path.join(ROOT_PATH, 'lib\\deep-motion-editing\\blender_rendering\\')
ANIMATION_PATH = os.path.join(ROOT_PATH, '..\\Data\\360fps\\animation.bvh')

TEST = True

def main():

	while True:
		print('Please select the type of operation you want to perform:')
		print('1. Render')
		print('2. Skinning')
		print('0. Exit the program')

		if TEST:
			option = '1'
		else:
			option = input('Enter your choice: ')

		if option == '1':
			os.chdir(RENDERING_PATH)
			os.system(f"blender -P render.py -- --bvh_path={ANIMATION_PATH}")
			break
		elif option == '2':
			break
		elif option == '0':
			print('Exiting the program...')
			break
		else:
			print('Invalid input, try again.')

main()