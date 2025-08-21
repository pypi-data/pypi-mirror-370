from RPi import GPIO  # type: ignore

from bluer_sbc.env import BLUER_SBC_ENV

from bluer_ugv.swallow.session.classical.camera import (
    ClassicalCamera,
    ClassicalNavigationCamera,
    ClassicalTrackingCamera,
)
from bluer_ugv.swallow.session.classical.push_button import ClassicalPushButton
from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.mousepad import ClassicalMousePad
from bluer_ugv.swallow.session.classical.motor.rear import ClassicalRearMotors
from bluer_ugv.swallow.session.classical.motor.steering import ClassicalSteeringMotor
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint
from bluer_ugv.env import BLUER_UGV_MOUSEPAD_ENABLED
from bluer_ugv.logger import logger


class ClassicalSession:
    def __init__(
        self,
        object_name: str,
    ):
        self.object_name = object_name

        self.leds = ClassicalLeds()

        self.setpoint = ClassicalSetPoint(
            leds=self.leds,
        )

        if BLUER_UGV_MOUSEPAD_ENABLED:
            self.mousepad = ClassicalMousePad(
                leds=self.leds,
                setpoint=self.setpoint,
            )

        self.keyboard = ClassicalKeyboard(
            setpoint=self.setpoint,
        )

        self.push_button = ClassicalPushButton(
            leds=self.leds,
        )

        self.steering = ClassicalSteeringMotor(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        self.rear = ClassicalRearMotors(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        camera_class = (
            ClassicalTrackingCamera
            if BLUER_SBC_ENV == "tracking"
            else (
                ClassicalNavigationCamera
                if BLUER_SBC_ENV == "navigation"
                else ClassicalCamera
            )
        )
        logger.info(f"camera: {camera_class.__name__}")
        self.camera = camera_class(
            keyboard=self.keyboard,
            leds=self.leds,
            setpoint=self.setpoint,
            object_name=self.object_name,
        )

        logger.info(
            "{}: created for {}".format(
                self.__class__.__name__,
                self.object_name,
            )
        )

    def cleanup(self):
        for thing in [
            self.rear,
            self.steering,
            self.camera,
        ]:
            thing.cleanup()

        GPIO.cleanup()

        logger.info(f"{self.__class__.__name__}.cleanup")

    def initialize(self) -> bool:
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            logger.error(e)
            return False

        return all(
            thing.initialize()
            for thing in [
                self.push_button,
                self.leds,
                self.steering,
                self.rear,
                self.camera,
            ]
        )

    def update(self) -> bool:
        return all(
            thing.update()
            for thing in [
                self.keyboard,
                self.push_button,
                self.camera,
                self.setpoint,
                self.steering,
                self.rear,
                self.leds,
            ]
        )
