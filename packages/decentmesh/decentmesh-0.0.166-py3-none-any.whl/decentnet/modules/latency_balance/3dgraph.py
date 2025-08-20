import sys
from random import uniform

import numpy as np
import pyqtgraph.opengl as gl
from PySide6 import QtCore, QtWidgets

from decentnet.modules.latency_balance.icosa_balancer import IcosaBalancer

# Constants
NUM_POINTS = 35  # Number of points in the sphere
GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))  # Golden angle in radians for Fibonacci sphere
ADJUSTMENT_SPEED = 0.4  # Fraction of the adjustment applied per cycle (5%)
NEW_TARGET_SPEED = 0.1  # Speed for transitioning to new values
DISTANCE_SCALE = 0.2  # Scale factor for distance from center
FRAME_RATE = 30  # Timer interval in milliseconds
BATCH_UPDATE_INTERVAL = 5  # Number of cycles between batch updates

# Latency ranges for initial values
LATENCY_MIN = 1
LATENCY_MAX = 150

# Point size and colors
POINT_COLOR = (0.5, 0, 0.5, 0.9)  # RGBA color for points
POINT_SIZE = 8  # Size of each point

# Line color and width
LINE_COLOR = (0.4, 0.8, 0.95, 0.2)  # RGBA color for lines
LINE_WIDTH = 0.1  # Width of each line


class PointData:
    """Class to hold per-point data for animation."""

    def __init__(self, client_id, initial_in, theta, phi):
        self.client_id = client_id
        self.in_latency = initial_in
        self.target_in = initial_in  # Initial target is the starting value
        self.adjustment = 0.0  # Incremental adjustment per cycle
        self.theta = theta
        self.phi = phi
        self.point_item = None


class Latency3DApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Spherical Latency Visualization")
        self.setGeometry(100, 100, 800, 600)

        # Generate initial client data
        self.clients_data = {
            f"client_{i}": {
                "in_latency": uniform(LATENCY_MIN, LATENCY_MAX),
                "out_latency": uniform(LATENCY_MIN, LATENCY_MAX),
                "byte_size": 1
            }
            for i in range(NUM_POINTS)
        }

        # Set up GLViewWidget for 3D rendering
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=80)
        self.setCentralWidget(self.view)

        # Timer for animation updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(FRAME_RATE)

        # Create points and lines for visualization
        self.point_data_list = []
        self.line_items = []  # Store line items for easy removal
        self.create_points_and_lines()

        # Counter to control batch updates
        self.update_counter = 0

    def fibonacci_sphere(self, num_points):
        """Generate theta and phi angles for points distributed on a sphere using the Fibonacci sphere algorithm."""
        theta_phi_pairs = []

        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2  # y goes from 1 to -1
            radius = np.sqrt(1 - y * y)  # Radius at y

            theta = GOLDEN_ANGLE * i  # Golden angle increment
            phi = np.arccos(y)  # Derived from y value for spherical distribution

            theta_phi_pairs.append((theta, phi))

        return theta_phi_pairs

    def create_points_and_lines(self):
        """Create points in a spherical distribution using Fibonacci sphere for even placement."""
        theta_phi_pairs = self.fibonacci_sphere(len(self.clients_data))

        for (client_id, client_data), (theta, phi) in zip(self.clients_data.items(), theta_phi_pairs):
            initial_in = client_data["in_latency"]

            # Create PointData object with fixed theta and phi from Fibonacci sphere
            point_data = PointData(client_id, initial_in, theta, phi)

            # Calculate initial position on the sphere with distance based on initial_in
            distance = initial_in * DISTANCE_SCALE
            x = distance * np.sin(phi) * np.cos(theta)
            y = distance * np.sin(phi) * np.sin(theta)
            z = distance * np.cos(phi)

            # Create a scatter plot point
            point_item = gl.GLScatterPlotItem(pos=np.array([[x, y, z]]), color=POINT_COLOR, size=POINT_SIZE)
            point_data.point_item = point_item
            self.point_data_list.append(point_data)
            self.view.addItem(point_item)

    def clear_lines(self):
        """Remove old lines from the view to prevent performance issues."""
        for line in self.line_items:
            self.view.removeItem(line)
        self.line_items.clear()

    def update_lines(self):
        """Update lines between points based on current positions."""
        self.clear_lines()  # Remove old lines before adding new ones

        # Create lines connecting each pair of points
        for i in range(len(self.point_data_list)):
            for j in range(i + 1, len(self.point_data_list)):
                start = self.point_data_list[i].point_item.pos[0]
                end = self.point_data_list[j].point_item.pos[0]
                line = gl.GLLinePlotItem(pos=np.array([start, end]), color=LINE_COLOR, width=LINE_WIDTH,
                                         antialias=True)
                self.line_items.append(line)
                self.view.addItem(line)

    def generate_new_targets(self):
        """Generate new target latencies and set adjustments using IcosaBalancer."""
        for point_data in self.point_data_list:
            # Set new target latencies randomly
            point_data.target_in = uniform(LATENCY_MIN, LATENCY_MAX)
            self.clients_data[point_data.client_id]["in_latency"] = point_data.in_latency
            self.clients_data[point_data.client_id]["out_latency"] = point_data.target_in

        # Calculate adjustments with IcosaBalancer based on new target values
        adjustments = IcosaBalancer.balance_client_latencies(self.clients_data)

        # Assign adjustments to each point's data
        for point_data in self.point_data_list:
            point_data.adjustment = adjustments[point_data.client_id]["in_latency_adjustment"]

    def update_animation(self):
        """Animate each point moving closer or farther based on in_latency values, with adjustments to target value using IcosaBalancer."""

        # Define rotation speeds for azimuth and elevation to achieve diagonal rotation
        azimuth_speed = 0.5  # Adjust for speed of azimuth rotation
        elevation_speed = 0.3  # Adjust for speed of elevation rotation

        # Retrieve and increment the camera rotation angles for diagonal movement
        current_azimuth = self.view.opts['azimuth'] + azimuth_speed
        current_elevation = self.view.opts['elevation'] + elevation_speed

        # Apply the rotation by updating camera position with new azimuth and elevation
        self.view.setCameraPosition(azimuth=current_azimuth, elevation=current_elevation)

        # Every BATCH_UPDATE_INTERVAL cycles, generate new targets and calculate adjustments
        if self.update_counter % BATCH_UPDATE_INTERVAL == 0:
            self.generate_new_targets()

        # Smoothly transition each point towards its target latency position
        for point_data in self.point_data_list:
            distance_to_target = point_data.target_in - point_data.in_latency
            if abs(distance_to_target) > 0.1:
                point_data.in_latency += distance_to_target * NEW_TARGET_SPEED
            else:
                point_data.in_latency += point_data.adjustment * ADJUSTMENT_SPEED

            # Calculate the new position based on the updated in_latency
            distance = point_data.in_latency * DISTANCE_SCALE
            x = distance * np.sin(point_data.phi) * np.cos(point_data.theta)
            y = distance * np.sin(point_data.phi) * np.sin(point_data.theta)
            z = distance * np.cos(point_data.phi)

            # Update point position with new coordinates
            point_data.point_item.setData(pos=np.array([[x, y, z]]))

        # Increment update counter and refresh lines and view
        self.update_counter += 1
        self.update_lines()
        self.view.update()  # Refresh the view


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Latency3DApp()
    window.show()
    sys.exit(app.exec())
