#!/usr/bin/env python

from launch import LaunchDescription
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import ComposableNodeContainer,Node
import math

def generate_launch_description():

	ld = LaunchDescription()

	lidar = ComposableNodeContainer(
		name="blickfeld_qb2_component",
		namespace="",
		package="rclcpp_components",
		executable="component_container",
		composable_node_descriptions=[
				ComposableNode(
					package="blickfeld_qb2_ros2_driver",
					plugin="blickfeld::ros_interop::Qb2Driver",
					name="blickfeld_qb2_driver",
					parameters=[
						{
							"fqdn": "192.168.0.97",
							"serial_number": "H477OBIAI",
							"application_key": "2e66845e3cc8528dxMvd0gkTHOHcUzpj",
							"frame_id": "lidar",
							"point_cloud_topic": "/bf/points_raw",
							"use_measurement_timestamp": False,
							"publish_intensity": True,
							"publish_point_id": True,
						}
					],
				),
			],
			output="screen",
			)

	tf=Node(
			package="tf2_ros",
			#plugin="tf2_ros::StaticTransformBroadcasterNode",
			executable="static_transform_publisher",
			arguments= ["0","0","1.33",f"{-math.pi/2}",f"{math.pi}","0","world","lidar"],
			output="screen",
	)
    
	ld.add_action(lidar)
	ld.add_action(tf)
    
	return ld
