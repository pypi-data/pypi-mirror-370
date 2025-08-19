import numpy as np
from shoeboxpy.model6dof import Shoebox
from shoeboxpy.animate import animate_history
import matplotlib.pyplot as plt


# Initialize the shoebox model
shoebox = Shoebox(
    L=1.0,  # Length (m)
    B=0.3,  # Width (m)
    T=0.03,  # Height (m)
    eta0=np.array([0.0, 0.0, 0.0, 0.1, 0.1, 0.1]),  # Initial position and orientation
    nu0=np.zeros(6),  # Initial velocities
    GM_phi=0.2,  # Metacentric height in roll
    GM_theta=0.2,  # Metacentric height in pitch
)

dt = 0.01
T = np.arange(0, 10, dt)
pose_history = np.zeros((len(T), 6))  # Initialize pose history
velocity_history = np.zeros((len(T), 6))  # Initialize velocity history

# Simulate for 10 seconds with a time step of 0.01 seconds
for i, t in enumerate(T):
    shoebox.step(tau=np.array([2.0, 0.5, 0.0, 0.0, 0.0, 0.1]), dt=dt)  # Apply control forces
    position, velocity = shoebox.get_states()
    pose_history[i] = position  # Store the current state
    velocity_history[i] = velocity  # Store the current velocities

# Plot final on a matplotlib figure. left side of the plot shows the position, right side shows the velocity.

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(T, pose_history[:, 0], label='x (m)')
plt.plot(T, pose_history[:, 1], label='y (m)')



animate_history(pose_history, dt=dt, L=1.0, B=0.3, T=0.2)  # Animate the results