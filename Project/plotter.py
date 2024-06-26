import open3d as o3d
import pyautogui
import shutil

from global_constants import *

# data is a list of models. A model is a group of columns (i.e. the model 'marker' or 'bone')
def plotData(filePath=None, data=None):
    if data is None or filePath is None:
      print(f'Error: Invalid data or file path\n')

    fName = os.path.basename(filePath)
    fName, fExt = os.path.splitext(fName)
    if fExt == EXTENSIONS[Extension.csv]:

      if fName == RIGID_BODY:
        while True:
          print(f'Please select the type of rigid body visualization')
          print(f'1. Original rigid body points')
          print(f'2. Kalman filtered rigid body points')
          print(f'3. Linear regression estimated rigid body points')
          print(f'4. Spline interpolation estimated rigid body points')
          print(f'0. Exit the program')

          option = input(f'Enter your choice: ')
          if option == '1':
            print(f'Original rigid body points')
            # markerRigidBodyPlot(data, fName, None)

          elif option == '2':
            print(f'Kalman filtered rigid body points')
            # markerRigidBodyPlot(data, fName, KALMAN_FILTER)

          elif option == '3':
            print(f'Linear regression estimated rigid body points')
            # markerRigidBodyPlot(data, fName, LINEAR_REGRESSION)

          elif option == '4':
            print(f'Spline interpolation estimated rigid body points')
            # markerRigidBodyPlot(data, fName, SPLINE_INTERPOLATION)

          elif option == '0':
            # exit the loop and end the program
            break

          else:
              print(f'Invalid input, try again.')

          print()

        return True

      elif fName == SKELETON:

        while True:
          print(f'Please select the type of skeleton visualization:')
          print(f'1. Skeleton with markers')
          print(f'2. Skeleton joints')
          print(f'0. Exit the program')

          option = input(f'Enter your choice: ')
          if option == '1':
            print(f'Skeleton with markers')
            # skeletonMarkerPlot(data, fName)
            return True

          elif option == '2':
            print(f'Skeleton joints')
            # skeletonJointsPlot(data, fName)
            return True

          elif option == '0':
            # exit the loop and end the program
            break

          else:
              print(f'Invalid input, try again.')

    else:
        print(f'Error: Invalid file extension: {fExt}\n')


def getIndex(start, dictionary):
  for key in dictionary.keys():
    if start in key:
      return list(dictionary.keys()).index(key)

  return -1


def visualizeSequence(visualizer, markersList, fName, SAVE):

  if SAVE:
    # # Get screen size
    # screen_size = (pyautogui.size().width, pyautogui.size().height)
    # # Define the codec using VideoWriter_fourcc() and create a VideoWriter object
    # fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # out = cv2.VideoWriter(SAVE_VIDEO_PATH + fName, fourcc, FPS, screen_size)
    # cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Recording", 480, 270)
    # Iteration over all the point clouds
    for i, marker in enumerate(markersList):
      # if i % 3 == 0: #skip every 3rd frame to reduce computations
      #   continue
      visualizer.clear_geometries() #clears any existing geometries from the visualizer
      pcd = o3d.geometry.PointCloud()
      pcd.points = o3d.utility.Vector3dVector(marker) #sets the points of the pcd from the points in the marker tuple
      visualizer.add_geometry(pcd) #adds the pcd to the visualizer for rendering
      visualizer.update_geometry(pcd)
      visualizer.poll_events()
      visualizer.update_renderer()
      # Capture screenshot
      img = pyautogui.screenshot()
      # Convert the image into numpy array representation
      frame = np.array(img)
      # Write the RBG image to file
      out.write(frame)
      # Display screen/frame being recorded
      cv2.imshow('Recording', frame)

      # Wait for the user to press 'q' key to stop the recording
      if cv2.waitKey(1) == ord('q'):
        break

    # Release the VideoWriter object
    # out.release()
    # cv2.destroyAllWindows()

  else:
    for i, marker in enumerate(markersList):
      # if i % 3 == 0: #skip every 3rd frame to reduce computations
      #   continue
      visualizer.clear_geometries() #clears any existing geometries from the visualizer
      pcd = o3d.geometry.PointCloud()
      pcd.points = o3d.utility.Vector3dVector(marker) #sets the points of the pcd from the points in the marker tuple
      visualizer.add_geometry(pcd) #adds the pcd to the visualizer for rendering
      visualizer.update_geometry(pcd)
      visualizer.poll_events()
      visualizer.update_renderer()

  visualizer.destroy_window()


def setVisualizer(pointSize):

  # Creation of the visualizer window
  visualizer = o3d.visualization.Visualizer()
  visualizer.create_window(window_name='Open3D', width=720, height=480)
  # visualizer.set_full_screen(True)
  visualizer.get_render_option().background_color = np.asarray([0, 0, 0]) #black background
  visualizer.get_render_option().point_size = pointSize

  return visualizer


def recordAndSave(path, fName):

  # Get screen size
  screen_size = (pyautogui.size().width, pyautogui.size().height)
  # Define the codec using VideoWriter_fourcc() and create a VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*"XVID")
  out = cv2.VideoWriter(path + fName, fourcc, FPS, screen_size)
  cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)
  cv2.resizeWindow("Recording", 480, 270)
  while True:
    # Capture screenshot
    img = pyautogui.screenshot()
    # Convert the image into numpy array representation
    frame = np.array(img)
    # Write the RBG image to file
    out.write(frame)
    # Display screen/frame being recorded
    cv2.imshow('Recording', frame)

    # Wait for the user to press 'q' key to stop the recording
    if cv2.waitKey(1) == ord('q'):
        break

  # Release the VideoWriter object
  out.release()
  cv2.destroyAllWindows()


