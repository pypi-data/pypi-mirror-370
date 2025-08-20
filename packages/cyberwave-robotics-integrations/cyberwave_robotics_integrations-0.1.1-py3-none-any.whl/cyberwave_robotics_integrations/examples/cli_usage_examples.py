#!/usr/bin/env python3
"""
CLI Usage Examples
Demonstrates command-line interface for robot drivers
"""

import subprocess
import sys
import os

def demo_cli_installation():
    """Show CLI installation and setup"""
    print("📦 CLI Installation Demo")
    print("-" * 40)
    
    print("Installation commands:")
    print("  pip install cyberwave-cli")
    print("  pip install cyberwave-robotics-integrations")
    print("")
    print("Verify installation:")
    print("  cyberwave --help")
    print("  cyberwave drivers --help")
    print("")

def demo_basic_cli_commands():
    """Demonstrate basic CLI commands"""
    print("⚡ Basic CLI Commands Demo")
    print("-" * 40)
    
    commands = [
        ("List available drivers", "cyberwave drivers list"),
        ("Check driver status", "cyberwave drivers status"),
        ("Start SO100 driver", "cyberwave drivers start so100"),
        ("Start Spot driver", "cyberwave drivers start spot"),
        ("Start Tello driver", "cyberwave drivers start tello"),
        ("Stop all drivers", "cyberwave drivers stop --all"),
    ]
    
    for description, command in commands:
        print(f"\n{description}:")
        print(f"  $ {command}")
        print("  # Would execute driver command")

def demo_advanced_cli_usage():
    """Demonstrate advanced CLI features"""
    print("\n🚀 Advanced CLI Usage Demo")
    print("-" * 40)
    
    print("Device registration and management:")
    print("  $ cyberwave drivers start tello --device-id 123 --token <token>")
    print("  $ cyberwave drivers start tello  # Auto-register device")
    print("")
    
    print("Telemetry forwarding:")
    print("  $ cyberwave drivers start spot --forward-telemetry")
    print("  $ cyberwave drivers start so100 --backend-url http://localhost:8000")
    print("")
    
    print("Configuration management:")
    print("  $ cyberwave config set api_key <your-key>")
    print("  $ cyberwave config set base_url http://localhost:8000")
    print("  $ cyberwave config show")
    print("")
    
    print("Batch operations:")
    print("  $ cyberwave drivers start-all")
    print("  $ cyberwave drivers status-all")
    print("  $ cyberwave drivers stop-all")

def demo_robot_specific_commands():
    """Demonstrate robot-specific CLI commands"""
    print("\n🤖 Robot-Specific Commands Demo")
    print("-" * 40)
    
    print("SO100 Robotic Arm:")
    print("  $ cyberwave drivers start so100 --port /dev/ttyUSB0")
    print("  $ cyberwave drivers so100 home")
    print("  $ cyberwave drivers so100 move-joint shoulder 45")
    print("  $ cyberwave drivers so100 move-to 0.3 0.1 0.4")
    print("")
    
    print("Boston Dynamics Spot:")
    print("  $ cyberwave drivers start spot --ip 192.168.1.100")
    print("  $ cyberwave drivers spot stand")
    print("  $ cyberwave drivers spot sit")
    print("  $ cyberwave drivers spot walk 1.0 0.0")
    print("")
    
    print("DJI Tello Drone:")
    print("  $ cyberwave drivers start tello")
    print("  $ cyberwave drivers tello takeoff")
    print("  $ cyberwave drivers tello move up 50")
    print("  $ cyberwave drivers tello rotate cw 90")
    print("  $ cyberwave drivers tello land")
    print("")
    
    print("KUKA KR3 Industrial Arm:")
    print("  $ cyberwave drivers start kuka_kr3 --ip 192.168.1.200")
    print("  $ cyberwave drivers kuka_kr3 home")
    print("  $ cyberwave drivers kuka_kr3 move-joints 0 45 -30 0 90 0")

def demo_configuration_examples():
    """Show configuration file examples"""
    print("\n⚙️ Configuration Examples")
    print("-" * 40)
    
    print("~/.cyberwave/config.yaml:")
    print("""
api_key: "your-api-key-here"
base_url: "http://localhost:8000"
default_environment: "your-env-uuid"

robots:
  so100:
    port: "/dev/ttyUSB0"
    baudrate: 115200
    timeout: 5.0
    
  spot:
    ip: "192.168.1.100"
    username: "admin"
    password: "password"
    
  tello:
    ip: "192.168.10.1"
    port: 8889
    
  kuka_kr3:
    ip: "192.168.1.200"
    port: 7000
    safety_limits: true

telemetry:
  enabled: true
  forward_to_backend: true
  sample_rate_hz: 10
  
logging:
  level: "INFO"
  file: "~/.cyberwave/logs/drivers.log"
""")

