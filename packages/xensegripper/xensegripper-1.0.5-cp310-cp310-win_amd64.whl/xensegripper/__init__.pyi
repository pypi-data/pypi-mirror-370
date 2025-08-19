from typing import Union
from abc import ABC, abstractmethod

class XenseGripper(ABC):
    @abstractmethod
    def set_position(self, position: float, vmax: float , fmax: float):
        pass

    @abstractmethod
    def get_gripper_status(self) -> dict:
        pass
    
    @classmethod
    def create(cls, mac_addr=None, **kwargs) -> Union["XenseTCPGripper", "XenseSerialGripper"]:
        """
        创建一个 XenseGripper 实例，自动选择通信方式（串口或 TCP/IP）

        根据传入参数自动决定使用串口实现（`XenseSerialGripper`）或
        网络实现（`XenseTCPGripper`）创建一个夹爪实例。

        Args:
            mac_addr (str, optional): 如果提供 IP 地址，则使用 TCP 连接到远程夹爪。
                                        否则使用本地串口连接。
            **kwargs: 额外参数（如 `port`），仅在串口连接时使用。

        Returns:
            XenseGripper: 实现 `Gripper` 接口的夹爪实例，具体为串口或 TCP 实现。
        """

class XenseSerialGripper(XenseGripper):
    """
    Direct communication with gripper
    """
    def set_position(self, position, vmax=80.0, fmax=27.0):
        """
        Set the target position of the Gripper.

        Args:
            position (float): Target position of the gripper in millimeters (mm). 
                              Must be in the range (0, 85). 
                              0 mm means fully open, 85 mm means fully closed.
            vmax (float, optional): Maximum speed of motion in mm/s. 
                                    Must be in the range (0, 200). 
                                    Default is 80 mm/s.
            fmax (float, optional): Maximum output force in Newtons (N). 
                                    Must be in the range (0, 40). 
                                    Default is 27 N.

        Raises:
            ValueError: If any of the input arguments are outside their allowed physical limits.

        """

    def get_gripper_status(self) -> dict:
        """Retrieve the gripper status, including motor temperature, output force, speed, and position.

        Returns:
            dict: gripper status including: position, velocity, force and temperature 
        """
    
    
class XenseTCPGripper(XenseGripper):
    """
    Direct communication with gripper
    """
    
    def set_position(self, position, vmax=80.0, fmax=27.0):
        """
        Set the target position of the Gripper.

        Args:
            position (float): Target position of the gripper in millimeters (mm). 
                              Must be in the range (0, 85). 
                              85 mm means fully open, 0 mm means fully closed.
            vmax (float, optional): Maximum speed of motion in mm/s. 
                                    Must be in the range (0, 200). 
                                    Default is 80 mm/s.
            fmax (float, optional): Maximum output force in Newtons (N). 
                                    Must be in the range (0, 40). 
                                    Default is 27 N.

        Raises:
            ValueError: If any of the input arguments are outside their allowed physical limits.

        """
        

    def get_gripper_status(self) -> dict:
        """
        Read status from gripper

        Returns:
        - dict, {position, velocity, force, temperature}
        """

    def open_gripper(self):
        """
        Open Gripper with default v and f.
        """

    def close_gripper(self):
        """
        Close Gripper with default v and f.
        """
    
    def set_led_color(self, r: int, g: int, b: int):
        """
        Set the color of the gripper's LED.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).
        """