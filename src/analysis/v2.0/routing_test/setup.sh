IP_SUFFIX=$1

source /opt/ros/jade/setup.bash
export ROS_MASTER_URI=http://192.168.122.4:11311
export ROS_IP=10.1.1.$IP_SUFFIX
export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH
