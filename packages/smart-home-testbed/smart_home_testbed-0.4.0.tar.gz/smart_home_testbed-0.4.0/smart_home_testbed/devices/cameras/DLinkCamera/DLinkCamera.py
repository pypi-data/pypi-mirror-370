from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraControl


class DLinkCamera(CameraScreenshotState, CameraControl):
    """
    DLink camera (DCS-8000LH).
    """

    ### Class attributes
    # Android package
    android_package = "com.dlink.mydlinkunified"
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.9
    ## Screen coordinates
    # Stream event
    x_start = 424.8
    y_start = 907.2
    x_stop = 57.6
    y_stop = 1008
    # Error message
    x_error = 360
    y_error = 806.4


    def start_stream(self) -> None:
        """
        Dismiss the potential error message,
        then start the camera's video stream.
        Overwrites the method from the parent class CameraControl.
        """
        phone = self.get_phone()
        phone.shell(f"input tap {self.x_error} {self.y_error}")
        phone.shell(f"input tap {self.x_start} {self.y_start}")
