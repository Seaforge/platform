#!/usr/bin/env python3
"""
Demo 5: OOW DP (DYNAMIC POSITIONING) TRAINING
A realistic station-keeping scenario requiring precise thruster control
and decision-making under environmental stress.

Scenario: Offshore supply vessel holding position at an oil platform
against wind, current, and wave conditions.

Training focus: Thruster management, fuel optimization, situational awareness,
emergency procedures (loss of DP system, thruster failure).
"""

import json
import math
import time
from typing import Dict, List, Tuple


class DPVessel:
    """Dynamic positioning vessel with thruster control."""

    def __init__(self):
        self.vessel_name = "MV DP SENTINEL"
        self.vessel_class = "PSV"  # Platform Supply Vessel

        # Position (UTM-like coordinates for stability)
        self.position = {"x": 100.0, "y": 100.0}  # meters from target
        self.target = {"x": 0.0, "y": 0.0}
        self.heading = 45.0  # degrees
        self.heading_target = 0.0

        # Velocity (m/s)
        self.velocity = {"x": 0.0, "y": 0.0}
        self.angular_velocity = 0.0

        # Thrusters
        self.thrusters = {
            "main_engine": {"power": 0, "max": 100},  # % thrust
            "bow_thruster": {"power": 0, "max": 100},
            "port_azimuth": {"power": 0, "max": 100, "angle": 0},  # degrees
            "starboard_azimuth": {"power": 0, "max": 100, "angle": 0}
        }

        # Environmental forces
        self.wind = {"speed": 25, "direction": 180}  # knots, degrees
        self.current = {"speed": 1.5, "direction": 90}  # knots, degrees
        self.waves = {"height": 2.5, "period": 8}  # meters, seconds

        # Resources
        self.fuel_level = 100.0  # percent
        self.fuel_consumption_rate = 0.5  # % per minute at full power
        self.time_elapsed = 0.0
        self.dt = 1.0  # time step in seconds

        # Performance tracking
        self.position_history = []
        self.errors = []  # position deviations
        self.actions_log = []

    def apply_environmental_forces(self) -> None:
        """Apply wind and current disturbances to vessel position."""
        # Wind effect (simplified: drives lateral drift)
        wind_rad = math.radians(self.wind["direction"])
        wind_force_x = self.wind["speed"] * 0.01 * math.cos(wind_rad)
        wind_force_y = self.wind["speed"] * 0.01 * math.sin(wind_rad)

        # Current effect
        curr_rad = math.radians(self.current["direction"])
        curr_force_x = self.current["speed"] * 0.005 * math.cos(curr_rad)
        curr_force_y = self.current["speed"] * 0.005 * math.sin(curr_rad)

        # Apply forces to velocity
        self.velocity["x"] += (wind_force_x + curr_force_x) * self.dt
        self.velocity["y"] += (wind_force_y + curr_force_y) * self.dt

    def apply_thruster_forces(self) -> None:
        """Convert thruster commands to vessel movement."""
        # Main engine + bow thruster (surge/yaw)
        if self.thrusters["main_engine"]["power"] > 0:
            main_thrust = self.thrusters["main_engine"]["power"] * 0.05
            self.velocity["x"] += main_thrust * math.cos(math.radians(self.heading))
            self.velocity["y"] += main_thrust * math.sin(math.radians(self.heading))

        # Bow thruster (sway)
        if self.thrusters["bow_thruster"]["power"] > 0:
            bow_thrust = self.thrusters["bow_thruster"]["power"] * 0.02
            self.velocity["x"] += bow_thrust * math.sin(math.radians(self.heading))
            self.velocity["y"] -= bow_thrust * math.cos(math.radians(self.heading))

        # Azimuth thrusters (omnidirectional)
        for azimuth_name in ["port_azimuth", "starboard_azimuth"]:
            azimuth = self.thrusters[azimuth_name]
            if azimuth["power"] > 0:
                az_rad = math.radians(azimuth["angle"])
                force = azimuth["power"] * 0.03
                self.velocity["x"] += force * math.cos(az_rad)
                self.velocity["y"] += force * math.sin(az_rad)

        # Yaw control (heading)
        yaw_command = (self.heading_target - self.heading) * 0.02
        self.angular_velocity += yaw_command

    def update_position(self) -> None:
        """Update vessel position based on velocity."""
        # Apply damping (friction)
        self.velocity["x"] *= 0.95
        self.velocity["y"] *= 0.95
        self.angular_velocity *= 0.90

        # Update position
        self.position["x"] += self.velocity["x"] * self.dt
        self.position["y"] += self.velocity["y"] * self.dt
        self.heading += self.angular_velocity * self.dt
        self.heading = self.heading % 360

        self.position_history.append({
            "x": self.position["x"],
            "y": self.position["y"],
            "heading": self.heading,
            "time": self.time_elapsed
        })

    def consume_fuel(self) -> None:
        """Consume fuel based on thruster power usage."""
        total_power = sum(t.get("power", 0) for t in self.thrusters.values()) / 4
        fuel_burn = (total_power / 100) * self.fuel_consumption_rate * (self.dt / 60.0)
        self.fuel_level = max(0, self.fuel_level - fuel_burn)

    def calculate_position_error(self) -> float:
        """Calculate distance from target position (meters)."""
        error_x = self.position["x"] - self.target["x"]
        error_y = self.position["y"] - self.target["y"]
        return math.sqrt(error_x**2 + error_y**2)

    def step(self, thruster_commands: Dict = None) -> Dict:
        """Advance simulation one timestep."""
        if thruster_commands:
            # Update thrusters correctly (don't overwrite structure)
            for thruster_name, command in thruster_commands.items():
                if thruster_name == "heading_target":
                    self.heading_target = command
                elif thruster_name in self.thrusters:
                    self.thrusters[thruster_name].update(command)
            self.actions_log.append({
                "time": self.time_elapsed,
                "commands": thruster_commands
            })

        self.apply_environmental_forces()
        self.apply_thruster_forces()
        self.update_position()
        self.consume_fuel()

        error = self.calculate_position_error()
        self.errors.append(error)
        self.time_elapsed += self.dt

        return {
            "position": self.position,
            "heading": self.heading,
            "error_m": error,
            "fuel": self.fuel_level,
            "velocity": self.velocity
        }

    def get_status(self) -> Dict:
        """Get current vessel status."""
        error = self.calculate_position_error()
        is_on_station = error < 5.0  # Within 5 meters = on station
        is_critical = error > 20.0  # More than 20 meters = critical
        is_out_of_fuel = self.fuel_level < 5.0

        return {
            "vessel": self.vessel_name,
            "time_elapsed": self.time_elapsed,
            "position": self.position,
            "target": self.target,
            "error_m": round(error, 2),
            "on_station": is_on_station,
            "critical_drift": is_critical,
            "heading": self.heading,
            "fuel": self.fuel_level,
            "out_of_fuel": is_out_of_fuel,
            "wind": f"{self.wind['speed']} kts from {self.wind['direction']}°",
            "current": f"{self.current['speed']} kts from {self.current['direction']}°"
        }


