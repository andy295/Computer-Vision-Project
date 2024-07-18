import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DME_PATH = os.path.join(ROOT_PATH, 'lib\\deep-motion-editing\\blender_rendering\\')
ANIMATION_PATH = os.path.join(ROOT_PATH, '..\\Data\\360fps\\animation.bvh')
CHARACTER_PATH = os.path.join(ROOT_PATH, 'Data\\Character\\X-Bot.fbx')

def main():

	while True:
		print('Please select the type of operation you want to perform:')
		print('1. Render')
		print('2. Skinning')
		print('0. Exit the program')

		option = input('Enter your choice: ')

		if option == '1':
			os.chdir(DME_PATH)
			os.system(f"blender -P render.py -- --bvh_path={ANIMATION_PATH}")
			break
		elif option == '2':
			os.chdir(DME_PATH)
			os.system(f"blender -P skinning.py -- --bvh_file={ANIMATION_PATH} --fbx_file={CHARACTER_PATH}")
			break
		elif option == '0':
			print('Exiting the program...')
			break
		else:
			print('Invalid input, try again.')

main()
