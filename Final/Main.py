import tkinter as tk
from tkinter import messagebox
import time
import re
import os
import threading

class StudentCheckInSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("student checkin system")
        self.root.configure(bg="#262B33")  

        self.student_id_var = tk.StringVar()
        self.start_time = None
        self.student_data = self.read_student_data()

        self.create_widgets()
        self.file_monitor_thread = threading.Thread(target=self.check_student_file)
        self.file_monitor_thread.daemon = True
        self.file_monitor_thread.start()

    def create_widgets(self):
        font_style = ("Arial", 10, "bold")
        tk.Label(self.root, text="enter student ID:", bg="#262B33", fg="white", font=font_style).grid(row=0, column=0, padx=10, pady=10)
        self.student_id_entry = tk.Entry(self.root, textvariable=self.student_id_var, font=font_style)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=10)

        self.check_in_button = tk.Button(self.root, text="check in", command=self.check_in, font=font_style, bg="#363e4a", fg="white")
        self.check_in_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.check_out_button = tk.Button(self.root, text="check out", command=self.check_out, state=tk.DISABLED, font=font_style, bg="#363e4a", fg="white")
        self.check_out_button.grid(row=2, column=0, columnspan=2, pady=10)

    def read_student_data(self):
        student_data = {}
        try:
            with open('StudentID.txt', 'r') as file:
                for line in file:
                    match = re.match(r'studentID:\((\d+)\),name\(([^)]+)\),history\(([^)]+)\),timeout\((\w+)\)', line.strip())
                    if match:
                        student_id, name, history_str, timeout = match.groups()
                        history = {key: int(value) for key, value in (item.split(':') for item in history_str.split(', '))}
                        student_data[student_id] = (name, history, timeout == 'True')
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        except Exception as e:
            messagebox.showerror("error", f"error reading student data: {str(e)}")
        return student_data

    def write_student_data(self):
        with open('StudentID.txt', 'w') as file:
            for student_id, (name, history_dict, timeout) in self.student_data.items():
                history_str = ', '.join(f'{key}:{value}' for key, value in history_dict.items())
                file.write(f'studentID:({student_id}),name({name}),history({history_str}),timeout({timeout})\n')

    def check_in(self):
        student_id = self.student_id_var.get()
        if not student_id.isdigit():
            messagebox.showerror("error", "please eater a valid student ID")
            return

        if student_id not in self.student_data:
            messagebox.showerror("error", "student ID not found")
            return

        if self.student_data[student_id][2]:
            messagebox.showerror("error", "you are in timeout")
            return

        self.student_data[student_id][1]['excuses'] += 1
        self.write_student_data()

        self.start_time = time.time()
        self.check_in_button.config(state=tk.DISABLED)
        self.check_out_button.config(state=tk.NORMAL)
        check_in_time = time.strftime('%H:%M:%S', time.localtime(self.start_time))
        messagebox.showinfo("checked in", f"student ID {student_id} checked in at {check_in_time}")

    def check_out(self):
        if not self.start_time:
            messagebox.showerror("error", "you must check in first")
            return

        end_time = time.time()
        duration = end_time - self.start_time
        duration_minutes = duration / 60
        student_id = self.student_id_var.get()
        check_out_time = time.strftime('%H:%M:%S', time.localtime(end_time))

        if duration_minutes > 7:
            self.student_data[student_id][1]['BathroomViolations'] += 1

        with open('checkinlog.txt', 'a') as file:
            file.write(f'studentID:({student_id}),timeinbathroom({duration_minutes:.2f} minutes),timeofcheckin({check_out_time})\n')

        messagebox.showinfo("checked out", f"student ID {student_id} checked out. duration: {duration_minutes:.2f} minutes")

        self.write_student_data()

        self.start_time = None
        self.student_id_var.set("")
        self.check_in_button.config(state=tk.NORMAL)
        self.check_out_button.config(state=tk.DISABLED)

    def check_student_file(self):
        try:
            last_modified = os.path.getmtime('StudentID.txt')
            while True:
                if os.path.getmtime('StudentID.txt') > last_modified:
                    self.student_data = self.read_student_data()
                    last_modified = os.path.getmtime('StudentID.txt')
                time.sleep(1)
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCheckInSystem(root)
    root.mainloop()
