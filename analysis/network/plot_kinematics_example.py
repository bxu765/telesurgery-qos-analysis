import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def align_console_kinematic_data_new(robot, completed):
        Tpos = np.array([[0, -1,  0],
                         [-1, 0,  0],
                         [0,  0, -1]])
        Trot = np.array([[0, 1, 0],
                         [1, 0, 0],
                         [0, 0, 1]]) 
        sf_pos = 0.000115 * 0.09     
        sf_rot = 0.008

        new_completed = np.zeros((len(robot), completed.shape[1]))
        r, c = new_completed.shape
          
        for i in range(r):
            e = np.argmin(np.abs(completed[:, 0] - robot[i, 0]))
            #e = np.where(completed[:, 1] == robot[i, 1])[0][0]
            new_completed[i, :] = completed[e, :] 
            pos0 = Tpos @ np.sum(completed[0:e+1, 2:5], axis=0) * sf_pos
            rot0 = Trot @ np.sum(completed[0:e+1, 5:8], axis=0) * sf_rot 
            pos1 = Tpos @ np.sum(completed[0:e+1, 8:11], axis=0) * sf_pos
            rot1 = Trot @ np.sum(completed[0:e+1, 11:14], axis=0) * sf_rot
            Ti = np.concatenate([pos0, rot0, pos1, rot1])
            new_completed[i, 2:14] = Ti
        
        return new_completed

def get_robot_grasper_commands(command_data):
        Left_Commands = command_data[:, -2]
        Right_Commands = command_data[:, -1]
        Left = np.zeros(len(Left_Commands))
        Right = np.zeros(len(Right_Commands))

        for i in range(len(Left_Commands)):
            if Left_Commands[i] < -0.7:
                Left[i] = 1
            if Right_Commands[i] < -0.7:
                Right[i] = 1

        return Left, Right

def process_robot_yaw(robot_data):
    # Process yaw data to ensure it is continuous
    robot_data[:, -1] = np.where(robot_data[:, -1] < -1.7, robot_data[:, -1] + 2 * np.pi, robot_data[:, -1])
    robot_data[:,  7] = np.where(robot_data[:,  7] < -1.7, robot_data[:,  7] + 2 * np.pi, robot_data[:,  7])
    return robot_data

# Load trajectory data
script_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(script_dir, "../..", "SurRoL_dVTrainer/tests/dVTrainer/Data/exp_data_15/no_fault/freefault1")
robot_data     = np.loadtxt(os.path.join(root, "robot_sim_data_1.csv"), delimiter=",", skiprows=1)
completed_data = np.loadtxt(os.path.join(root, "console_data_completed_1.csv"), delimiter=",", skiprows=1)
command_data   = np.loadtxt(os.path.join(root, "robot_command_data_1.csv"), delimiter=",", skiprows=1)
robot_data = robot_data[:len(command_data), :]
robot_data = process_robot_yaw(robot_data)

completed_data[:, 0] *= 10**-9
console_data = align_console_kinematic_data_new(robot_data, completed_data)
pedal_data = console_data[:, 16] * -1 + 1
left_grasper, right_grasper = get_robot_grasper_commands(command_data)

# Time axes (relative to start)
t_robot   = robot_data[:, 0]   - robot_data[0, 0]
t_console = console_data[:, 0] - robot_data[0, 0]
max_time = max(t_robot[-1], t_console[-1])

# ── Figure 1: Left arm ────────────────────────────────────────────────────────
fig, axs = plt.subplots(6, 1, figsize=(10, 14), sharex=True)
fig.suptitle('Left Robotic Arm Trajectory (X, Y, Z, Yaw), Grasper, and Pedal vs Time')

for ax, r_col, c_col, label in zip(axs[:3], [2, 3, 4], [2, 3, 4], ['X', 'Y', 'Z']):
    ax.plot(t_robot,   robot_data[:, r_col]   - robot_data[0, r_col],   label='Robot')
    ax.plot(t_console, console_data[:, c_col] - console_data[0, c_col], '--', label='Console')
    ax.set_ylabel(f'{label} Position')
    ax.legend()

axs[3].plot(t_robot,   robot_data[:, 7]   - robot_data[0, 7],   label='Robot Yaw')
axs[3].plot(t_console, console_data[:, 7] - console_data[0, 7], '--', label='Console Yaw')
axs[3].set_ylabel('Yaw')
axs[3].legend()

axs[4].plot(t_console, left_grasper, label='Left Grasper')
axs[4].set_ylabel('Grasper')
axs[4].set_ylim(-0.1, 1.1)
axs[4].set_yticks([0, 1])
axs[4].set_yticklabels(['Open', 'Close'])
axs[4].legend()

axs[5].plot(t_console, pedal_data, label='Pedal')
axs[5].set_ylabel('Pedal')
axs[5].set_ylim(-0.1, 1.1)
axs[5].set_yticks([0, 1])
axs[5].set_yticklabels(['Up', 'Down'])
axs[5].set_xlabel('Time (s)')
axs[5].legend()

for ax in axs:
    ax.set_xlim(0, max_time)

plt.tight_layout()

# ── Figure 2: Right arm ───────────────────────────────────────────────────────
fig2, axs2 = plt.subplots(6, 1, figsize=(10, 14), sharex=True)
fig2.suptitle('Right Robotic Arm Trajectory (X, Y, Z, Yaw), Grasper, and Pedal vs Time')

for ax, r_col, c_col, label in zip(axs2[:3], [8, 9, 10], [8, 9, 10], ['X', 'Y', 'Z']):
    ax.plot(t_robot,   robot_data[:, r_col]   - robot_data[0, r_col],   label='Robot')
    ax.plot(t_console, console_data[:, c_col] - console_data[0, c_col], '--', label='Console')
    ax.set_ylabel(f'{label} Position')
    ax.legend()

axs2[3].plot(t_robot,   robot_data[:, 13]   - robot_data[0, 13],   label='Robot Yaw')
axs2[3].plot(t_console, console_data[:, 13] - console_data[0, 13], '--', label='Console Yaw')
axs2[3].set_ylabel('Yaw')
axs2[3].legend()

axs2[4].plot(t_console, right_grasper, label='Right Grasper')
axs2[4].set_ylabel('Grasper')
axs2[4].set_ylim(-0.1, 1.1)
axs2[4].set_yticks([0, 1])
axs2[4].set_yticklabels(['Open', 'Close'])
axs2[4].legend()

axs2[5].plot(t_console, pedal_data, label='Pedal')
axs2[5].set_ylabel('Pedal')
axs2[5].set_ylim(-0.1, 1.1)
axs2[5].set_yticks([0, 1])
axs2[5].set_yticklabels(['Up', 'Down'])
axs2[5].set_xlabel('Time (s)')
axs2[5].legend()

for ax in axs2:
    ax.set_xlim(0, max_time)

plt.tight_layout()
plt.show()
