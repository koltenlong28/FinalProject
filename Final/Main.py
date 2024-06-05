import tkinter as tk
from tkinter import messagebox
import time
import re

class StudentCheckInSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("student checkin placeholder")
        self.root.configure(bg="#262B33")  

        self.student_id_var = tk.StringVar()
        self.start_time = None
        self.student_data = self.read_student_data()

        self.create_widgets()

    def create_widgets(self):
   
        font_style = ("Arial", 10, "bold")
#---------------widget customize---------------#
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
                lines = file.readlines()
                for line in lines:
                    match = re.match(r'studentID:\((\d+)\),Name\(([^,]+),\s([^,]+)\),History\(([^)]+)\)', line.strip())
                    if match:
                        student_id = match.group(1)
                        name = f"{match.group(2)}, {match.group(3)}"
                        history = match.group(4)
                        history_dict = {}
                        history_items = history.split(', ')
                        for item in history_items:
                            key, value = item.split(':')
                            history_dict[key] = int(value)
                        student_data[student_id] = (name, history_dict)
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        return student_data

    def write_student_data(self):
        with open('StudentID.txt', 'w') as file:
            for student_id, (name, history_dict) in self.student_data.items():
                history_str = ', '.join(f'{key}:{value}' for key, value in history_dict.items())
                file.write(f'studentID:({student_id}),Name({name}),History({history_str})\n')

    def check_in(self):
        student_id = self.student_id_var.get()
        if not student_id.isdigit():
            messagebox.showerror("error", "please enter valid Student ID")
            return

        if student_id not in self.student_data:
            messagebox.showerror("error", "student ID not found")
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
        

#---------------time---------------#


        end_time = time.time()
        duration = end_time - self.start_time
        duration_minutes = duration / 60
        student_id = self.student_id_var.get()
        check_out_time = time.strftime('%H:%M:%S', time.localtime(end_time))

        if duration_minutes > 7:
            self.student_data[student_id][1]['BathroomViolations'] += 1

        with open('checkinlog.txt', 'a') as file:
            file.write(f'studentid:({student_id}),timeinbathroom({duration_minutes:.2f} minutes),timeofcheckin({check_out_time})\n')

        messagebox.showinfo("checked out", f"student ID {student_id} checked out. duration: {duration_minutes:.2f} minutes")

        self.write_student_data()

        self.start_time = None
        self.student_id_var.set("")
        self.check_in_button.config(state=tk.NORMAL)
        self.check_out_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCheckInSystem(root)
    root.mainloop()
