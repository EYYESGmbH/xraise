#!/usr/bin/python3
import cv2
import numpy as np
import datetime
from rosbags.typesys import Stores, get_typestore
from rosbags.highlevel import AnyReader
from pathlib import Path
import argparse

class FrameCount:
	def __init__(self):
		self.init=False
		self.FPS=0

	def count(self,timestamp_sec):
		if not self.init:
			self.frame_count = 0
			self.start_time = timestamp_sec
			self.init=True
		else:
			self.frame_count += 1
			elapsed_time = timestamp_sec - self.start_time

			if elapsed_time >= 1.0:
				self.FPS=self.frame_count
				self.frame_count = 0
				self.start_time = timestamp_sec

def main():
	parser = argparse.ArgumentParser(description="Display data from a ROS2 bag file.")
	parser.add_argument('ros2_bag', type=str, help="Path to the ROS2 bag.")
	args = parser.parse_args()

	bag_path = args.ros2_bag

	rgb_topic_name = '/camera/image_raw/compressed'  # Replace with your topic name
	oak_left_topic_name = '/oak/Left/image_raw/compressed'  # Replace with your topic name
	oak_right_topic_name = '/oak/Right/image_raw/compressed'  # Replace with your topic name
	gps_topic_name = '/fix'  # Replace with your GPS topic name

	typestore = get_typestore(Stores.ROS2_FOXY)

	gps_msg=None
	image=None

	left_image_valid=False
	right_image_valid=False

	frame_counters = {}

	with AnyReader([Path(bag_path)], default_typestore=typestore) as reader:
		for connection, timestamp, rawdata in reader.messages():

			image=None

			print( connection.msgtype )

			#if connection.topic==rgb_topic_name or connection.topic==oak_left_topic_name or connection.topic==oak_right_topic_name:
			if connection.msgtype == 'sensor_msgs/msg/CompressedImage':
				rgb_msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
				np_arr = np.frombuffer(rgb_msg.data, np.uint8)
				image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
				print(f"Image size: {image.shape[1]}x{image.shape[0]} (Width x Height)")
				print(f"Image data type: {image.dtype}")

				if connection.topic == oak_left_topic_name:
					left_image = image
					left_image_valid = True

				if connection.topic==oak_right_topic_name:
					right_image=image
					right_image_valid=True

			elif connection.topic==gps_topic_name:
				gps_msg=typestore.deserialize_cdr(rawdata, connection.msgtype)
				#print(gps_msg)
			else:
				continue

			if image is not None:
				timestamp_sec = timestamp / 1e9
				datetime_obj = datetime.datetime.fromtimestamp(timestamp_sec)
				timestamp_str = f"Timestamp: {datetime_obj.strftime('%Y-%m-%d %H:%M:%S')}"

				# Find or create a FrameCount object for the current topic
				if connection.topic not in frame_counters:
					frame_counters[connection.topic] = FrameCount()

				frame_counter = frame_counters[connection.topic]
				frame_counter.count(timestamp_sec)

				font = cv2.FONT_HERSHEY_SIMPLEX
				font_scale = 0.5
				color = (0, 255, 0)  # Green color
				thickness = 1
				position = (10, 30)  # Top-left corner

				# Convert timestamp to seconds and overlay it on the image

				cv2.putText(image, timestamp_str, position, font, font_scale, color, thickness, cv2.LINE_AA)
				
				if gps_msg is not None:
					latitude = gps_msg.latitude
					longitude = gps_msg.longitude

					if not np.isnan(longitude) and not np.isnan(latitude):  # Check if long and lat are not NaN
						gps_text = f"GPS: Lat {latitude:.6f}, Lon {longitude:.6f}"
					else:
						gps_text = "GPS: Lat NaN, Lon NaN"
				else:
						gps_text = "GPS: no fix"
					
				gps_position = (10, 50)  # Below the timestamp
				cv2.putText(image, gps_text, gps_position, font, font_scale, color, thickness, cv2.LINE_AA)

				fps_text = f"FPS: {frame_counter.FPS}"
				fps_position = (10, 70)  # Below the GPS text
				cv2.putText(image, fps_text, fps_position, font, font_scale, color, thickness, cv2.LINE_AA)
				
				fixed_width = 640
				scale_ratio = fixed_width / image.shape[1]
				new_height = int(image.shape[0] * scale_ratio)
				image = cv2.resize(image, (fixed_width, new_height), interpolation=cv2.INTER_AREA)

				cv2.imshow(connection.topic, image)

				#if left_image_valid and right_image_valid:
				#	overlay = cv2.addWeighted(left_image, 0.5, right_image, 0.5, 0)
				#	fixed_width = 640
				#	scale_ratio = fixed_width / overlay.shape[1]
				#	new_height = int(overlay.shape[0] * scale_ratio)
			#		overlay = cv2.resize(overlay, (fixed_width, new_height), interpolation=cv2.INTER_AREA)
			#		cv2.imshow("Overlay", overlay)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break

	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()