import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
import math
import serial

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')
        self.publisher_ = self.create_publisher(Imu, '/imu/data', 10)
        
        self.port = '/dev/ttyACM0'
        self.baud = 115200
        
        try:
            # timeout=0 configura la lectura en modo no bloqueante
            self.ser = serial.Serial(self.port, self.baud, timeout=0)
            self.get_logger().info(f'Puerto {self.port} abierto en modo no bloqueante.')
        except Exception as e:
            self.get_logger().error(f'Error abriendo {self.port}: {e}')
            self.ser = None

        self.buffer = ""
        self.timer = self.create_timer(0.02, self.timer_callback)

    def euler_to_quaternion(self, roll_deg, pitch_deg, yaw_deg):
        roll = math.radians(roll_deg)
        pitch = math.radians(pitch_deg)
        yaw = math.radians(yaw_deg)

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q = Quaternion()
        q.w = cr * cp * cy + sr * sp * sy
        q.x = sr * cp * cy - cr * sp * sy
        q.y = cr * sp * cy + sr * cp * sy
        q.z = cr * cp * sy - sr * sp * cy
        return q

    def timer_callback(self):
        pitch_val = 0.0
        roll_val = 0.0

        if self.ser and self.ser.is_open:
            try:
                # Leer todos los bytes disponibles en el buffer sin bloquear el bucle
                bytes_to_read = self.ser.in_waiting
                if bytes_to_read > 0:
                    raw_data = self.ser.read(bytes_to_read).decode('utf-8', errors='ignore')
                    self.buffer += raw_data
                    
                    # Extraer la última línea completa disponible
                    if '\n' in self.buffer:
                        lines = self.buffer.split('\n')
                        last_line = lines[-2].strip()  # Penúltimo elemento es la última línea completa
                        self.buffer = lines[-1]        # Mantener lo incompleto en el buffer
                        
                        if "Pitch:" in last_line and "Roll:" in last_line:
                            parts = last_line.split(',')
                            pitch_val = float(parts[0].split(':')[1])
                            roll_val = float(parts[1].split(':')[1])
            except Exception as e:
                pass

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'
        msg.orientation = self.euler_to_quaternion(roll_val, pitch_val, 0.0)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()