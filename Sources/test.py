from IL_sensors_cmd import Read_all_sensor, set_all_zero
import tkinter as tk
from tkinter import messagebox
import time
import numpy as np
import csv

def repeatabilitywithoutfixture(IP, PORT):
    root = tk.Tk()
    root.withdraw()

    # set_all_zero(IP, PORT)
    time.sleep(3)
    df = {
        "Cover_1": [],
        "Cover_2": [],
        "Cover_3": [],
        "Bench_1": [],
        "Bench_2": [],
        "Bench_3": [],
        "Bench_4": [],
    }

    for i in range(10):
        values = Read_all_sensor(IP, PORT)
        array_values = values.split(",")
        array_values.pop(0)
        measured_values = np.array(array_values).astype(int) / 1000
        time.sleep(1)
        df["Cover_1"].append(measured_values[0])
        df["Cover_2"].append(measured_values[1])
        df["Cover_3"].append(measured_values[2])
        df["Bench_1"].append(measured_values[3])
        df["Bench_2"].append(measured_values[4])
        df["Bench_3"].append(measured_values[5])
        df["Bench_4"].append(measured_values[6])
        print(measured_values.astype(str))
    # print(df)
    keys = list(df.keys())
    rows = zip(*[df[key] for key in keys])

    with open("repeatabilitywithoutmovingfixture.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)  # Write header row
        writer.writerows(rows)  # Write data rows

def repeatabilitywithfixture(IP, PORT):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # set_all_zero(IP, PORT)
    time.sleep(3)
    df = {
        "Cover_1": [],
        "Cover_2": [],
        "Cover_3": [],
        "Bench_1": [],
        "Bench_2": [],
        "Bench_3": [],
        "Bench_4": [],
    }

    for i in range(10):
        messagebox.showinfo("Remove and insert part.", "Remove and insert part.")
        values = Read_all_sensor(IP, PORT)
        array_values = values.split(",")
        array_values.pop(0)
        measured_values = np.array(array_values).astype(int) / 1000
        df["Cover_1"].append(measured_values[0])
        df["Cover_2"].append(measured_values[1])
        df["Cover_3"].append(measured_values[2])
        df["Bench_1"].append(measured_values[3])
        df["Bench_2"].append(measured_values[4])
        df["Bench_3"].append(measured_values[5])
        df["Bench_4"].append(measured_values[6])
        print(measured_values.astype(str))
        
    # print(df)
    keys = list(df.keys())
    rows = zip(*[df[key] for key in keys])

    with open("repeatabilitywithmovingfixture.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)  # Write header row
        writer.writerows(rows)  # Write data rows

def reproduce(IP, PORT):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # set_all_zero(IP, PORT)
    time.sleep(3)
    df = {
        "Cover_1": [],
        "Cover_2": [],
        "Cover_3": [],
        "Bench_1": [],
        "Bench_2": [],
        "Bench_3": [],
        "Bench_4": [],
    }

    for i in range(10):
        messagebox.showinfo("Remove and insert part.", "Remove and insert part.")
        values = Read_all_sensor(IP, PORT)
        array_values = values.split(",")
        array_values.pop(0)
        measured_values = np.array(array_values).astype(int) / 1000
        df["Cover_1"].append(measured_values[0])
        df["Cover_2"].append(measured_values[1])
        df["Cover_3"].append(measured_values[2])
        df["Bench_1"].append(measured_values[3])
        df["Bench_2"].append(measured_values[4])
        df["Bench_3"].append(measured_values[5])
        df["Bench_4"].append(measured_values[6])
        print(measured_values.astype(str))

    # print(df)
    keys = list(df.keys())
    rows = zip(*[df[key] for key in keys])

    with open("reproduce.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)  # Write header row
        writer.writerows(rows)  # Write data rows

IP = "169.254.148.227"
PORT = 64000

repeatabilitywithoutfixture(IP, PORT)
# repeatabilitywithfixture(IP, PORT)
# reproduce(IP, PORT)

    