def demo_integration_patterns():
    """Show integration patterns with main SDK"""
    print("\n🔗 Integration Patterns Demo")
    print("-" * 40)
    
    print("Pattern 1: Digital Twin + Hardware Driver")
    print("""
import cyberwave as cw
from cyberwave_robotics_integrations.drivers.so100_driver import SO100Driver

# Create digital twin
arm_twin = cw.twin("cyberwave/so101")

# Create hardware driver
arm_driver = SO100Driver()
arm_driver.connect()

# Sync digital twin with hardware
def sync_twin_to_hardware():
    position = arm_twin.position
    joints = arm_twin.joints.all()
    
    # Apply to hardware
    arm_driver.move_to_position(position)
    for joint_name, angle in joints.items():
        arm_driver.move_joint(joint_name, angle)

# Sync hardware to digital twin  
def sync_hardware_to_twin():
    hw_position = arm_driver.get_position()
    hw_joints = arm_driver.get_joint_states()
    
    # Update digital twin
    arm_twin.position = hw_position
    for joint_name, angle in hw_joints.items():
        setattr(arm_twin.joints, joint_name, angle)
""")
    
    print("\nPattern 2: Bidirectional Sync")
    print("""
import cyberwave as cw
from cyberwave_robotics_integrations.factory import Robot

# Create both digital and physical representations
digital_robot = cw.twin("spot/spot_mini")
physical_robot = Robot("spot")

# Bidirectional sync function
def sync_robots():
    # Digital -> Physical
    physical_robot.move_to(*digital_robot.position[:2])
    
    # Physical -> Digital  
    hw_pos = physical_robot.get_position()
    digital_robot.position = [hw_pos[0], hw_pos[1], 0]

# Real-time sync loop
while True:
    sync_robots()
    cw.simulation.step()
    time.sleep(0.1)
""")

def demo_troubleshooting():
    """Show common troubleshooting scenarios"""
    print("\n🔍 Troubleshooting Guide")
    print("-" * 40)
    
    print("Common Issues and Solutions:")
    print("")
    
    print("1. Driver Connection Failed:")
    print("   Problem: Cannot connect to robot hardware")
    print("   Solutions:")
    print("   - Check robot IP address/port")
    print("   - Verify network connectivity")
    print("   - Check robot power and initialization")
    print("   - Review robot-specific connection requirements")
    print("")
    
    print("2. Import Errors:")
    print("   Problem: Cannot import driver modules")
    print("   Solutions:")
    print("   - pip install cyberwave-robotics-integrations")
    print("   - Check Python environment and PATH")
    print("   - Verify package installation: pip list | grep cyberwave")
    print("")
    
    print("3. CLI Commands Not Found:")
    print("   Problem: cyberwave drivers command not available")
    print("   Solutions:")
    print("   - Install CLI: pip install cyberwave-cli")
    print("   - Check entry points: pip show cyberwave-robotics-integrations")
    print("   - Restart terminal after installation")
    print("")
    
    print("4. Permission Errors:")
    print("   Problem: Cannot access serial ports or network devices")
    print("   Solutions:")
    print("   - Add user to dialout group: sudo usermod -a -G dialout $USER")
    print("   - Check device permissions: ls -la /dev/ttyUSB*")
    print("   - Run with sudo (not recommended for production)")

def main():
    """Run all CLI demo sections"""
    print("🖥️ Cyberwave Robotics CLI Demo")
    print("=" * 60)
    
    demo_cli_installation()
    demo_basic_cli_commands()
    demo_advanced_cli_usage()
    demo_robot_specific_commands()
    demo_configuration_examples()
    demo_integration_patterns()
    demo_troubleshooting()
    
    print("\n" + "=" * 60)
    print("🎉 CLI Demo Complete!")
    
    print("\n📚 CLI Features Covered:")
    print("- Driver management (start/stop/status)")
    print("- Device registration and authentication")
    print("- Telemetry forwarding")
    print("- Robot-specific commands")
    print("- Configuration management")
    print("- Integration with main SDK")
    print("- Error handling and troubleshooting")
    
    print("\n🔧 Next Steps:")
    print("- Install the CLI: pip install cyberwave-cli")
    print("- Try the commands with real hardware")
    print("- Set up configuration files")
    print("- Integrate with your Cyberwave environment")

if __name__ == "__main__":
    main()
