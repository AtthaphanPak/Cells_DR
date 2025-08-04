import numpy as np

def fit_plane(points):
    X = np.c_[points[:, 0], points[:, 1], np.ones(points.shape[0])]
    Z = points[:, 2]
    coeffs, *_ = np.linalg.lstsq(X, Z, rcond=None)
    a, b, c = coeffs
    normal = np.array([-a, -b, 1.0])
    normal /= np.linalg.norm(normal)
    return normal, coeffs
def calculate_relative_tilt(n_ref, n_test):
    """Calculate total tilt angle (degrees) between two normal vectors"""
    dot = np.dot(n_ref, n_test)
    angle_rad = np.arccos(np.clip(dot, -1.0, 1.0))
    return np.degrees(angle_rad)
def calculate_roll_pitch_from_ref(n_test, n_ref=np.array([0, 0, 1])):
    """Calculate pitch, roll from test plane's normal vector (relative to vertical)"""
    nx, ny, nz = n_test
    roll = np.degrees(np.arctan2(ny, nz))   # Around X axis
    pitch = np.degrees(np.arctan2(-nx, np.sqrt(ny**2 + nz**2)))  # Around Y axis
    return roll, pitch
def describe_pitch_direction(pitch, threshold=0.001):
    if pitch > threshold:
        return f"Tilt backward {abs(pitch):.5f}°"
    elif pitch < -threshold:
        return f"Tilt forward {abs(pitch):.5f}°"
    else:
        return "No forward/backward tilt"
def describe_roll_direction(roll, threshold=0.001):
    if roll > threshold:
        return f"Tilt left {abs(roll):.5f}°"
    elif roll < -threshold:
        return f"Tilt right {abs(roll):.5f}°"
    else:
        return "No left/right tilt"
def evaluate_offset_and_result(ref_points, test_points, nominal=-18.11, tolerance=0.25):
    cover_avg_z = np.mean(ref_points[:, 2])
    bench_avg_z = np.mean(test_points[:, 2])
    offset = bench_avg_z - cover_avg_z
    is_pass = abs(offset - nominal) <= tolerance
    return offset, cover_avg_z, bench_avg_z, is_pass

# ------------------------------
if __name__ == "__main__":
    # Top cover
    ref_points = np.array([
        [0, 0, 0.012],
        [155, 10, 0.058],
        [100, 90, 0.032]
    ])
    # Optical bench
    test_points = np.array([
        [40, 70, -18.143],
        [135, 70, -18.518],
        [25, 23, -17.445],
        [135, 15, -18.065]
    ])
    # Fit planes
    n_ref, _ = fit_plane(ref_points)
    n_test, _ = fit_plane(test_points)
    # Tilt
    tilt_angle = calculate_relative_tilt(n_ref, n_test)
    roll, pitch = calculate_roll_pitch_from_ref(n_test)
    # Output tilt info
    print(f"Reference Normal: {n_ref}")
    print(f"Test Normal: {n_test}")
    print(f"Tilt angle between planes: {tilt_angle:.5f}°")
    print(describe_pitch_direction(pitch))
    print(describe_roll_direction(roll))
    # Offset and PASS/FAIL check
    offset, cover_avg_z, bench_avg_z, is_pass = evaluate_offset_and_result(ref_points, test_points)
    print(f"Cover avg Z: {cover_avg_z:.3f} mm")
    print(f"Bench avg Z: {bench_avg_z:.3f} mm")
    print(f"Offset: {offset:.3f} mm")
    print("Result: PASS" if is_pass else "Result: FAIL")