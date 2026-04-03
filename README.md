# ROS 2 workspace: minirobot

This workspace brings together a small differential-drive robot controlled by an **ESP32** running **micro-ROS**, a **micro-ROS Agent** on the host, and **joystick teleoperation** on the PC. The main custom package is **`minirobot`**, which bridges an Xbox-style gamepad to LED patterns, servo position, and (together with `teleop_twist_joy`) motion commands the firmware understands.

---

## What’s in this repository

| Path | Role |
|------|------|
| `src/minirobot` | Custom ament package: C++ sample node, Python joy bridge, launch file, ESP32 Arduino sketch |
| `src/micro-ROS-Agent` | micro-ROS Agent (used over **UDP**, port **8888** in the default launch) |
| `src/teleop_twist_joy` | Publishes `geometry_msgs/Twist` on `/cmd_vel` from `/joy` (configurable) |

The ESP32 firmware lives under:

`src/minirobot/esp32_microros/minirobot_esp32_microros/minirobot_esp32_microros.ino`

---

## Prerequisites

- **ROS 2** (e.g. Rolling, Humble, or Jazzy—adjust paths and `source` commands for your distro).
- **colcon** and ament build tools.
- **Python 3** with `rclpy` (pulled in with your ROS install).
- **Joystick / gamepad** supported by Linux (or your OS) so `joy_node` can publish `/joy`.
- For the robot: **ESP32** with the **micro-ROS Arduino** support and libraries used in the sketch (`micro_ros_arduino`, `ESP32Servo`, etc.).

Clone or place dependent repos under `src/` as you already have, then build from the workspace root.

---

## Build

From the workspace root (the directory that contains `src/`):

```bash
source /opt/ros/<DISTRO>/setup.bash   # e.g. rolling, humble
cd /path/to/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Rebuild after changing `package.xml`, `CMakeLists.txt`, or adding launch/scripts.

---

## Run (recommended: full stack)

The launch file starts three processes:

1. **micro-ROS Agent** — `udp4` on port **8888** (must match the ESP32 transport settings).
2. **teleop_twist_joy** — Xbox config: `joy_config:=xbox`.
3. **minirobot_joy** — Python node that maps buttons/axes to `/LEDs` and `/servo`.

```bash
source install/setup.bash
ros2 launch minirobot minirobot_launch.py
```

**Before driving:** power the ESP32, ensure it is flashed with firmware that connects to the same network and agent **IP/port** as configured in the sketch (see below). The agent must be reachable from the ESP32 at the address you set in `set_microros_wifi_transports(...)`.

### Other useful commands

- Run only the joy bridge (agent and teleop already running elsewhere):

  ```bash
  ros2 run minirobot minirobot_joy.py
  ```

- Run the small C++ demo executable:

  ```bash
  ros2 run minirobot minirobot_info
  ```

---

## ESP32 firmware (micro-ROS)

1. Open `minirobot_esp32_microros.ino` in the **Arduino IDE** (or your preferred flow) with **micro-ROS for ESP32** set up per the official micro-ROS Arduino documentation.
2. **Edit Wi-Fi and agent settings** in `setup()` — the sketch uses `set_microros_wifi_transports(ssid, password, agent_ip, port)`. Use your LAN SSID/password and the **host IP** where `micro_ros_agent` is listening (port **8888** matches the default launch).
3. Flash the ESP32. On boot, the node name is **`minirobot_esp32`**.

> **Security:** Do not commit real Wi-Fi passwords or fixed production IPs. Use a local `secrets.h` or environment-specific branches if you share the repo.

### Hardware assumptions (from firmware)

- **Motors:** H-bridge pins `IN1`–`IN4` (see `#define` values in the sketch).
- **Encoders:** Left/right quadrature on the pins defined as `LeftEncoder_*` / `RightEncoder_*`.
- **LEDs:** Two GPIOs for left/right indicators.
- **Servo:** PWM on the configured pin (see `servoPin` in the sketch).
- **Battery:** Analog input on `BATTERY_PIN` with scaling in `map_to_percentage()`—tune `min_voltage` / `max_voltage` for your pack and divider.

---

## ROS interfaces

### Subscriptions (ESP32 → listens on micro-ROS)

| Topic | Type | Purpose |
|-------|------|---------|
| `LEDs` | `std_msgs/Int8` | LED pattern: `0`–`3` (all off, left, right, both) |
| `/servo` | `std_msgs/Int8` | Servo angle (clamped in firmware) |
| `cmd_vel` | `geometry_msgs/Twist` | Differential drive from `linear.x` and `angular.z` |

### Publishers (ESP32 → micro-ROS)

| Topic | Type | Purpose |
|-------|------|---------|
| `battery` | `std_msgs/Int8` | Estimated battery percentage |
| `left_motor_ticks` | `std_msgs/Int32` | Encoder tick count (left, sign adjusted in timer) |
| `right_motor_ticks` | `std_msgs/Int32` | Encoder tick count (right) |

Exact graph names may include namespaces depending on micro-ROS and your agent; use `ros2 topic list` while the robot is connected.

### `minirobot_joy` behavior (Xbox-style mapping)

- **Buttons 0–3** (A/B/X/Y): publish `Int8` on **`/LEDs`** with values `0`–`3`.
- **Axes 6 and 7** (typical D-pad on many mappings): bump servo or set to endpoints; publishes **`/servo`** as `std_msgs/Int8` (0–45 range on the PC side, firmware limits further).

If your gamepad differs, change `teleop_twist_joy` config or adjust axis/button indices in `minirobot/scripts/minirobot_joy.py`.

---

## Package: `minirobot` (overview)

- **`minirobot_info`** — Minimal C++ node (useful as a build sanity check).
- **`minirobot_joy.py`** — Subscribes to `/joy`, publishes `/LEDs` and `/servo`.
- **`minirobot_launch.py`** — Agent + teleop + joy bridge.
- **Python package** `minirobot/` — Empty module package to satisfy `ament_python_install_package`.

License for the package is **Apache-2.0** (see `src/minirobot/LICENSE`).

---

## Troubleshooting

| Symptom | Things to check |
|---------|------------------|
| ESP32 never joins ROS graph | Wi-Fi credentials, firewall, agent IP/port, same LAN as the PC |
| No `/joy` | Device permissions (`input` group on Linux), correct `joy_config`, cable/BT connection |
| Robot doesn’t move | `teleop_twist_joy` running, `/cmd_vel` echoed, motor wiring and sketch `cmd_vel` subscription |
| LEDs/servo ignore gamepad | `minirobot_joy` running, topic names `/LEDs` vs `LEDs` (micro-ROS may remap—verify with `ros2 topic list` / `ros2 topic echo`) |

Use `ros2 node list`, `ros2 topic list`, and `ros2 topic echo <topic>` with the workspace sourced to debug live.

---

## Maintainer

Package metadata lists **akshath** as maintainer; update `package.xml` when ownership or contact details change.