def run_dp_training_demo() -> Dict:
    """Run OOW DP training scenario."""
    print("\n" + "="*70)
    print("DEMO 5: OOW DP (DYNAMIC POSITIONING) TRAINING")
    print("="*70)
    print("\n⚓ SCENARIO: Offshore Supply Vessel — Station-Keeping at Platform\n")

    vessel = DPVessel()

    print("📋 INITIAL CONDITIONS:")
    print(f"   Vessel: {vessel.vessel_name} (Platform Supply Vessel)")
    print(f"   Start Position: X={vessel.position['x']:.1f}m, Y={vessel.position['y']:.1f}m")
    print(f"   Target Position: X={vessel.target['x']:.1f}m, Y={vessel.target['y']:.1f}m")
    print(f"   Error: {vessel.calculate_position_error():.1f}m\n")

    print("🌊 ENVIRONMENTAL CONDITIONS:")
    print(f"   Wind: {vessel.wind['speed']} knots from {vessel.wind['direction']}°")
    print(f"   Current: {vessel.current['speed']} knots from {vessel.current['direction']}°")
    print(f"   Wave Height: {vessel.waves['height']}m, Period {vessel.waves['period']}s\n")

    print("🎮 OPERATOR CONTROL SEQUENCE:\n")

    # Simulate operator commands over time
    control_phases = [
        # Phase 1: Initial positioning (0-30 seconds)
        {
            "name": "Initial Approach",
            "duration": 30,
            "commands": [
                {"main_engine": {"power": 80}, "heading_target": 0},
                {"main_engine": {"power": 60}, "bow_thruster": {"power": 30}},
                {"main_engine": {"power": 40}, "bow_thruster": {"power": 20}}
            ]
        },
        # Phase 2: Fine positioning (30-60 seconds)
        {
            "name": "Station-Keeping Adjustment",
            "duration": 30,
            "commands": [
                {"main_engine": {"power": 20}, "bow_thruster": {"power": 15}},
                {"main_engine": {"power": 15}, "port_azimuth": {"power": 25, "angle": 270}},
                {"main_engine": {"power": 10}, "bow_thruster": {"power": 10}}
            ]
        },
        # Phase 3: Hold position (60-90 seconds)
        {
            "name": "On-Station Holding",
            "duration": 30,
            "commands": [
                {"main_engine": {"power": 10}, "bow_thruster": {"power": 5}},
                {"main_engine": {"power": 8}, "bow_thruster": {"power": 8}},
                {"main_engine": {"power": 12}, "port_azimuth": {"power": 15, "angle": 90}}
            ]
        }
    ]

    total_simulation_time = 0
    for phase_idx, phase in enumerate(control_phases, 1):
        print(f"   Phase {phase_idx}: {phase['name']} ({phase['duration']}s)")

        steps_per_phase = phase['duration']
        for step in range(steps_per_phase):
            cmd_idx = min(step // (steps_per_phase // len(phase['commands'])), len(phase['commands']) - 1)
            status = vessel.step(phase['commands'][cmd_idx])

        # Print phase summary
        avg_error = sum(vessel.errors[-steps_per_phase:]) / len(vessel.errors[-steps_per_phase:]) if vessel.errors else 0
        current_status = vessel.get_status()
        on_station_marker = "✓" if current_status['on_station'] else "✗"
        fuel_marker = "⚠️ " if current_status['fuel'] < 20 else "✓"

        print(f"      {on_station_marker} Error: {current_status['error_m']:.2f}m | {fuel_marker} Fuel: {current_status['fuel']:.1f}%")
        total_simulation_time = current_status['time_elapsed']
        print()

    # Calculate performance metrics
    final_status = vessel.get_status()
    avg_error = sum(vessel.errors) / len(vessel.errors) if vessel.errors else 0
    max_error = max(vessel.errors) if vessel.errors else 0
    time_on_station = sum(1 for e in vessel.errors if e < 5.0)
    on_station_percent = (time_on_station / len(vessel.errors) * 100) if vessel.errors else 0

    print("\n" + "="*70)
    print("PERFORMANCE REVIEW")
    print("="*70)

    print(f"\n📊 STATION-KEEPING METRICS:")
    print(f"   Total Time: {final_status['time_elapsed']} seconds")
    print(f"   Final Error: {final_status['error_m']:.2f} meters")
    print(f"   Average Error: {avg_error:.2f} meters")
    print(f"   Maximum Error: {max_error:.2f} meters")
    print(f"   Time On-Station (<5m): {on_station_percent:.0f}%")

    print(f"\n⛽ RESOURCE MANAGEMENT:")
    print(f"   Fuel Consumed: {100 - final_status['fuel']:.1f}%")
    print(f"   Remaining: {final_status['fuel']:.1f}%")
    print(f"   Efficiency: {'Good' if final_status['fuel'] > 60 else 'Moderate' if final_status['fuel'] > 30 else 'Poor'}")

    # Scoring
    if final_status['on_station'] and on_station_percent > 80:
        score = "EXCELLENT - Ready for platform transfer operations"
    elif on_station_percent > 60:
        score = "GOOD - Acceptable for most operations"
    elif on_station_percent > 40:
        score = "FAIR - Requires more training"
    else:
        score = "POOR - Immediate retraining required"

    print(f"\n🎓 ASSESSMENT: {score}")

    if final_status['critical_drift']:
        print("   ⚠️  WARNING: Critical drift detected. Loss of DP may cause collision risk.")
    if final_status['out_of_fuel']:
        print("   🚨 CRITICAL: Out of fuel! Emergency procedures required.")

    print("\n" + "="*70 + "\n")

    return {
        "status": "pass",
        "demo": "dp_training",
        "scenario": "Station-Keeping at Offshore Platform",
        "duration": final_status['time_elapsed'],
        "final_error_m": final_status['error_m'],
        "average_error_m": avg_error,
        "on_station_percent": on_station_percent,
        "fuel_remaining": final_status['fuel'],
        "assessment": score,
        "position_history": vessel.position_history[-20:]  # Last 20 positions for visualization
    }


if __name__ == "__main__":
    result = run_dp_training_demo()
    print(f"Demo result: {json.dumps(result, indent=2)}")
