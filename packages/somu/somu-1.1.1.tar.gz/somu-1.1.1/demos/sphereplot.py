import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

plt.rcParams["axes.labelsize"] = 0

def fibonacci_sphere(n_points):
    points = np.zeros((n_points, 3))
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio
    
    for i in range(n_points):
        y = 1 - (2 * i) / (n_points - 1)  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)       # radius at y
        theta = 2 * np.pi * i / phi
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius
        points[i] = [x, y, z]
    return points

def scatter_sphere(points, labels, figsize=(30, 18)):
	fig = plt.figure(figsize=figsize)
	ax = fig.add_subplot(111, projection='3d')

	u = np.linspace(0, 2 * np.pi, 100)
	v = np.linspace(0, np.pi, 100)
	x = np.outer(np.cos(u), np.sin(v))
	y = np.outer(np.sin(u), np.sin(v))
	z = np.outer(np.ones(np.size(u)), np.cos(v))

	ax.plot_surface(x, y, z, color='white', alpha=0.1)
	ax.scatter(points[:, 0], points[:, 1], points[:, 2], color='darkred', s=36)

	for point, label in zip(points, labels):
		ax.text(point[0]+0.04, point[1]-0.01, point[2], label, color='darkred', fontweight='bold', fontsize=12, alpha=((1+point[2])/2))

	ax.set_xticklabels([])
	ax.set_yticklabels([])
	ax.set_zticklabels([])
	ax.set_box_aspect([1, 1, 1])
	plt.show()
