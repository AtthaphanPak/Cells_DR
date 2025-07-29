from IL_sensors_cmd import Read_all_sensor, set_all_zero
from measurement import fit_plane, calculate_relative_tilt, calculate_roll_pitch_from_ref, describe_pitch_direction, describe_roll_direction, evaluate_offset_and_result
import configparser
import os
from PyQt6.QtWidgets import QMessageBox
import numpy as np

class Displacement_measurement():
    def __init__(self):
        self.config = configparser.ConfigParser()
        pcname = os.environ['COMPUTERNAME']     
        print(pcname)
        try:
            self.config.read("C:\Projects\Cells_DR\Source\Properties\Config.ini")
            self.IL_IP = self.config["DEFAULT"].get("IL_IP", "")
            self.IL_PORT = self.config["DEFAULT"].get("IL_PORT", "")
            self.LogPath = self.config["DEFAULT"].get("LogPath", "")
            self.mode = self.config["DEFAULT"].get("mode", "")
        except Exception as e:
            QMessageBox.critical(None, "Close Program", f"{e}\nPlease check config.ini")
            quit()
  
    def main(self):
        IL_status = set_all_zero(self.IL_IP, self.IL_PORT)
        if IL_status is False:
            QMessageBox.critical(None, "IL Sensor ERROR", "Can not set zreo\nPlease check IL-Sensor power")
            quit()
        
        IL_status = Read_all_sensor(self.IL_IP, self.IL_PORT)
        if IL_status is False:
            QMessageBox.critical(None, "IL Sensor ERROR", "Can not read sensor\nPlease check IL-Sensor power")
            quit()

        measured_values = map(float, IL_status.split(",").pop(0))
        QMessageBox.information(None, "Measured values", f"Displacement measured\nCover 1\t{measured_values}\nCover 2\t{measured_values}\nCover 3\t{measured_values}\nBench 1\t{measured_values}\nBench 2\t{measured_values}\nBench 3\t{measured_values}\nBench 4\t{measured_values}")

        # Top cover
        ref_points = np.array([
            [10, 50, measured_values[0]],
            [150, 140, measured_values[1]],
            [175, 50, measured_values[2]]
        ])
        # Optical bench
        test_points = np.array([
            [10, 0, measured_values[3]],
            [10, 50, measured_values[4]],
            [50, 0, measured_values[5]],
            [50, 50, measured_values[6]]
        ])
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

if __name__ == "__main__":
    main = Displacement_measurement()
    main.main()