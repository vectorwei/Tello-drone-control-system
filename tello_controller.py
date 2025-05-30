# tello_controller.py
from djitellopy import Tello
import time

class TelloController:
    def __init__(self):
        self.tello = Tello()
        self.connect()
        self.in_air = False

    def connect(self):
        self.tello.connect()
        print(f"Battery: {self.tello.get_battery()}%")

    def takeoff(self):
        if not self.in_air:
            self.tello.takeoff()
            self.in_air = True
    def land(self):
        if self.in_air:
            self.tello.land()
            self.in_air = False

    def move_up(self):
        self.tello.move_up(30)

    def move_down(self):
        self.tello.move_down(30)

    def rotate(self):
        self.tello.rotate_clockwise(360)

    def end(self):
        if self.in_air:
            self.land()
        self.tello.end()
