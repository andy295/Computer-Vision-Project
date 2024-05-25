import open3d as o3d
import imageio

from global_constants import *

def plotData(filePath=None, data=None):
    if data is None or filePath is None:
      print(f'Error: Invalid data or file path\n')

    fName = os.path.basename(filePath)
    fName, fExt = os.path.splitext(fName)
    if fExt == EXTENSIONS[Extension.csv]:

      if fName == RIGID_BODY:
        markerRigidBodyPlot(data, fName)
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


def visualizeAndSaveSequence(visualizer, markersList, fName):
  images=[]
  # Iteration over all the point clouds
  for marker in markersList:
    visualizer.clear_geometries() #clears any existing geometries from the visualizer
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(marker) #sets the points of the pcd from the points in the marker tuple
    visualizer.add_geometry(pcd) #adds the pcd to the visualizer for rendering
    visualizer.update_geometry(pcd) 
    visualizer.poll_events() 
    visualizer.update_renderer()
    
  # images = np.array(images)
  # for img in images:
  #   img = (img[..., :3] * 255).astype(np.uint8) #convert to rgb
  # if os.path.exists(SAVE_VIDEO_PATH+fName):
  #   return
  # imageio.mimsave(SAVE_VIDEO_PATH+fName, images, fps=FPS) #save the images as a video

  visualizer.destroy_window()


def setVisualizer(pointSize):

  # Creation of the visualizer window
  visualizer = o3d.visualization.Visualizer()
  visualizer.create_window(window_name='Open3D', width=720, height=480)
  visualizer.get_render_option().background_color = np.asarray([0, 0, 0]) #black background
  visualizer.get_render_option().point_size = pointSize

  return visualizer


#plots the rigid body markers
def markerRigidBodyPlot(data, fName):
    points1 = []
    points2 = []
    points3 = []
    points4 = []
    allMarkers = []
    
    # transform from dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])  
    points1 = list(zip(data[1]._positions['x'], data[1]._positions['y'], data[1]._positions['z']))
    points2 = list(zip(data[2]._positions['x'], data[2]._positions['y'], data[2]._positions['z']))
    points3 = list(zip(data[3]._positions['x'], data[3]._positions['y'], data[3]._positions['z']))
    points4 = list(zip(data[4]._positions['x'], data[4]._positions['y'], data[4]._positions['z']))
    allMarkers = list(zip(points1, points2, points3, points4)) #list of tuples [xyz, xyz, xyz, xyz],
                                                              #where each tuple is a point cloud

    # Creation of the visualizer object (the visualization window)
    visualizer = setVisualizer(10.0)

    visualizeAndSaveSequence(visualizer, allMarkers, fName)


def skeletonMarkerPlot(data, fName):

    bonesMarkerList = []
    for model in data:
      if model._description['Type'] == 'Bone Marker':
        points = list(zip(model._positions['x'], model._positions['y'], model._positions['z']))
        bonesMarkerList.append(points)

    bonesMarkerList = list(zip(*bonesMarkerList)) #list of tuples [xyz, xyz, xyz, xyz]

    # Creation of the visualizer window
    visualizer = setVisualizer(8.0)

    visualizeAndSaveSequence(visualizer, bonesMarkerList, fName)


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
