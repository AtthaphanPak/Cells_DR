from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox, QLineEdit
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from datetime import datetime
import numpy as np
import sys
import csv
import os
import configparser

from IL_sensors_cmd import Read_all_sensor, set_all_zero
from measurement import fit_plane, calculate_relative_tilt, calculate_roll_pitch_from_ref, describe_pitch_direction, describe_roll_direction, evaluate_offset_and_result
from fitsdll import fn_Handshake, fn_Log, fn_Query

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("C:\Projects\Cells_DR\Sources\GUI\Displacement_window.ui", self)

        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
        self.exit_confirm_enabled = True
        self.config = configparser.ConfigParser()
        pcname = os.environ['COMPUTERNAME']
        print(pcname)
        self.MC = pcname
        try:
            self.config.read("C:\Projects\Cells_DR\Properties\Config.ini")
            self.IL_IP = self.config["DEFAULT"].get("IL_IP", "")
            self.IL_PORT = int(self.config["DEFAULT"].get("IL_PORT", ""))
            self.LogPath = self.config["DEFAULT"].get("LogPath", "")
            self.mode = self.config["DEFAULT"].get("MODE", "")

            self.model = self.config["FITs"].get("model", "")
            self.operation = self.config["FITs"].get("operation", "")            
        except Exception as e:
            print(f"{e}\nPlease check config.ini")
            print("Close Program", f"{e}\nPlease check config.ini")
            quit()
        
        os.makedirs(self.LogPath, exist_ok=True)
        self.clear_log()

        self.MainstackedWidget.setCurrentIndex(0)
        self.enLineEdit.setFocus()
        self.enLineEdit.returnPressed.connect(self.LoginButton.click)

        pixmap_insert = QPixmap(r"C:\Projects\Cells_DR\Properties\insert_img.jpg")
        self.insert_img.setPixmap(pixmap_insert)
        # self.insert_img.setScaledContents(True)
        pixmap_remove = QPixmap(r"C:\Projects\Cells_DR\Properties\remove_img.jpg")
        self.remove_img.setPixmap(pixmap_remove)
        # self.remove_img.setScaledContents(True)

        # action Button 
        self.LoginButton.clicked.connect(self.login)
        self.ModeButton.clicked.connect(self.select_mode)
        self.StartButton.clicked.connect(self.check_serials)
        self.LogoutButton.clicked.connect(self.logout)
        self.FinishButton.clicked.connect(self.finish_cycle)

    def closeEvent(self, event):
        print("CloseEvent")
        if self.MainstackedWidget.currentIndex() != 0:
            QMessageBox.information(self, "Exit Denied", "You can exit the program at the login screen.")
            event.ignore()
        else:
            event.accept()

    def clear_log(self):
        self.df = {}
        self.en = ""
        self.sn_cover = ""
        self.sn_bench = ""
        self.enLineEdit.setText("")
        self.SNCoverValue.setText("")
        self.SNBenchValue.setText("")
        self.lineEdit_Operator.setText("")
        self.lineEdit_Operation.setText("")
        self.lineEdit_Station.setText("")
        self.lineEdit_Serial.setText("")
        self.lineEdit_Serial_2.setText("")
        self.Cover_1_Value.setText("")
        self.Cover_2_Value.setText("")
        self.Cover_3_Value.setText("")
        self.Bench_1_Value.setText("")
        self.Bench_2_Value.setText("")
        self.Bench_3_Value.setText("")
        self.Bench_4_Value.setText("")
        self.Result_tilt_planes.setText("")
        self.Result_Pitch.setText("")
        self.Result_Roll.setText("")
        self.Result_cover_avg.setText("")
        self.Result_Bench_avg.setText("")
        self.Result_offset.setText("")
        self.Result_Final.setText("")
        self.Result_Final.setStyleSheet("")
    
    def select_mode(self):
        password, ok = QInputDialog.getText(self, "Admin login", "Enter admin password:", QLineEdit.EchoMode.Password)
        if ok and password == "Admin123":
            mode_dialog = QInputDialog()
            mode, ok2 = QInputDialog.getItem(self, "Select Mode", "Choose mode:",["Production", "Debug"], 0, False)
            if ok2:
                self.mode = mode
        else:
            QMessageBox.warning(self, "Asscess Denied", "Incorrect password.")

    def login(self):
        self.en = self.enLineEdit.text()
        if len(self.en) == 6:
            self.label_Error_login.setText("")
            QTimer.singleShot(100, self.serial_page)
        else:
            self.label_Error_login.setStyleSheet("color: red;")
            self.label_Error_login.setText("Invalid Employee number")
            return
        
    def logout(self):
        self.MainstackedWidget.setCurrentIndex(0)
        self.clear_log()
            
    def serial_page(self):
        self.MainstackedWidget.setCurrentIndex(1)
        self.SNCoverValue.setFocus()
        self.SNCoverValue.returnPressed.connect(lambda: self.SNBenchValue.setFocus())
        self.SNBenchValue.returnPressed.connect(self.StartButton.click)

    def check_serials(self):
        print("check_serials")
        self.sn_cover = self.SNCoverValue.text()
        self.sn_bench = self.SNBenchValue.text()
        if self.mode.upper() == "PRODUCTION":
            if len(self.sn_cover) == 12:
                fits_status = fn_Handshake(self.model, self.operation, self.sn_cover)
                if fits_status == True:
                    if len(self.sn_bench) == 12:
                        self.Errorlabel.setText("")
                        QTimer.singleShot(100, self.mainprocess)
                    else:
                        self.Errorlabel.setStyleSheet("color: red;")
                        self.Errorlabel.setText("SN Bench must be 12 digit")
                else:
                    self.Errorlabel.setStyleSheet("color: red;")
                    self.Errorlabel.setText(fits_status)
            else:
                self.Errorlabel.setStyleSheet("color: red;")
                self.Errorlabel.setText("SN Cover must be 12 digit")
        else:
            self.Errorlabel.setText("")
            QTimer.singleShot(100, self.mainprocess)
        
    def mainprocess(self):
        self.MainstackedWidget.setCurrentIndex(2)
        self.lineEdit_Operator.setText(self.en)
        self.lineEdit_Operation.setText(self.operation)
        self.lineEdit_Station.setText(self.MC)
        self.lineEdit_Serial.setText(self.sn_cover)
        self.lineEdit_Serial_2.setText(self.sn_bench)

        QMessageBox.information(self, "Insert Top Cover", "Please Insert Top cover to reset all sensor to zero")
        IL_status = set_all_zero(self.IL_IP, self.IL_PORT)
        if IL_status is False:
            print("Can not set zreo\nPlease check IL-Sensor power")
            QMessageBox.critical(self, "IL Sensor ERROR", "Can not set zreo\nPlease check IL-Sensor power")
            quit()
        
        QMessageBox.information(self, "Remove Top cover", "Please remove top cover before read measured values")
        IL_status = Read_all_sensor(self.IL_IP, self.IL_PORT)
        if IL_status is False:
            print("Can not read sensor\nPlease check IL-Sensor power")
            QMessageBox.critical(self, "IL Sensor ERROR", "Can not read sensor\nPlease check IL-Sensor power")
            quit()

        array_values = IL_status.split(",")
        array_values.pop(0)
        # print(array_values)
        measured_values = np.array(array_values).astype(int) / 1000
        if np.any((measured_values > 999) | (measured_values < -999)):
            QMessageBox.warning(self, "Sensor out limit", "Please check Sensor or Unit that place in fixture")
            self.MainstackedWidget.setCurrentIndex(1)
            self.SNCoverValue.setFocus()
            return
        
        measured_values_str = measured_values.astype(str)
        self.Cover_1_Value.setText(measured_values_str[0])
        self.Cover_2_Value.setText(measured_values_str[1])
        self.Cover_3_Value.setText(measured_values_str[2])
        self.Bench_1_Value.setText(measured_values_str[3])
        self.Bench_2_Value.setText(measured_values_str[4])
        self.Bench_3_Value.setText(measured_values_str[5])
        self.Bench_4_Value.setText(measured_values_str[6])
        # print(f"Displacement measured\nCover 1\t{measured_values[0]}\nCover 2\t{measured_values[1]}\nCover 3\t{measured_values[2]}\nBench 1\t{measured_values[3]}\nBench 2\t{measured_values[4]}\nBench 3\t{measured_values[5]}\nBench 4\t{measured_values[6]}")
        
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
        Result_Pitch = describe_pitch_direction(pitch)
        Result_Roll = describe_roll_direction(roll)
        # Output tilt info

        print(f"Reference Normal: {n_ref}")
        print(f"Test Normal: {n_test}")
        self.Result_tilt_planes.setText(f"{tilt_angle:.5f}")
        self.Result_Pitch.setText(Result_Pitch)
        self.Result_Roll.setText(Result_Roll)

        # Offset and PASS/FAIL check
        offset, cover_avg_z, bench_avg_z, is_pass = evaluate_offset_and_result(ref_points, test_points)
        result = "PASS" if is_pass else "FAIL"
        self.Result_cover_avg.setText(f"{cover_avg_z:5f}")
        self.Result_Bench_avg.setText(f"{bench_avg_z:.5f}")
        self.Result_offset.setText(f"{offset:.5f}")
        if result == "PASS":
            self.Result_Final.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            self.Result_Final.setText(result)
        else:
            self.Result_Final.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            self.Result_Final.setText(result)
        
        
        self.df = {
            "EN": self.en,
            "SN Cover": self.sn_cover,
            "SN Bench": self.sn_bench,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Cover 1": measured_values_str[0],
            "Cover 2": measured_values_str[1],
            "Cover 3": measured_values_str[2],
            "Bench 1": measured_values_str[3],
            "Bench 2": measured_values_str[4],
            "Bench 3": measured_values_str[5],
            "Bench 4": measured_values_str[6],
            "Reference Normal": str(n_ref),
            "Test Normal": str(n_test),
            "Tilt angle between planes": f"{tilt_angle:.5f}",
            "Tilt Pitch direction":str(Result_Pitch),
            "Tilt Roll direction":str(Result_Roll),
            "Cover avg Z": f"{cover_avg_z:5f}",
            "Bench avg Z": f"{bench_avg_z:.5f}",
            "Offset": f"{offset:.5f}",
            "Result": "PASS" if is_pass else "FAIL"
        }

        QTimer.singleShot(100, self.record_results)

    def record_results(self):
        now = self.df["Timestamp"].replace(":","-")
        filepath = os.path.join(self.LogPath, f"{self.sn_cover}_{now}.csv")
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.df.keys())  # Write header
            writer.writerow(self.df.values())  # Write values
                
            parameters = ";".join(self.df.keys())
            values = ";".join(self.df.values())
        if self.mode.upper() == "PRODUCTION":
            fits_status = fn_Log(self.model, self.operation, parameters, values)
            if fits_status == True:
                QMessageBox.information(self, "FITs Message", "Data has been uploaded to FITs")
            else:
                QMessageBox.critical(self, "FITs Message", "Data uploaded failed to FITs\nPlease manual key and contract developer Ext:7763")
        else:
            QMessageBox.information(self, "System Message", f"Data has been Store in Log file\n{self.LogPath}")
        
        self.MainstackedWidget.setCurrentIndex(3)
    
    def finish_cycle(self):
        self.clear_log()
        self.MainstackedWidget.setCurrentIndex(1)
        self.SNCoverValue.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())    