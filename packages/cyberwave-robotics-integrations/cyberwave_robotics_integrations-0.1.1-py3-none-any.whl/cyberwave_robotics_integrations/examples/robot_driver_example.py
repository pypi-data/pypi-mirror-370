#!/usr/bin/env python3
"""
Robot Driver Factory Example
Demonstrates using the robot factory for different robot types
"""

from cyberwave_robotics_integrations.factory import Robot
import cyberwave as cw

def demo_factory_usage():
    """Demonstrate robot factory usage"""
    print("🏭 Robot Factory Demo")
    print("=" * 40)
    
    # Available robot types
    robot_types = ["spot", "so100", "tello", "kuka_kr3"]
    
    for robot_type in robot_types:
        print(f"\n🤖 Testing {robot_type.upper()} driver:")
        try:
            robot = Robot(robot_type)
            print(f"✅ {robot_type} driver created successfully")
            
            # Simulate connection (would connect to real hardware)
            print(f"  Connecting to {robot_type}...")
            # robot.connect()  # Uncomment for real hardware
            
            # Demo robot-specific commands
            if robot_type == "spot":
                print("  Commands: stand(), sit(), move_to(x, y)")
                # robot.stand()
                # robot.move_to(1.0, 2.0)
                # robot.sit()
                
            elif robot_type == "so100":
                print("  Commands: move_joint(), move_to_position()")
                # robot.move_joint("shoulder", 45)
                # robot.move_to_position([0.3, 0.1, 0.4])
                
            elif robot_type == "tello":
                print("  Commands: takeoff(), move_forward(), land()")
                # robot.takeoff()
                # robot.move_forward(100)  # cm
                # robot.land()
                
            elif robot_type == "kuka_kr3":
                print("  Commands: home(), move_joints()")
                # robot.home()
                # robot.move_joints([0, 45, -30, 0, 90, 0])
            
            print(f"  Disconnecting from {robot_type}...")
            # robot.disconnect()  # Uncomment for real hardware
            
        except Exception as e:
            print(f"⚠️ {robot_type} demo failed (expected without hardware): {e}")

def demo_sdk_integration():
    """Demonstrate integration with main Cyberwave SDK"""
    print("\n🔗 SDK Integration Demo")
    print("=" * 40)
    
    # Configure SDK
    cw.configure(base_url="http://localhost:8000")
    print("SDK configured")
    
    # Create digital twins
    print("\nCreating digital twins:")
    twins = {
        'arm': cw.twin("cyberwave/so101", name="Digital SO101"),
        'spot': cw.twin("spot/spot_mini", name="Digital Spot"),
        'drone': cw.twin("dji/tello", name="Digital Tello")
    }
    
    for name, twin in twins.items():
        print(f"✅ Created {name}: {twin.name}")
    
    # Create corresponding hardware drivers
    print("\nCreating hardware drivers:")
    drivers = {}
    for name in twins.keys():
        try:
            if name == 'arm':
                drivers[name] = Robot("so100")
            elif name == 'spot':
                drivers[name] = Robot("spot")
            elif name == 'drone':
                drivers[name] = Robot("tello")
            
            print(f"✅ Created {name} driver")
            
        except Exception as e:
            print(f"⚠️ {name} driver failed: {e}")
    
    # Demonstrate twin-driver coordination
    print("\nDemonstrating twin-driver coordination:")
    
    # Move digital twin
    twins['arm'].move_to([0.3, 0.1, 0.4])
    print("  Digital twin moved")
    
    # Would sync to hardware driver
    # if 'arm' in drivers:
    #     position = twins['arm'].position
    #     drivers['arm'].move_to_position(position)
    #     print("  Hardware synced with digital twin")
    
    print("✅ Integration demo completed")

def demo_configuration_file():
    """Show how to create and use configuration files"""
    print("\n⚙️ Configuration File Demo")
    print("=" * 40)
    
    config_content = '''# ~/.cyberwave/config.yaml
api_key: "your-api-key-here"
base_url: "http://localhost:8000"
default_environment: "your-environment-uuid"

# Robot-specific configurations
robots:
  so100:
    port: "/dev/ttyUSB0"
    baudrate: 115200
    timeout: 5.0
    home_position: [0, 0, 0.3]
    
  spot:
    ip: "192.168.1.100"
    username: "admin"  
    password: "spot_password"
    max_velocity: 1.5
    
  tello:
    ip: "192.168.10.1"
    port: 8889
    max_height: 5.0
    
  kuka_kr3:
    ip: "192.168.1.200"
    port: 7000
    safety_limits: true
    workspace_limits:
      x: [-0.8, 0.8]
      y: [-0.8, 0.8] 
      z: [0.0, 1.2]

# Telemetry settings
telemetry:
  enabled: true
  forward_to_backend: true
  sample_rate_hz: 10
  buffer_size: 1000
  
# Logging configuration
logging:
  level: "INFO"
  console: true
  file: "~/.cyberwave/logs/drivers.log"
  max_file_size: "10MB"
  backup_count: 5
'''
    
    print("Configuration file structure:")
    print(config_content)
    
    print("Usage with CLI:")
    print("  $ cyberwave config init  # Create default config")
    print("  $ cyberwave config show  # Display current config")
    print("  $ cyberwave config set robots.spot.ip 192.168.1.100")
    print("  $ cyberwave drivers start spot  # Uses config settings")

def main():
    """Run robot driver examples"""
    print("🤖 Robot Driver Factory Examples")
    print("=" * 60)
    
    demo_factory_usage()
    demo_sdk_integration()
    demo_configuration_file()
    
    print("\n" + "=" * 60)
    print("🎉 Robot Driver Examples Complete!")
    
    print("\n📋 Summary:")
    print("✅ Factory pattern for robot creation")
    print("✅ Integration with main Cyberwave SDK")
    print("✅ Configuration file management")
    print("✅ Digital twin + hardware driver coordination")
    
    print("\n🚀 Ready to Use:")
    print("1. Install: pip install cyberwave cyberwave-robotics-integrations")
    print("2. Configure: cw.configure(api_key='your-key')")
    print("3. Create twins: cw.twin('registry/id')")
    print("4. Control hardware: Robot('robot-type')")

if __name__ == "__main__":
    main()
