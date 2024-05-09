import open3d as o3d
import numpy as np


def getIndex(start, dictionary):
  for key in dictionary.keys():
    if start in key:
      return list(dictionary.keys()).index(key)
  return -1 


def visualizeSequence(visualizer, markersList):
  # Iteration over all the point clouds
  for marker in markersList:
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
  visualizer.get_render_option().background_color = np.asarray([0, 0, 0]) #black background
  visualizer.get_render_option().point_size = pointSize
  return visualizer


#this function plots the rigid body markers
def markerRigidBodyPlot(data):
    #rigidBodyMarker = []
    points1 = []
    points2 = []
    points3 = []
    points4 = []
    allMarkers = []
    
    #                 dictionary[str, dict[str, dict[str, list]]], 
    #                           .          .         .        .
    #                          .           .          .         .
    #                         .            .           .          .
    #                      marker1      Position       x          [x1, x2, x3, ...]
    #                    marker2     MarkerQuality     y           [y1, y2, y3, ...]
    #dataList = list(data.items())
    for key, value in data.items():
      
      # This is for extracting the Rigid body point but it's almost the same point as marker 4
      #if key == 'Rigid_Body-Ragnetto-54A2169DEC4611EE5F75BB645DD45CA7':
      #  print(f'Key rbr: {key}')
      #   for key2, value2 in value.items():
      #    if key2 == 'Position':
      #      rigidBodyMarker = list(zip(value2['X'], value2['Y'], value2['Z']))
      
      #we search for the key corresponding to the marker we want to use, 
      #then we move to its value (another dictionary)
      if key == 'Rigid_Body_Marker-Ragnetto:Marker1-54A2169DEC4611EE5F75BB645DD45CA7':
        for key2, value2 in value.items(): 
          if key2 == 'Position':
            points1 = list(zip(value2['X'], value2['Y'], value2['Z'])) #transform from
                        # dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
      
      if key == 'Rigid_Body_Marker-Ragnetto:Marker2-54A2169DEC4611EE5F75BB645DD45CA7':
        for key2, value2 in value.items():
          if key2 == 'Position':
            points2 = list(zip(value2['X'], value2['Y'], value2['Z'])) #transform from
                        # dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
            
      if key == 'Rigid_Body_Marker-Ragnetto:Marker3-54A2169DEC4611EE5F75BB645DD45CA7':
        for key2, value2 in value.items():
          if key2 == 'Position':
            points3 = list(zip(value2['X'], value2['Y'], value2['Z'])) #transform from
                        # dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
      
      if key == 'Rigid_Body_Marker-Ragnetto:Marker4-54A2169DEC4611EE5F75BB645DD45CA7':
        for key2, value2 in value.items(): 
          if key2 == 'Position':
            points4 = list(zip(value2['X'], value2['Y'], value2['Z'])) #transform from
                        # dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
          
    allMarkers = list(zip(points1, points2, points3, points4)) #list of tuples [xyz, xyz, xyz, xyz],
                                                              #where each tuple is a point cloud

    # Creation of the visualizer object (the visualization window)
    visualizer = setVisualizer(10.0)
    
    visualizeSequence(visualizer, allMarkers)
    
    
def skeletonMarkerPlot(data):
    bonesMarkerList = []
    
    #                dictionary[str, dict[str, dict[str, list]]]
    #                           .          .         .        .
    #                          .           .          .         .
    #                         .            .           .          .
    #                      marker1      Position       x          [x1, x2, x3, ...]
    #                    marker2     MarkerQuality     y           
    for key, value in data.items():
      #we search for the key corresponding to the marker we want to use, 
      #then we move to its value (another dictionary)
      if 'Marker' in key:
        for key2, value2 in value.items():
          if key2 == 'Position':
            points = list(zip(value2['X'], value2['Y'], value2['Z'])) #transform from
                        # dictionary[(X:x1,x2...), (Y:y1,y2...), (Z:z1,z2...)] to list of tuples (list[x, y, z])
            bonesMarkerList.append(points) #transform from list of tuples to list of lists
            
    bonesMarkerList = list(zip(*bonesMarkerList)) #list of tuples [xyz, xyz, xyz, xyz]

    # Creation of the visualizer window
    visualizer = setVisualizer(12.0)
    
    visualizeSequence(visualizer, bonesMarkerList)
    

def skeletonJointsPlot(data):
  
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

  #create a dictionary[boneName, list of points] from data
  for key, value in data.items(): #key is the bone name in the dictionary
    if 'Marker' not in key: #exclude the markers and get only the bone points
      for key2, value2 in value.items(): 
        if key2 == 'Position':
          points = list(zip(value2['X'], value2['Y'], value2['Z']))
          bonesPosDict[key] = points #create a dictionary[boneName, list of points]
            
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
    
    
