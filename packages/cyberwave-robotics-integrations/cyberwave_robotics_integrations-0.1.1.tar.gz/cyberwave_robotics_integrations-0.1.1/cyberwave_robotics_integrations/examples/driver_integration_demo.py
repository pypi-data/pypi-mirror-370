#!/usr/bin/env python3
"""
Robot Driver Integration Demo
Demonstrates how to use robot drivers with the Cyberwave SDK
"""

import cyberwave as cw
from cyberwave_robotics_integrations.drivers import so100_driver, spot_driver, tello_driver
from cyberwave_robotics_integrations.factory import Robot

def demo_direct_driver_usage():
    """Demonstrate direct driver usage"""
    print("🔧 Direct Driver Usage Demo")
    print("-" * 40)
    
    # SO100 Robotic Arm
    print("\n🦾 SO100 Robotic Arm:")
    try:
        arm_driver = so100_driver.SO100Driver()
        print("✅ SO100 driver created")
        
        # Simulate connection (would connect to real hardware)
        print("  Connecting to robot...")
        # arm_driver.connect()  # Uncomment for real hardware
        
        print("  Moving joints...")
        # arm_driver.move_joint("shoulder", 45)  # Uncomment for real hardware
        # arm_driver.move_joint("elbow", -30)
        
        print("✅ SO100 demo completed")
        
    except Exception as e:
        print(f"⚠️ SO100 demo failed (expected without hardware): {e}")
    
    # Spot Quadruped
    print("\n🐕 Boston Dynamics Spot:")
    try:
        spot_driver_instance = spot_driver.SpotDriver()
        print("✅ Spot driver created")
        
        print("  Would connect to Spot robot...")
        # spot_driver_instance.connect()  # Uncomment for real hardware
        # spot_driver_instance.stand()
        # spot_driver_instance.move_to(1.0, 0.0)
        
        print("✅ Spot demo completed")
        
    except Exception as e:
        print(f"⚠️ Spot demo failed (expected without hardware): {e}")
    
    # Tello Drone
    print("\n🚁 DJI Tello Drone:")
    try:
        tello_driver_instance = tello_driver.TelloDriver()
        print("✅ Tello driver created")
        
        print("  Would connect to Tello...")
        # tello_driver_instance.connect()  # Uncomment for real hardware
        # tello_driver_instance.takeoff()
        # tello_driver_instance.move_forward(100)  # cm
        
        print("✅ Tello demo completed")
        
    except Exception as e:
        print(f"⚠️ Tello demo failed (expected without hardware): {e}")

def demo_factory_pattern():
    """Demonstrate robot factory pattern"""
    print("\n🏭 Robot Factory Pattern Demo")
    print("-" * 40)
    
    # Create robots using factory
    robot_types = ["so100", "spot", "tello", "kuka_kr3"]
    
    for robot_type in robot_types:
        try:
            robot = Robot(robot_type)
            print(f"✅ Created {robot_type} robot via factory")
            
            # Demonstrate common interface
            print(f"  Robot type: {robot_type}")
            # robot.connect()  # Uncomment for real hardware
            # robot.status()
            
        except Exception as e:
            print(f"⚠️ {robot_type} factory failed: {e}")

def demo_sdk_integration():
    """Demonstrate integration with main Cyberwave SDK"""
    print("\n🔗 SDK Integration Demo")
    print("-" * 40)
    
    # Configure SDK
    cw.configure(base_url="http://localhost:8000")
    
    # Create digital twins that can connect to real hardware
    print("Creating digital twins with hardware drivers...")
    
    # Digital twin with hardware driver integration
    arm_twin = cw.twin("cyberwave/so101", name="Physical SO101")
    spot_twin = cw.twin("spot/spot_mini", name="Physical Spot")
    
    print(f"✅ Created digital twin: {arm_twin.name}")
    print(f"✅ Created digital twin: {spot_twin.name}")
    
    # Simulate coordinated movement
    print("\nSimulating coordinated movement...")
    
    # Move digital twins (would sync with physical robots)
    arm_twin.move_to([0.3, 0.1, 0.4])
    spot_twin.move_to([1.0, 0.5, 0.0])
    
    print("✅ Digital twins moved (would sync to hardware)")
    
    # Joint control for robotic arm
    arm_twin.joints.shoulder = 30
    arm_twin.joints.elbow = -45
    arm_twin.joints.wrist = 90
    
    print("✅ Arm joints configured (would move physical robot)")
    
    # Simulation control
    cw.simulation.play()
    print("✅ Simulation started")
    
    # Run physics simulation
    for step in range(5):
        cw.simulation.step()
        print(f"  Physics step {step+1}: Updating robot states")
    
    cw.simulation.pause()
    print("✅ Simulation paused")

