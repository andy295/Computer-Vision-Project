import cv2
import os
import json
import numpy as np
from numpy.linalg import inv
import open3d as o3d
import math
from global_constants import *
from plotter import setVisualizer
from scipy.spatial.transform import Rotation

'''works only with the downloaded frames. Currently we have 0001, 0176, 0263, 0626'''
FRAME_NR_PATH = '0626.jpg'
FRAME_NR = 626
WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (0, 0, 255)
SCALE = 1
BIAS = [0, 0]
SHOW_3D_SKELETON = False
img = cv2.imread(FRAME_IMAGE_PATH + FRAME_NR_PATH)
img = cv2.resize(img, (WIDTH, HEIGHT))


bonesGraph = {
    'pelvis' : ['spine_01', 'thigh_l', 'thigh_r'],
    'spine_01' : ['spine_02'],
    'spine_02' : ['spine_03'],
    'spine_03' : ['spine_04'],
    'spine_04' : ['spine_05'],
    'spine_05' : ['clavicle_l', 'clavicle_r', 'neck_01'],
    'clavicle_l' : ['upperarm_l'],
    'upperarm_l' : ['lowerarm_l', 'upperarm_twist_01_l', 'upperarm_twist_02_l'],
    'lowerarm_l' : ['hand_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l'],
    'hand_l' : ['index_metacarpal_l', 'middle_metacarpal_l', 'pinky_metacarpal_l', 'ring_metacarpal_l', 'thumb_01_l'],
    'clavicle_r' : ['upperarm_r'],
    'upperarm_r' : ['lowerarm_r', 'upperarm_twist_01_r', 'upperarm_twist_02_r'],
    'lowerarm_r' : ['hand_r', 'lowerarm_twist_01_r', 'lowerarm_twist_02_r'],
    'hand_r' : ['index_metacarpal_r', 'middle_metacarpal_r', 'pinky_metacarpal_r', 'ring_metacarpal_r', 'thumb_01_r'],
    'neck_01' : ['neck_02'],
    'neck_02' : ['head'],
    'thigh_l' : ['calf_l', 'thigh_twist_01_l', 'thigh_twist_02_l'],
    'calf_l' : ['calf_twist_01_l', 'calf_twist_02_l', 'foot_l'],
    'foot_l' : ['ball_l', 'ankle_bck_l', 'ankle_fwd_l'],
    'thigh_r' : ['calf_r', 'thigh_twist_01_r', 'thigh_twist_02_r'],
    'calf_r' : ['calf_twist_01_r', 'calf_twist_02_r', 'foot_r'],
    'foot_r' : ['ball_r', 'ankle_bck_r', 'ankle_fwd_r']
}

# unnecessary bones removed for clarity of the projection
bones_to_remove = ['root', 'center_of_mass', 'ik_foot_root', 'ik_hand_root', 'interaction', 'ik_hand_gun', 'ik_hand_l', 'ik_hand_r', 'ik_foot_l', 'ik_foot_r',
                'clavicle_out_l', 'clavicle_scap_l',
                'index_01_l', 'index_02_l', 'index_03_l', 
                'middle_01_l', 'middle_02_l', 'middle_03_l', 
                'pinky_01_l', 'pinky_02_l', 'pinky_03_l', 
                'ring_01_l', 'ring_02_l', 'ring_03_l', 
                'thumb_02_l', 'thumb_03_l', 
                'weapon_l', 'wrist_inner_l', 'wrist_outer_l',
                'lowerarm_correctiveRoot_l', 'lowerarm_bck_l', 'lowerarm_fwd_l','lowerarm_in_l', 'lowerarm_out_l', 
                'upperarm_correctiveRoot_l', 'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_in_l', 'upperarm_out_l',
                'upperarm_twistCor_01_l', 'upperarm_bicep_l', 'upperarm_tricep_l', 'upperarm_twistCor_02_l',
                'clavicle_pec_l', 'clavicle_pec_r', 
                'clavicle_out_r', 'clavicle_scap_r',
                'index_01_r', 'index_02_r', 'index_03_r', 
                'middle_01_r', 'middle_02_r', 'middle_03_r',
                'pinky_01_r', 'pinky_02_r', 'pinky_03_r', 
                'ring_01_r', 'ring_02_r', 'ring_03_r', 
                'thumb_02_r', 'thumb_03_r',
                'weapon_r', 'wrist_inner_r', 'wrist_outer_r',
                'lowerarm_correctiveRoot_r', 'lowerarm_bck_r', 'lowerarm_fwd_r', 'lowerarm_in_r', 'lowerarm_out_r',
                'upperarm_correctiveRoot_r', 'upperarm_bck_r', 'upperarm_fwd_r', 'upperarm_in_r', 'upperarm_out_r',
                'upperarm_twistCor_01_r', 'upperarm_bicep_r', 'upperarm_tricep_r', 'upperarm_twistCor_02_r',
                'spine_04_latissimus_l', 'spine_04_latissimus_r', 
                'calf_correctiveRoot_l', 'calf_kneeBack_l', 'calf_knee_l','calf_twistCor_02_l', 
                'thigh_correctiveRoot_l', 'thigh_bck_l', 'thigh_bck_lwr_l', 'thigh_fwd_l', 'thigh_fwd_lwr_l', 'thigh_in_l', 'thigh_out_l',
                'thigh_twistCor_01_l', 'thigh_twistCor_02_l', 
                'calf_correctiveRoot_r', 'calf_kneeBack_r', 'calf_knee_r', 'calf_twistCor_02_r',
                'thigh_correctiveRoot_r', 'thigh_bck_r', 'thigh_bck_lwr_r', 'thigh_fwd_r', 'thigh_fwd_lwr_r', 'thigh_in_r', 'thigh_out_r',
                'thigh_twistCor_01_r', 'thigh_twistCor_02_r']

