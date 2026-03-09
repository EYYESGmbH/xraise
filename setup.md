Working with ROS
================

Network setup:
------------------

***Axis Camera:***  
Fixed IP set to: 192.168.0.90

***FLIR Camera:***  
Gets the IP address 192.168.0.96 from the DHCP server on the server   



***Blickfeld LIDAR:***  
Gets the IP address 192.168.0.97 from the DHCP server on the server   

If the ethernet address of the LIDAR or FLIR camera changes, the file /etc/dhcp/dhcpd.conf needs to be updated

ROS sensor recording
--------------------

Xraise ROS package content:

Package name: xraise_bringup

Launch files:
* **camera.launch.xml**: Launches a camera node that publishes the stream of an Axis camera to /camera/image_raw...
* **flir.launch.py**: Launches a camera node that publishes the stream of the FLIR camera to /flir/image_raw...
* **lidar.launch.py**: Launches a camera node that publishes the stream of the LIDAR to /bf/points_raw
* **recorder.launch.py**: Launches the camera node, the gpsd_client and records the following topics:  
	* /fix
	* /camera/image_raw/compressed  
	* /flir/image_raw/compressed
	* /bf/points_raw
	* /tf
	* /tf_static

To start the recording: 

```
cd /mnt2 #target dirctroy for the recording
ros2 launch xraise recorder.launch.py
```

Recording can be stopped with Ctrl-C

The tool ```rqt```can be used to monitor the images (RGB and thermal) published in ROS.

The tool ```rviz2```can be used to visualize the 3D pointcloud

Viewing a recorder ROS bag:
---------------------------

The script show.py gives an example how to read and display the information stored in a ROS bag.

Call:
```~/xraise/scripts/show.py /mnt2/rosbag_xyz```

The ROS bag play command can be used to show a recorded pointcloud:

```ros2 bag play /mnt2/rosbag_xyz```

During the playback, ```rviz2``` and ```rqt```can be used to display the pointcloud and the images


Install Instructions
====================

Base system: Jetson Jetpack 5.1.1, Ubuntu 20.04

Prepare ROS installation
------------------------

```
locale  # check for UTF-8
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale  # verify settings
```

Install dependencies
--------------------
 
```
sudo apt install isc-dhcp-server  gpsd-clients gpsd curl ntp pip
```

Tool to convert readme.md to pdf - if required:

```
sudo apt install  pandoc texlive-latex-base texlive-fonts-recommended texlive-extra-utils\
  texlive-latex-extra
```

or use: https://www.pdfforge.org/online/de/markdown-in-pdf

Install ROS
--------------------

```
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee \
  /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update

sudo apt install ros-foxy-desktop ros-foxy-gscam  ros-foxy-ament-cmake \ python3-colcon-common-extensions\
  ros-foxy-image-transport-plugins ros-foxy-gpsd-client ros-foxy-gps-tools ros-foxy-joint-state-publisher-gui \
  ros-foxy-rqt-image-view
``` 

Clone xraise repo:   
-------------------------

Clone the xraise repo to: ~/xraise   

The following commands are relative to the xraise - directory.


Setup DHCP and GPS
------------------

***Network setup:***  

Realteck Ethernet (LAN):   
eth0, Upstream Port, set to DHCP

Intel Ehternet (POEx):   
eth1, 4x POE Ports, set to static IP 192.168.0.1   
DHCP Server enabled

***Set network settings on Realtek Ethernet:***   
Settings->Network
IPv4 Method: Manual   
Address: 192.168.0.1  
Netmask: 255.255.255.0  

***Configure DHCP***

Check the MAC addresses of the FLIR camera and the Lidar in the ./setup/dhcpd.conf file

Remark: The default service file isc-dhcp-server.service does not start correctly because of a wrong start order in combination with the NetworkManager, so a modified file dhcp.service is used.

```
sudo cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.bak && sudo cp ./setup/dhcpd.conf /etc/dhcp/dhcpd.conf

sudo cp /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.bak && \ 
sudo cp ./setup/isc-dhcp-server /etc/default/isc-dhcp-server

sudo cp ./setup/dhcp.service /etc/systemd/system

sudo systemctl enable NetworkManager-wait-online.service
sudo systemctl enable dhcp.service
sudo systemctl start dhcp.service
```

***Configure GPSD***

```
sudo cp ./setup/gpsd /etc/default/gpsd
sudo systemctl enable gpsd.service && sudo systemctl restart gpsd.service
```

The tool ```cgps``` can be used to check GPS reception.

***Configure NTP***

Enable GPS as ntp time source:

```
sudo sh -c 'cat ./setup/ntp.cat >> /etc/ntp.conf'
sudo systemctl enable ntp.service && sudo systemctl restart ntp.service
sudo cp ./setup/datefromgps /etc/cron.d
```

When the time offset is to big, ntpd seems to not update from gps - therefor run a script from cron to do it manually.

```
sudo cp ./setup/datefromgps /etc/cron.d
```

Setup Blickfeld ROS driver dependencies
------------------------------------------

```
sudo apt install ros-foxy-diagnostic-updater libgrpc++-dev protobuf-compiler-grpc \
  libprotobuf-dev
```


Setup ROS workspace
-------------------

Append the following lines to ~/.bashrc:
```
source /opt/ros/foxy/setup.bash
source ~/ros2_ws/install/setup.bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash 
```

```
cd ~
cp -r ./xraise/ros2_ws ~
source ~/.bashrc
cd ~/ros2_ws
colcon build
source ~/.bashrc
```
Ros2_ws contains a copy of the Blickfeld ROS driver from https://github.com/Blickfeld/blickfeld_qb2_ros2_driver (Tag: v2.1.0).  
To compile this driver, internet connection is required.


See https://github.com/Blickfeld/blickfeld_qb2_ros2_driver/blob/main/doc/modules/ROOT/pages/index.adoc for details.

Install Python libraries:
```
pip install rosbags
```


