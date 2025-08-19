# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.sensors.sensor import Sensor

hull_angle = Sensor(
    "hull_angle_walker_2", "Hull Angle", lambda sensors: sensors["walker_2"][0]
)
hull_velocity = Sensor(
    "hull_velocity_walker_2",
    "Hull Angular Velocity",
    lambda sensors: sensors["walker_2"][1],
)
x_vel = Sensor("x_vel_walker_2", "X Velocity", lambda sensors: sensors["walker_2"][2])
y_vel = Sensor("y_vel_walker_2", "Y Velocity", lambda sensors: sensors["walker_2"][3])
hip_joint_1_angle = Sensor(
    "hip_joint_1_angle_walker_2",
    "Hip Joint 1 Angle",
    lambda sensors: sensors["walker_2"][4],
)
hip_joint_1_velocity = Sensor(
    "hip_joint_1_velocity_walker_2",
    "Hip Joint 1 Velocity",
    lambda sensors: sensors["walker_2"][5],
)
knee_joint_1_angle = Sensor(
    "knee_joint_1_angle_walker_2",
    "Knee Joint 1 Angle",
    lambda sensors: sensors["walker_2"][6],
)
knee_joint_1_velocity = Sensor(
    "knee_joint_1_velocity_walker_2",
    "Knee Joint 1 Velocity",
    lambda sensors: sensors["walker_2"][7],
)
leg_1_ground_contact = Sensor(
    "leg_1_ground_contact_walker_2",
    "Leg 1 Ground Contact",
    lambda sensors: sensors["walker_2"][8],
)
hip_joint_1_angle_2 = Sensor(
    "hip_joint_1_angle_walker_2",
    "Hip Joint 1 Angle",
    lambda sensors: sensors["walker_2"][9],
)
hip_joint_1_velocity_2 = Sensor(
    "hip_joint_1_velocity_walker_2",
    "Hip Joint 1 Velocity",
    lambda sensors: sensors["walker_2"][10],
)
knee_joint_1_angle_2 = Sensor(
    "knee_joint_1_angle_walker_2",
    "Knee Joint 1 Angle",
    lambda sensors: sensors["walker_2"][11],
)
knee_joint_1_velocity_2 = Sensor(
    "knee_joint_1_velocity_walker_2",
    "Knee Joint 1 Velocity",
    lambda sensors: sensors["walker_2"][12],
)
leg_1_ground_contact_2 = Sensor(
    "leg_1_ground_contact_walker_2",
    "Leg 1 Ground Contact",
    lambda sensors: sensors["walker_2"][13],
)
lidar_1 = Sensor("lidar_1_walker_2", "Lidar 1", lambda sensors: sensors["walker_2"][14])
lidar_2 = Sensor("lidar_2_walker_2", "Lidar 2", lambda sensors: sensors["walker_2"][15])
lidar_3 = Sensor("lidar_3_walker_2", "Lidar 3", lambda sensors: sensors["walker_2"][16])
lidar_4 = Sensor("lidar_4_walker_2", "Lidar 4", lambda sensors: sensors["walker_2"][17])
lidar_5 = Sensor("lidar_5_walker_2", "Lidar 5", lambda sensors: sensors["walker_2"][18])
lidar_6 = Sensor("lidar_6_walker_2", "Lidar 6", lambda sensors: sensors["walker_2"][19])
lidar_7 = Sensor("lidar_7_walker_2", "Lidar 7", lambda sensors: sensors["walker_2"][20])
lidar_8 = Sensor("lidar_8_walker_2", "Lidar 8", lambda sensors: sensors["walker_2"][21])
lidar_9 = Sensor("lidar_9_walker_2", "Lidar 9", lambda sensors: sensors["walker_2"][22])
lidar_10 = Sensor(
    "lidar_10_walker_2", "Lidar 10", lambda sensors: sensors["walker_2"][23]
)
left_neighbor_relative_x = Sensor(
    "left_neighbor_relative_x_walker_2",
    "Left Neighbor Relative X",
    lambda sensors: sensors["walker_2"][24],
)
left_neighbor_relative_y = Sensor(
    "left_neighbor_relative_y_walker_2",
    "Left Neighbor Relative Y",
    lambda sensors: sensors["walker_2"][25],
)
right_neighbor_relative_x = Sensor(
    "right_neighbor_relative_x_walker_2",
    "Right Neighbor Relative X",
    lambda sensors: sensors["walker_2"][26],
)
right_neighbor_relative_y = Sensor(
    "right_neighbor_relative_y_walker_2",
    "Right Neighbor Relative Y",
    lambda sensors: sensors["walker_2"][27],
)
walker_pos_relative_x = Sensor(
    "walker_pos_relative_x_walker_2",
    "Walker Pos Relative X",
    lambda sensors: sensors["walker_2"][28],
)
walker_pos_relative_y = Sensor(
    "walker_pos_relative_y_walker_2",
    "Walker Pos Relative Y",
    lambda sensors: sensors["walker_2"][29],
)
package_angle = Sensor(
    "package_angle_walker_2", "Package Angle", lambda sensors: sensors["walker_2"][30]
)

sensors_walker_2 = [
    hull_angle,
    hull_velocity,
    x_vel,
    y_vel,
    hip_joint_1_angle,
    hip_joint_1_velocity,
    knee_joint_1_angle,
    knee_joint_1_velocity,
    leg_1_ground_contact,
    hip_joint_1_angle_2,
    hip_joint_1_velocity_2,
    knee_joint_1_angle_2,
    knee_joint_1_velocity_2,
    leg_1_ground_contact_2,
    lidar_1,
    lidar_2,
    lidar_3,
    lidar_4,
    lidar_5,
    lidar_6,
    lidar_7,
    lidar_8,
    lidar_9,
    lidar_10,
    left_neighbor_relative_x,
    left_neighbor_relative_y,
    right_neighbor_relative_x,
    right_neighbor_relative_y,
    walker_pos_relative_x,
    walker_pos_relative_y,
    package_angle,
]