class SkeletonData:
    def __init__(self, coordinates, id):
        self.coordinates = coordinates
        self.id = id

    def __repr__(self):
        return f"SkeletonData(id={self.id}, coordinates={self.coordinates})"

# convert a rotation matrix to a rotation vector and a translation vector 
def matrix_to_rot_vec(matrix):
    # Rodriguez convert a rotation matrix to a rotation vector
    rotation_vector, _ = cv2.Rodrigues(matrix[:3, :3])
    translation_vector = matrix[:3, 3]
    return rotation_vector.squeeze(), translation_vector

# convert a rotation vector and a translation vector to a rotation matrix
def rot_vec_to_matrix(rotation_vector, translation_vector):
    # Rodriguez convert a rotation vector to rotation a rotation matrix
    T = np.eye(4)
    R, _ = cv2.Rodrigues(rotation_vector)
    T[:3, :3] = R
    T[:3, 3] = translation_vector.squeeze()
    return T

# convert a left handed coordinate system (UE5) to a right handed coordinate system (cv2)
def left_to_right_handed (quat, translation_vector):
    # Left handed (Unreal Enginge) :  (+X: forward, +Y: right, +Z: up) 
    # Right handed (openCV) : (+X: right, +Y: down, +Z: forward)
    rotation_vector = Rotation.from_quat(quat).as_rotvec()
    mat = rot_vec_to_matrix(rotation_vector, translation_vector)

    C = np.array([
        [0,  1,   0, 0],
        [0,  0,  -1, 0],
        [1,  0,   0, 0],
        [0,  0,   0, 1]
    ], dtype=np.float32)
    
    # Apply transformation
    mat = C @ mat @ inv(C)
    
    rotation_vector, translation_vector = matrix_to_rot_vec(mat)
    quat = Rotation.from_rotvec(rotation_vector).as_quat()

    return quat, translation_vector

# Read the JSON data from the file and save them in a list of SkeletonData objects
def get_all_skeleton_frames(bones_to_remove):

    try:
        with open(ACTOR_DATA_PATH, 'r') as file:
            actor_data = json.load(file)
    except FileNotFoundError:
        print(f"File 1: {ACTOR_DATA_PATH}")
        exit(1)

    all_frames_skeleton_position = []
    for frame in actor_data.get('actor_data', []):
        skeleton = frame.get('skeleton')
        frame = frame.get('frameNr')
        bones = []
        if skeleton is not None and frame is not None:
            skeleton_frame = []
            for bone in skeleton:
                if bone.get('name') is not None and bone.get('name') != 'None' and bone.get('location') is not None:
                    skeleton_bone = SkeletonData(bone.get('location'), bone.get('name'))
                    skeleton_frame.append(skeleton_bone)
                    bones.append(bone.get('name'))
            skeleton_frame = SkeletonData(skeleton_frame, frame)
            all_frames_skeleton_position.append(skeleton_frame)

    # remove the non necessary bones
    del all_frames_skeleton_position[0]
    for i in range(len(all_frames_skeleton_position)):
        frame = all_frames_skeleton_position[i]
        useful_bones = [bone for bone in frame.coordinates if bone.id not in bones_to_remove]
        all_frames_skeleton_position[i] = SkeletonData(useful_bones, frame.id)

    bones = [bone for bone in bones if bone not in bones_to_remove]

    return all_frames_skeleton_position, bones

