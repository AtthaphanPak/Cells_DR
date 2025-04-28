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
    roll = np.degrees(np.arctan2(ny, nz))
    pitch = np.degrees(np.arctan2(-nx, np.sqrt(ny**2 + nz**2)))
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
    
if __name__ == "__main__":
    # Top cover
    ref_points = np.array([
        [0, 50, 0.060],
        [60, 50, 0.060],
        [30, 10, 0.060]
    ])
    # Optical bench
    test_points = np.array([
        [10, 0, 1.400],
        [10, 50, 1.500],
        [50, 0, 1.600],
        [50, 50, 1.500]
    ])
    # Fit planes
    n_ref, _ = fit_plane(ref_points)
    n_test, _ = fit_plane(test_points)
    # Tilt between reference and test
    tilt_angle = calculate_relative_tilt(n_ref, n_test)
    # Roll/pitch of test plane from Z-axis (or you could rotate into reference)
    roll, pitch = calculate_roll_pitch_from_ref(n_test)
    # Output
    print(f"Reference Normal: {n_ref}")
    print(f"Test Normal: {n_test}")
    print(f"Tilt angle between planes: {tilt_angle:.5f}°")
    print(describe_pitch_direction(pitch))
    print(describe_roll_direction(roll))