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
    dot = np.dot(n_ref, n_test)
    angle_rad = np.arccos(np.clip(dot, -1.0, 1.0))
    return np.degrees(angle_rad)
def calculate_roll_pitch_from_ref(n_test):
    nx, ny, nz = n_test
    roll = np.degrees(np.arctan2(ny, nz))  # around X
    pitch = np.degrees(np.arctan2(-nx, np.sqrt(ny**2 + nz**2)))  # around Y
    return roll, pitch
def describe_pitch_direction(pitch, threshold=0.001):
    if pitch > threshold:
        return f"Tilt backward {abs(pitch):.4f}°"
    elif pitch < -threshold:
        return f"Tilt forward {abs(pitch):.4f}°"
    else:
        return "No forward/backward tilt"
def describe_roll_direction(roll, threshold=0.001):
    if roll > threshold:
        return f"Tilt left {abs(roll):.4f}°"
    elif roll < -threshold:
        return f"Tilt right {abs(roll):.4f}°"
    else:
        return "No left/right tilt"
def evaluate_offset_and_result(ref_z, test_z, nominal=-18.11, tolerance=0.25):
    offset = np.mean(test_z) - np.mean(ref_z)
    is_pass = abs(offset - nominal) <= tolerance
    return offset, is_pass
def analyze_displacement(sensor_values):
    # Top cover
    ref_points = np.array([
        [0, 0, sensor_values[0]],
        [155, 10, sensor_values[1]],
        [100, 90, sensor_values[2]]
    ])
    # Optical bench
    test_points = np.array([
        [40, 70, sensor_values[3]],
        [135, 70, sensor_values[4]],
        [25, 23, sensor_values[5]],
        [135, 15, sensor_values[6]]
    ])
    # Step 1-2: Fit reference plane
    n_ref, _ = fit_plane(ref_points)
    z_offset = np.mean(ref_points[:, 2])
    # Step 3-4: Offset both sets
    ref_points[:, 2] -= z_offset
    test_points[:, 2] -= z_offset
    print(ref_points[:, 2])
    print(test_points[:, 2])
    # Step 5: Fit adjusted test plane
    n_test, _ = fit_plane(test_points)
    # Step 6: Compute angles
    tilt_angle = calculate_relative_tilt(n_ref, n_test)
    roll, pitch = calculate_roll_pitch_from_ref(n_test)
    roll_msg = describe_roll_direction(roll)
    pitch_msg = describe_pitch_direction(pitch)
    offset, is_pass = evaluate_offset_and_result(ref_points[:, 2], test_points[:, 2])
    # Results
    return {
        "Reference Normal": n_ref,
        "Test Normal": z_offset,
        "tilt_angle": tilt_angle,
        "roll": roll,
        "pitch": pitch,
        "roll_direction": roll_msg,
        "pitch_direction": pitch_msg,
        "offset": offset,
        "test_points_offset": test_points,
        "result": "PASS" if is_pass else "FAIL"
    }