# Create a map of lines between the bones points
def create_lines_map(bonesGraph, bones):
    lines=[]
    for key, values in bonesGraph.items():
        keyIndex = bones.index(key)
        for value in values:
            valueIndex = bones.index(value)
            lines.append([keyIndex, valueIndex])
    return lines

# visualize the 3D skeleton of one chosen frame
def visualize_skeleton(listOfPoints, lines):

    visualizer = setVisualizer(8.0)
    lineSet = o3d.geometry.LineSet()
    lineSet.lines = o3d.utility.Vector2iVector(lines)
    lineColor = [1, 0, 0]
    lineSet.colors = o3d.utility.Vector3dVector(np.tile(lineColor, (len(lines), 1)))
    
    visualizer.clear_geometries()
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(listOfPoints)
    lineSet.points = o3d.utility.Vector3dVector(listOfPoints)
    visualizer.add_geometry(pcd)
    visualizer.add_geometry(lineSet)
    visualizer.update_geometry(pcd)
    visualizer.update_geometry(lineSet)
    visualizer.poll_events()
    visualizer.update_renderer()
    visualizer.run()
    visualizer.destroy_window()


all_frames_skeleton_position, bones = get_all_skeleton_frames(bones_to_remove)

# get the 3D points of one chosen frame
listOfPoints = [[point.coordinates[X], point.coordinates[Y], point.coordinates[Z]] 
                for point in all_frames_skeleton_position[FRAME_NR].coordinates]
listOfPoints = np.array(listOfPoints)

# convert the skeleton bone points to right handed coordinate system for the chosen frame
for i, point in enumerate(listOfPoints):
        _ , listOfPoints[i] = left_to_right_handed(np.array((0,0,0,1)), point)

lines = create_lines_map(bonesGraph, bones)

if SHOW_3D_SKELETON:
    visualize_skeleton(listOfPoints, lines)

# Get camera data from the json file
try:
    with open(CAMERA_DATA_PATH, 'r') as file:
        camera_data = json.load(file)
except FileNotFoundError:
        print(f"File 1: {CAMERA_DATA_PATH}")
        exit(1)
fov = camera_data['field_of_view']
aspect_ratio = camera_data['aspect_ratio']
rotation_quaternion = np.deg2rad(np.array([camera_data['world_rotation']['x'],
                            camera_data['world_rotation']['y'],
                            camera_data['world_rotation']['z'],
                            camera_data['world_rotation']['w']]))
translation_vector = np.array([camera_data['world_location']['x'],
                            camera_data['world_location']['y'],
                            camera_data['world_location']['z']])
# convert the camera data to right handed coordinate system
rotation_quaternion, translation_vector = left_to_right_handed(rotation_quaternion, translation_vector)
rotation_vector = Rotation.from_quat(rotation_quaternion).as_rotvec()

# defining the camera matrix
fov_rad = math.radians(fov)
fx = (WIDTH / 2) / math.tan(fov_rad / 2)
fy = (HEIGHT / 2) / math.tan((fov_rad / 2) / aspect_ratio)
cx = WIDTH / 2
cy = HEIGHT / 2
camera_matrix = np.array([[fx, 0, cx], 
                          [0, fy, cy], 
                          [0, 0, 1]], np.float32)

# Map the 3D point to 2D point  
T_cam_world = rot_vec_to_matrix(rotation_vector, translation_vector)
rotation_vector, translation_vector = matrix_to_rot_vec(inv(T_cam_world)) 
distortion_coeffs = np.zeros((5, 1), np.float32) # Define the distortion coefficients as 0,0,0,0,0 since we assume no distortion
projected_points, _ = cv2.projectPoints(listOfPoints, rotation_vector, translation_vector, camera_matrix, distortion_coeffs) 
if img is None:
    print("Image not read")
    exit(1)
# SCALE and BIAS are used to adjust the skeleton size and position if needed 
for point in projected_points: 
    x = (int(point[0][0]*SCALE + (BIAS[0])))
    y = (int(point[0][1]*SCALE +int(BIAS[1])))
    # draw bones points on the image
    img = cv2.circle(img, (x, y), 5, RED, -1) 
# draw lines between the bones points on the image
for line in lines:
    start_point = projected_points[line[0]].astype(int)
    end_point = projected_points[line[1]]. astype(int)
    start_point = (int(start_point[0][0] * SCALE + BIAS[0]), int(start_point[0][1] * SCALE + BIAS[1]))
    end_point = (int(end_point[0][0] * SCALE + BIAS[0]), int(end_point[0][1] * SCALE + BIAS[1]))
    cv2.line(img, start_point, end_point, BLACK, 2)
  
cv2.imshow('Image', img) 
cv2.waitKey(0) 
cv2.destroyAllWindows()
