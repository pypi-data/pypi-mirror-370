"""Small demo using the robot driver factory."""
from cyberwave_robotics_integrations.factory import Robot


def main() -> None:
    robot = Robot("spot")
    robot.connect()
    robot.move_to(1.0, 2.0)
    robot.sit()
    robot.disconnect()


if __name__ == "__main__":
    main()
