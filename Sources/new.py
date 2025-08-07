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
    pitch = np.degrees(np.arctan2(ny, nz))  # around Y
    roll = np.degrees(np.arctan2(-nx, np.sqrt(ny**2 + nz**2)))  # around X
    print("pitch: ", pitch)
    print("roll: ", roll)
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
        [160.9, 0, sensor_values[1]],
        [96.5, 80.9, sensor_values[2]]
    ])
    # Optical bench
    # test_points = np.array([
    #     [40, 70, sensor_values[3]],
    #     [135, 70, sensor_values[4]],
    #     [25, 23, sensor_values[5]],
    #     [135, 15, sensor_values[6]]
    # ])
    test_points = np.array([
        [44.2, 64.4, sensor_values[3]],
        [142.4, 56, sensor_values[4]],
        [28.4, 14.4, sensor_values[5]],
        [146, 7.5, sensor_values[6]]
    ])
    # Step 1-2: Fit reference plane
    n_ref, _ = fit_plane(ref_points)
    z_offset = np.mean(ref_points[:, 2])
    # Step 3-4: Offset both sets
    ref_points[:, 2] -= z_offset
    test_points[:, 2] -= z_offset
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
        "tilt_angle": tilt_angle,
        "roll": roll,
        "pitch": pitch,
        "roll_direction": roll_msg,
        "pitch_direction": pitch_msg,
        "offset": offset,
        "test_points_offset": test_points,
        "result": "PASS" if is_pass else "FAIL"
    }
# Example usage
if __name__ == "__main__":
    # sensor_values = [0.012, 0.020, 0.032, -18.143, -18.518, -17.445, -18.065]  # 3 cover + 4 bench unit 9
    sensor_values = [0.001, -0.102, -0.223, -18.174, -18.728, -17.426, -18.307]  # 3 cover + 4 bench unit 3
    result = analyze_displacement(sensor_values)
    for i, pt in enumerate(result["test_points_offset"], start=1):
        print(f"Bench {i}: Z = {pt[2]:.2f}")
    print(f"Tilt angle: {result['tilt_angle']:.4f}°")
    print(f"Pitch: {result['pitch_direction']}")
    print(f"Roll: {result['roll_direction']}")
    print(f"Offset Z: {result['offset']:.3f} mm")
    print(f"Result: {result['result']}")