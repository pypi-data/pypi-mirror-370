from ....DeviceState import TapoLightState
from ....DeviceControl import TapoControl, LightControl


class TapoLight(TapoLightState, TapoControl, LightControl):
    """
    Tapo L530E light.
    """

    ## Class variables
    # Device controls coordinates
    device_x = 187.2
    device_y = 705.6
    # Toggle coordinates
    x = 612
    y = 619.2
    # Brightness and color gauges
    x_left_gauge = 103
    x_right_gauge = 640
    # Brightness
    y_brightness = 1108.8
    # Color
    x_color_tab = 230.4
    y_color_tab = 1238.4
    y_color = 1310.4


    def do_set_color(self) -> None:
        """
        Ensure the "Color" tab is selected,
        then randomly set the color of the light. 
        """
        self.get_phone().shell(f"input tap {self.x_color_tab} {self.y_color_tab}")
        self._set_light_attr(self.y_color)