def clear_directory(directory, value):
    if value == 0:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

#plots the rigid body markers
def markerRigidBodyPlot(data, fName, typeOfFiltering):

  allMarkers = []
  # plot the original points
  if typeOfFiltering == None:
    # transform from dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
    for model in data:
      points = list(zip(model._positions[X], model._positions[Y], model._positions[Z]))
      allMarkers.append(points)

  else: #takes the filtered points based on the filter requested
    # transform from dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
    for model in data:
      filteredPoints = getattr(model, typeOfFiltering)
      points = list(zip(filteredPoints[X],filteredPoints[Y],filteredPoints[Z]))
      allMarkers.append(points)
  
  #transform to list of tuples [xyz, xyz, xyz, xyz] where each tuple is a point cloud
  allMarkers = list(zip(*allMarkers)) 
  visualizer = setVisualizer(10)
  visualizeSequence(visualizer, allMarkers, fName, SAVE = False)
  #save the video
  # while True:
  #   print("Do you want to save the video?")
  #   print("1. YES")
  #   print("0. NO. Exit the program")

  #   option = input("Enter your choice: ")
  #   if option == '1':
  #     print("Saving and showing video...")
  #     visualizer = setVisualizer(10.0)
  #     visualizeSequence(visualizer, allMarkers, fName, SAVE=True)
  #     print("Video saved")
  #     return True

  #   elif option == '0':
  #     print("Showing video...")
  #     visualizer = setVisualizer(10.0)
  #     visualizeSequence(visualizer, allMarkers, fName, SAVE=False)
  #     print("Video not saved")
  #     break # Exit the loop and end the program

  #   else:
  #     print("Invalid input, try again.")


def skeletonMarkerPlot(data, fName):

    bonesMarkerList = []
    for model in data:
      if model._description['Type'] == 'Bone Marker':
        points = list(zip(model._positions['x'], model._positions['y'], model._positions['z']))
        bonesMarkerList.append(points)

    bonesMarkerList = list(zip(*bonesMarkerList)) #list of tuples [xyz, xyz, xyz, xyz]

    # Creation of the visualizer window
    visualizer = setVisualizer(8.0)

    while True:
      print("Do you want to save the video?")
      print("1. YES")
      print("0. NO. Exit the program")

      option = input("Enter your choice: ")
      if option == '1':
        print("Saving and showing video...")
        images = visualizeSequence(visualizer, bonesMarkerList, fName, True)
        print("Video saved")
        return True

      elif option == '0':
        print("Showing video...")
        visualizeSequence(visualizer, bonesMarkerList, fName, False)
        print("Video not saved")
        break # Exit the loop and end the program

      else:
        print("Invalid input, try again.")


def skeletonJointsPlot(data, fName):

  bonesPosDict = {}
  jointsGraph = {
    'Hip' : ['Ab', 'RThigh', 'LThigh'],
    'Ab' : ['Chest'],
    'Chest' : ['Neck'],
    'Neck' : ['Head', 'RShoulder', 'LShoulder'],
    #'Head' : ['Neck'], #we know  head is not connected to anything new
    'LShoulder' : ['LUArm'],
    'LUArm' : ['LFArm'],
    'LFArm' : ['LHand'],
    #'LHand' : ['LFArm'], #we know  hand is not connected to anything new
    'RShoulder' : ['RUArm'],
    'RUArm' : ['RFArm'],
    'RFArm' : ['RHand'],
    #'RHand' : ['RFArm'], #we know  hand is not connected to anything new
    'LThigh' : ['LShin'],
    'LShin' : ['LFoot'],
    'LFoot' : ['LToe'],
    #'LToe' : ['LFoot'], #we know  toe is not connected to anything new
    'RThigh' : ['RShin'],
    'RShin' : ['RFoot'],
    'RFoot' : ['RToe'],
    #'RToe' : ['RFoot'] #we know  toe is not connected to anything new
  }

  for model in data:
    if model._description['Type'] != 'Bone Marker':
      points = list(zip(model._positions['x'], model._positions['y'], model._positions['z']))
      bonesPosDict[model._description['Name']] = points

  # Get the lists of points from the dictionary values
  lists_of_points = list(bonesPosDict.values())

  # Use zip to combine corresponding points from each list into tuples
  lists_of_points = list(zip(*lists_of_points))

  vertices = []
  #we adapt a list of tuples [xyz, xyz, xyz, xyz] to Open3D
  for skeletonPoints in lists_of_points:
    vertices.append(np.array(skeletonPoints))

  # Create a Visualizer object
  visualizer = setVisualizer(10.0)

  # Create line set to represent edges in the graph
  lines = []
  for start, ends in jointsGraph.items():
      start_idx = getIndex(start, bonesPosDict)
      for end in ends:
          end_idx = getIndex(end, bonesPosDict)
          lines.append([start_idx, end_idx])

  line_set = o3d.geometry.LineSet()
  #line_set.points = o3d.utility.Vector3dVector(vertices)
  line_set.lines = o3d.utility.Vector2iVector(lines)

  # Set line color (e.g., red)
  line_color = [1, 0, 0]  # RGB color (red)

  # Create a LineSet with colored lines
  line_set.colors = o3d.utility.Vector3dVector(np.tile(line_color, (len(lines), 1)))

  # Iteration over all the point clouds
  for skeletonPoints in vertices:
    visualizer.clear_geometries()
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(skeletonPoints)
    line_set.points = o3d.utility.Vector3dVector(skeletonPoints)
    visualizer.add_geometry(pcd)
    visualizer.add_geometry(line_set)
    visualizer.update_geometry(pcd)
    visualizer.update_geometry(line_set)
    visualizer.poll_events()
    visualizer.update_renderer()

  visualizer.destroy_window()
