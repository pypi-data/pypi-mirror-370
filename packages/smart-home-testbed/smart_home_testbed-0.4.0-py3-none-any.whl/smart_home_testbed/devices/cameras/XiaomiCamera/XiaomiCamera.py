import time
from miio import ChuangmiCamera
from ....DeviceControl import CameraControl


class XiaomiCamera(CameraControl, ChuangmiCamera):
    """
    Xiaomi camera (Chuangmi IPC019).
    """

    ### Class variables
    # Android package name
    android_package = "com.xiaomi.smarthome"
    ## Screen coordinates
    # Zone button
    x_zone = 345.6
    y_zone = 201.6
    # Camera control button
    x_camera = 619.2
    y_camera = 331.2
    # Stream event
    x_start = 100.8
    y_start = 489.6


    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initialize the Xiaomi camera (Chuangmi IPC019) with its IP address.

        Args:
            ipv4 (str): The device's IPv4 address.
            kwargs (dict): device-specific additional parameters, including device API token.
        """
        ChuangmiCamera.__init__(self, ip=ipv4, token=kwargs.get("token", ""))
        self._was_last_stream_successful = False
    

    def start_app(self) -> None:
        """
        Start the Mi Home app on the phone,
        then switch to the zone control screen,
        then to the camera's stream.

        Raises:
            IndexError: If no adb device is found.
        """
        # Start the Mi Home app
        phone = self.get_phone()
        phone.shell(f"monkey -p {XiaomiCamera.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Switch to the camera control screen
        phone.shell(f"input tap {self.x_zone} {self.y_zone}")
        phone.shell(f"input tap {self.x_camera} {self.y_camera}")


    def start_stream(self) -> None:
        """
        Start the camera's video stream.
        Overrides the method from the `CameraControl` class.
        """
        phone = self.get_phone()
        phone.shell(f"input tap {self.x_start} {self.y_start}")
        phone.shell(f"input tap {self.x_start} {self.y_start}")
    

    def do_stop_stream(self) -> None:
        """
        Stop the camera's video stream.
        Overrides the method from the `CameraControl` class.
        """
        self.start_stream()
    

    def get_state(self) -> bool:
        """
        Get the state of the camera.

        Returns:
            bool: True if the camera is on, False otherwise.
        """
        return self.status().power
