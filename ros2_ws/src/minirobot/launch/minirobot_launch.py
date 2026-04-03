import launch
import launch.actions
import launch.substitutions
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'run', 'micro_ros_agent', 'micro_ros_agent', 'udp4', '--port', '8888'],
            output='screen',
        ),
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'launch', 'teleop_twist_joy', 'teleop-launch.py', 'joy_config:=xbox'],
            output='screen',
        ),
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'run', 'minirobot', 'minirobot_joy.py'],
            output='screen',
        ),
    ])
