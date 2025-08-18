import socket
import struct
import time
import math

# ========================
# Configurable Robot Params
# ========================
robot_ip   = "198.162.1.11"
send_port  = 30001
recv_port  = 30003

def configure_robot(ip: str, send: int = 30001, recv: int = 30003):
    """Configure robot connection parameters."""
    global robot_ip, send_port, recv_port
    robot_ip = ip
    send_port = send
    recv_port = recv


# ========================
# Helper: Send URScript
# ========================
def send_urscript(script: str, wait: float = 0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, send_port))
    s.send(script.encode("utf-8"))
    time.sleep(wait)
    s.close()


# ========================
# State Functions
# ========================
def getpose():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, recv_port))
    data = s.recv(1108)
    s.close()
    pose = struct.unpack("!6d", data[444:492])
    x, y, z, rx, ry, rz = pose
    return (x*1000, y*1000, z*1000,
            math.degrees(rx), math.degrees(ry), math.degrees(rz))


def getjoints():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, recv_port))
    data = s.recv(1108)
    s.close()
    joints = struct.unpack("!6d", data[252:300])
    return tuple(math.degrees(j) for j in joints)


def get_tcp_speed():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((robot_ip, recv_port))
    data = s.recv(1108)
    s.close()
    tcp_speed = struct.unpack("!6d", data[492:540])
    vx, vy, vz, rx, ry, rz = tcp_speed
    speed_norm = (vx**2 + vy**2 + vz**2) ** 0.5
    return tcp_speed, speed_norm


def wait_until_stopped():
    while True:
        _, speed_norm = get_tcp_speed()
        if speed_norm < 0.0001:
            break
        time.sleep(0.02)


# ========================
# Motion Functions
# ========================
def moveLoffset(dx, dy, dz, rx=0, ry=0, rz=0, speed=0.1):
    rx_rad, ry_rad, rz_rad = map(math.radians, [rx, ry, rz])
    urscript = f"""
    movel(pose_trans(get_actual_tcp_pose(), p[{dx/1000}, {dy/1000}, {dz/1000}, {rx_rad}, {ry_rad}, {rz_rad}]), a={speed}, v={speed})
    """
    send_urscript(urscript)
    time.sleep(0.3)
    wait_until_stopped()


def moveJoffset(dx, dy, dz, rx=0, ry=0, rz=0, speed=0.1):
    rx_rad, ry_rad, rz_rad = map(math.radians, [rx, ry, rz])
    urscript = f"""
    movej(pose_trans(get_actual_tcp_pose(), p[{dx/1000}, {dy/1000}, {dz/1000}, {rx_rad}, {ry_rad}, {rz_rad}]), a={speed}, v={speed})
    """
    send_urscript(urscript)
    time.sleep(0.3)
    wait_until_stopped()


def moveL(x, y, z, rx=0, ry=3.14, rz=0, speed=0.1):
    rx_rad, ry_rad, rz_rad = map(math.radians, [rx, ry, rz])
    urscript = f"""
    movel(p[{x/1000}, {y/1000}, {z/1000}, {rx_rad}, {ry_rad}, {rz_rad}], a={speed}, v={speed})
    """
    send_urscript(urscript)
    time.sleep(0.3)
    wait_until_stopped()


def moveJ(x, y, z, rx=0, ry=3.14, rz=0, speed=0.1):
    rx_rad, ry_rad, rz_rad = map(math.radians, [rx, ry, rz])
    urscript = f"""
    movej(p[{x/1000}, {y/1000}, {z/1000}, {rx_rad}, {ry_rad}, {rz_rad}], a={speed}, v={speed})
    """
    send_urscript(urscript)
    time.sleep(0.3)
    wait_until_stopped()


# ========================
# IO Functions
# ========================
def digitalout(pin, value):
    val = "True" if value else "False"
    send_urscript(f"set_digital_out({pin}, {val})\n")

def digitalin(pin):
    send_urscript(f"get_digital_in({pin})\n")

def analogout(pin, value):
    send_urscript(f"set_analog_out({pin}, {value})\n")

def analogin(pin):
    send_urscript(f"get_analog_in({pin})\n")


# ========================
# Joint Functions
# ========================
def jointangle(joint_number: int):
    joints = getjoints()
    if 1 <= joint_number <= 6:
        return joints[joint_number - 1]
    raise ValueError("Joint number must be 1–6")

def jointupdate(joint_number: int, angle_desired: float, speed: float = 0.5):
    current_joints = list(getjoints())
    if 1 <= joint_number <= 6:
        current_joints[joint_number - 1] = angle_desired
    else:
        raise ValueError("Joint number must be 1–6")
    joints_rad = [math.radians(j) for j in current_joints]
    urscript = f"movej([{', '.join(str(j) for j in joints_rad)}], a={speed}, v={speed})"
    send_urscript(urscript)
    time.sleep(0.3)
    wait_until_stopped()