def demo_telemetry_and_monitoring():
    """Demonstrate telemetry collection and monitoring"""
    print("\n📊 Telemetry and Monitoring Demo")
    print("-" * 40)
    
    # Create robots for monitoring
    robots = [
        cw.twin("cyberwave/so101", name="Monitored Arm"),
        cw.twin("spot/spot_mini", name="Monitored Spot")
    ]
    
    print("Setting up telemetry monitoring...")
    
    # Simulate robot operations with monitoring
    for i, robot in enumerate(robots):
        print(f"\nMonitoring {robot.name}:")
        
        # Move robot and monitor state
        robot.move_to([i * 0.5, 0, 0.3])
        print(f"  Position: {robot.position}")
        print(f"  Rotation: {robot.rotation}")
        
        # For robotic arms, monitor joints
        if "Arm" in robot.name:
            robot.joints.shoulder = 45
            robot.joints.elbow = -30
            joint_states = robot.joints.all()
            print(f"  Joint states: {joint_states}")
        
        # Simulate sensor data collection
        if robot.has_sensors:
            print(f"  Sensors: Active")
        else:
            print(f"  Sensors: None configured")
    
    print("✅ Telemetry demo completed")

def demo_error_recovery():
    """Demonstrate error handling and recovery scenarios"""
    print("\n🛠️ Error Recovery Demo")
    print("-" * 40)
    
    # Simulate various error conditions
    scenarios = [
        ("Invalid robot creation", lambda: cw.twin("invalid/robot")),
        ("Invalid joint access", lambda: cw.twin("cyberwave/so101").joints.invalid_joint),
        ("Invalid position", lambda: cw.twin("cyberwave/so101").move_to([999, 999, 999]))
    ]
    
    for scenario_name, scenario_func in scenarios:
        print(f"\nTesting: {scenario_name}")
        try:
            result = scenario_func()
            print(f"  ⚠️ Expected error but got result: {result}")
        except Exception as e:
            print(f"  ✅ Error handled gracefully: {type(e).__name__}")
    
    # Recovery operations
    print("\nPerforming recovery operations...")
    cw.simulation.reset()
    print("  ✅ Simulation reset")
    
    # Create valid robot after errors
    recovery_robot = cw.twin("cyberwave/so101", name="Recovery Robot")
    recovery_robot.move_to([0, 0, 0.3])
    print("  ✅ Recovery robot created and positioned")

def main():
    """Run all robotics integration demos"""
    print("🤖 Cyberwave Robotics Integration Demo")
    print("=" * 60)
    
    # Run all demo sections
    demo_direct_driver_usage()
    demo_factory_pattern()
    
    # Set up environment for advanced demos
    robots = setup_environment()
    
    demo_sdk_integration()
    demo_simulation_states()
    demo_physics_interaction(robots)
    demo_telemetry_and_monitoring(robots)
    demo_error_recovery()
    
    # Final cleanup
    print("\n🧹 Cleanup")
    print("-" * 40)
    
    for robot in robots.values():
        robot.delete()
        print(f"  {robot.name} removed")
    
    cw.simulation.reset()
    print("  Simulation reset")
    
    print("\n" + "=" * 60)
    print("🎉 Robotics Integration Demo Complete!")
    
    print("\n📚 Integration Features Demonstrated:")
    print("- Direct hardware driver usage")
    print("- Robot factory pattern")
    print("- SDK integration with digital twins")
    print("- Physics simulation with real robot models")
    print("- Real-time telemetry and monitoring")
    print("- Error handling and recovery")
    print("- Performance optimization")
    
    print("\n🔧 Next Steps:")
    print("- Connect real hardware for full testing")
    print("- Configure robot-specific settings")
    print("- Set up telemetry forwarding")
    print("- Implement custom input controllers")

if __name__ == "__main__":
    main()
