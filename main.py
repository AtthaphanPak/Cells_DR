import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# ---------------------------
# Reference Plane (Z = 0 for all points)
# ---------------------------
# A = np.array([0.0, 0.0, 0.0])
# B = np.array([50.0, 0.0, 0.0])
# C = np.array([0.0, 50.0, 0.0])
# Fixed normal vector since reference plane is horizontal
n_ref = np.array([0.0, 0.0, 1.0])
# ---------------------------
# Test Plane - 4 points (from displacement measurements)
# ---------------------------
test_points = np.array([
    [10.2, 3.7, 0.502],
    [44.9, 2.1, 0.498],
    [5.4, 45.3, 0.503],
    [48.7, 48.0, 0.499]
])
# ---------------------------
# Least Squares Plane Fit จาก 4 จุด
# ---------------------------
def normal_vector_from_4_points(points):
    X = np.c_[points[:, 0], points[:, 1], np.ones(points.shape[0])]
    Z = points[:, 2]
    coeffs, _, _, _ = np.linalg.lstsq(X, Z, rcond=None)
    a, b = coeffs[0], coeffs[1]
    normal = np.array([-a, -b, 1.0])
    return normal / np.linalg.norm(normal), coeffs
# ---------------------------
# คำนวณมุมเอียง
# ---------------------------
def compute_tilt_angle_deg(n1, n2):
    cos_theta = np.clip(np.dot(n1, n2), -1.0, 1.0)
    angle_rad = np.arccos(cos_theta)
    return np.degrees(angle_rad)


# ---------------------------
# MAIN
# ---------------------------
n_test, (a, b, c) = normal_vector_from_4_points(test_points)
tilt_angle = compute_tilt_angle_deg(n_ref, n_test)
# คำนวณมุมเอียงแยกตามแกน
tilt_x_angle = np.degrees(np.arctan2(n_test[0], n_test[2]))
tilt_y_angle = np.degrees(np.arctan2(n_test[1], n_test[2]))
# ---------------------------
# สร้างภาพ 3D
# ---------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
# Plot test points
ax.scatter(test_points[:, 0], test_points[:, 1], test_points[:, 2], color='red', label='Test Points')
# Reference plane (flat Z = 0)
xx, yy = np.meshgrid(np.linspace(0, 50, 10), np.linspace(0, 50, 10))
zz_ref = np.zeros_like(xx)
zz_test = a * xx + b * yy + c
# Plot planes
ax.plot_surface(xx, yy, zz_ref, alpha=0.3, color='blue', label='Reference Plane')
ax.plot_surface(xx, yy, zz_test, alpha=0.3, color='red', label='Test Plane')
# Plot normals
origin = np.mean(test_points, axis=0)
ax.quiver(origin[0], origin[1], origin[2], n_test[0], n_test[1], n_test[2], length=10, color='red', label='Test Normal')
ax.quiver(origin[0], origin[1], origin[2], n_ref[0], n_ref[1], n_ref[2], length=10, color='blue', label='Ref Normal')
# Labels and info
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.set_title(f"Tilt Angle = {tilt_angle:.4f}°\n"
             f"Tilt X = {tilt_x_angle:.2f}° ({'Right' if tilt_x_angle>0 else 'Left'}), "
             f"Tilt Y = {tilt_y_angle:.2f}° ({'Forward' if tilt_y_angle>0 else 'Backward'})")
ax.view_init(elev=20, azim=135)
plt.tight_layout()
plt.show()