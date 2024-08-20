import open3d as o3d
import pyautogui
import shutil
import cv2
from global_constants import *

FPS = 64

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
          print(f'3. Spline interpolation estimated rigid body points')
          print(f'0. Exit the program')

          option = input(f'Enter your choice: ')
          if option == '1':
            print(f'Original rigid body points')
            markerRigidBodyPlot(data, fName, None)

          elif option == '2':
            print(f'Kalman filtered rigid body points')
            markerRigidBodyPlot(data, fName, KALMAN_FILTER)

          elif option == '3':
            print(f'Spline interpolation estimated rigid body points')
            markerRigidBodyPlot(data, fName, SPLINE_INTERPOLATION)

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
            skeletonMarkerPlot(data, fName)
            return True

          elif option == '2':
            print(f'Skeleton joints')
            skeletonJointsPlot(data, fName)
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

# Function to render and optionally saves a sequence of 3D marker frames using a visualizer.
# It processes each frame by updating the visualizer with new point cloud data and either
# captures and writes the frames to a video file or simply displays them.
# The function skips certain frames to reduce computation and finally releases resources
# or closes the visualizer window.
def visualizeSequence(visualizer, markersList, fName, SAVE_VIDEO):

  videoWriter = cv2.VideoWriter(SAVE_VIDEO_PATH + fName + '.avi', cv2.VideoWriter_fourcc(*'DIVX'), FPS, (720, 480))
  if SAVE_VIDEO:
    for i, marker in enumerate(markersList):
      if i % 3 == 0: # skip every 3rd frame to reduce computations
        continue
      if i % 5 == 0: # skip every 5th frame to reduce computations
        continue
      visualizer.clear_geometries() # clears any existing geometries from the visualizer
      pcd = o3d.geometry.PointCloud()
      pcd.points = o3d.utility.Vector3dVector(marker) # sets the points of the pcd from the points in the marker tuple
      visualizer.add_geometry(pcd) # adds the pcd to the visualizer for rendering
      visualizer.update_geometry(pcd)
      visualizer.poll_events()
      visualizer.update_renderer()

      # image = visualizer.capture_screen_float_buffer(do_render = True)
      # image = np.asarray(image)
      # images.append(image)

      image = visualizer.capture_screen_float_buffer(do_render=True)
      image = np.asarray(image)
      image = (image * 255).astype(np.uint8)  # convert to 8-bit image
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # convert to BGR for OpenCV

      # write the frame to the video
      videoWriter.write(image)

    videoWriter.release()

  else:
    for i, marker in enumerate(markersList):
      if i % 2 == 0: # skip every 3rd frame to reduce computations
        continue
      visualizer.clear_geometries() # clears any existing geometries from the visualizer
      pcd = o3d.geometry.PointCloud()
      pcd.points = o3d.utility.Vector3dVector(marker) #sets the points of the pcd from the points in the marker tuple
      visualizer.add_geometry(pcd) # adds the pcd to the visualizer for rendering
      visualizer.update_geometry(pcd)
      visualizer.poll_events()
      visualizer.update_renderer()

  visualizer.destroy_window()


def setVisualizer(pointSize):

  # creation of the visualizer window
  visualizer = o3d.visualization.Visualizer()
  visualizer.create_window(window_name='Open3D', width=720, height=480)
  visualizer.get_render_option().background_color = np.asarray([0, 0, 0]) #black background
  visualizer.get_render_option().point_size = pointSize

  return visualizer

# Function to visualize 3D marker data from a list of models. Depending on whether filtering
# is applied, it either uses original or filtered marker positions. The function transforms
# the marker data into a format suitable for visualization,
# then uses a visualizer to display a sequence of the marker points.
def markerRigidBodyPlot(data, fName, typeOfFiltering):

  allMarkers = []
  # plot the original points
  if typeOfFiltering == None:
    # transform from dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
    for model in data:
      points = list(zip(model._positions[X], model._positions[Y], model._positions[Z]))
      allMarkers.append(points)

  else: # takes the filtered points based on the filter requested
    # transform from dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
    for model in data:
      filteredPoints = getattr(model, typeOfFiltering)
      points = list(zip(filteredPoints[X],filteredPoints[Y],filteredPoints[Z]))
      allMarkers.append(points)
  
  # transform to list of tuples [xyz, xyz, xyz, xyz] where each tuple is a point cloud
  allMarkers = list(zip(*allMarkers)) 
  visualizer = setVisualizer(10)
  visualizeSequence(visualizer, allMarkers, fName, SAVE_VIDEO = False)

# Function to visualize 3D marker data from a list of models and optionally saves the video
# of the visualization. It collects the positions of markers, prepares them for visualization,
# and then prompts the user whether to save the video. Based on the user's choice, it either
# saves the video or just displays it using the `visualizeSequence` function.
def skeletonMarkerPlot(data, fName):

    bonesMarkerList = []
    for model in data:
      if model._description['Type'] == 'Marker':
        points = list(zip(model._positions['x'], model._positions['y'], model._positions['z']))
        bonesMarkerList.append(points)

    bonesMarkerList = list(zip(*bonesMarkerList)) #list of tuples [xyz, xyz, xyz, xyz]

    while True:
      print("Do you want to save the video?")
      print("1. YES")
      print("0. NO")

      option = input("Enter your choice: ")
      if option == '1':
        print("Saving and showing video...")
        SAVE_VIDEO = True
        visualizer = setVisualizer(8.0)
        visualizeSequence(visualizer, bonesMarkerList, fName, SAVE_VIDEO)
        print("Video saved")
        break

      elif option == '0':
        print("Showing video...")
        SAVE_VIDEO = False
        visualizer = setVisualizer(8.0)
        visualizeSequence(visualizer, bonesMarkerList, fName, SAVE_VIDEO)
        print("Video not saved")
        break

      else:
        print("Invalid input, try again.")

# Function to visualize 3D skeleton data by plotting the joints and connecting bones.
# It constructs a graph representing the skeleton structure, where each joint is connected
# to others according to a predefined hierarchy.
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
    if model._description['Type'] != 'Marker':
      points = list(zip(model._positions['x'], model._positions['y'], model._positions['z']))
      bonesPosDict[model._description['Name']] = points

  # get the lists of points from the dictionary values
  lists_of_points = list(bonesPosDict.values())

  # use zip to combine corresponding points from each list into tuples
  lists_of_points = list(zip(*lists_of_points))

  vertices = []
  # we adapt a list of tuples [xyz, xyz, xyz, xyz] to Open3D
  for skeletonPoints in lists_of_points:
    vertices.append(np.array(skeletonPoints))

  # create a Visualizer object
  visualizer = setVisualizer(10.0)

  # create line set to represent edges in the graph
  lines = []
  for start, ends in jointsGraph.items():
      start_idx = getIndex(start, bonesPosDict)
      for end in ends:
          end_idx = getIndex(end, bonesPosDict)
          lines.append([start_idx, end_idx])

  line_set = o3d.geometry.LineSet()
  # line_set.points = o3d.utility.Vector3dVector(vertices)
  line_set.lines = o3d.utility.Vector2iVector(lines)

  # set line color (e.g., red)
  line_color = [1, 0, 0] # RGB color (red)

  # create a LineSet with colored lines
  line_set.colors = o3d.utility.Vector3dVector(np.tile(line_color, (len(lines), 1)))

  # iteration over all the point clouds
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
