import tkinter as tk
from tkinter import messagebox
import time

class StudentCheckInSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("student check in placeholder")

        self.student_id_var = tk.StringVar()
        self.start_time = None

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="enter student ID:").grid(row=0, column=0, padx=10, pady=10)
        self.student_id_entry = tk.Entry(self.root, textvariable=self.student_id_var)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=10)

        self.check_in_button = tk.Button(self.root, text="check In", command=self.check_in)
        self.check_in_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.check_out_button = tk.Button(self.root, text="check Out", command=self.check_out, state=tk.DISABLED)
        self.check_out_button.grid(row=2, column=0, columnspan=2, pady=10)

    def check_in(self):
        student_id = self.student_id_var.get()
        if not student_id:
            messagebox.showerror("error", "please enter a valid student ID")
            return

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

        with open('checkinlog.txt', 'a') as file:
            file.write(f'studentID:({student_id}),timeinbathroom({duration_minutes:.2f} minutes),timeofcheckin({check_out_time})\n')

        messagebox.showinfo("checked out", f"student ID {student_id} checked out. duration: {duration_minutes:.2f} minutes")

        self.start_time = None
        self.student_id_var.set("")
        self.check_in_button.config(state=tk.NORMAL)
        self.check_out_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCheckInSystem(root)
    root.mainloop()
