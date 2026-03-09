import launch
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource, AnyLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os
from launch_ros.actions import Node

def generate_launch_description():
	# Path to the camera.launch.xml file
	camera_launch_path = os.path.join(
		FindPackageShare('xraise_bringup').find('xraise_bringup'),
		'launch',
		'camera.launch.xml'
	)


	# Include the camera.launch.xml
	camera_launch = IncludeLaunchDescription(
		AnyLaunchDescriptionSource(camera_launch_path)
	)

	flir_launch_path = os.path.join(
		FindPackageShare('xraise_bringup').find('xraise_bringup'),
		'launch',
		'flir.launch.xml'
	)


	# Include the camera.launch.xml
	flir_launch = IncludeLaunchDescription(
		AnyLaunchDescriptionSource(flir_launch_path)
	)

	# Include the gpsd_client-launch.py
	gpsd_client_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([
			FindPackageShare('gpsd_client').find('gpsd_client'),
			'/launch/gpsd_client-launch.py'
		])
	)

	# Include the lidar.launch.py
	lidar_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([
			FindPackageShare('xraise_bringup').find('xraise_bringup'),
			'/launch/lidar.launch.py'
		])
	)

	topic_list=['/fix','/camera/image_raw/compressed',
			    '/bf/points_raw',
				'/flir/image_raw/compressed',
				'tf',
				'tf_static'
			 	]

	record_execute=launch.actions.ExecuteProcess(
			cmd=['ros2', 'bag', 'record'] + topic_list,
			output='screen'
		)

	return LaunchDescription([
		flir_launch,
                lidar_launch,
		gpsd_client_launch,
		camera_launch,
		record_execute
	])


