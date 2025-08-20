#!/home/robot/venv311/bin/python3.11
import rpyc
import logging
from ev3dev2.motor import Motor, OUTPUT_A

logger = logging.getLogger(__name__)


def log_decorator(log_text):
    def inner(func):
        def wrapper(*args, **kwargs):
            print(log_text)
            func(*args, **kwargs)

        return wrapper

    return inner


class MyService(rpyc.Service):
    @log_decorator("Connected")
    def on_connect(self, conn):
        self.m = Motor(OUTPUT_A)

    @log_decorator("Disconnected, robot deactivated")
    def on_disconnect(self, conn):
        self.m.stop()

    @log_decorator("Changed motor")
    def change_output(self, output):
        self.m = Motor(output)

    @log_decorator("Running motor indefinitely")
    def run_forever(self, speed):
        self.m.run_forever(speed_sp=speed)

    @log_decorator("Running motor to absolute position")
    def run_abs_pos(self, speed, position, stop_action="brake"):
        self.m.run_to_abs_pos(
            speed_sp=speed, position_sp=position, stop_action=stop_action
        )

    @log_decorator("Running motor to relative position")
    def run_rel_pos(self, speed, position, stop_action="brake"):
        self.m.run_to_rel_pos(
            speed_sp=speed, position_sp=position, stop_action=stop_action
        )

    @log_decorator("Running motor for some time")
    def run_timed(self, speed, time, stop_action="brake"):
        self.m.run_timed(speed_sp=speed, time_sp=time, stop_action=stop_action)

    @log_decorator("Running motor with direct cycle speed")
    def run_direct(self, speed, duty_cycle):
        self.m.run_direct(speed_sp=speed, duty_cycle_sp=duty_cycle)

    def on_for_rotations(self, speed, rotations, brake=True, block=True):
        self.m.on_for_rotations(speed, rotations, brake=brake, block=block)

    def on_for_degrees(self, speed, degrees, brake=True, block=True):
        self.m.on_for_degrees(speed, degrees, brake=brake, block=block)

    def on_to_position(self, speed, position, brake=True, block=True):
        self.m.on_to_position(speed, position, brake=brake, block=block)

    def on_for_seconds(self, speed, seconds, brake=True, block=True):
        self.m.on_for_seconds(speed, seconds, brake=brake, block=block)

    @log_decorator("Waiting")
    def wait(self, cond, timeout=None):
        self.m.wait(cond, timeout=timeout)

    @log_decorator("Waiting until not moving")
    def wait_until_not_moving(self, timeout=None):
        self.m.wait_until_not_moving(timeout=timeout)

    def is_running(self) -> bool:
        return self.m.is_running

    def is_ramping(self) -> bool:
        return self.m.is_ramping

    def is_holding(self) -> bool:
        return self.m.is_holding

    def is_overloaded(self) -> bool:
        return self.m.is_overloaded

    def is_stalled(self) -> bool:
        return self.m.is_stalled

    @log_decorator("Resetting all values")
    def reset(self):
        self.m.reset()

    @log_decorator("Stopping motor")
    def stop(self):
        self.m.stop()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    t = ThreadedServer(
        MyService,
        port=18861,
        protocol_config={
            "allow_public_attrs": True,
        },
    )
    print("Starting server")
    t.start()
