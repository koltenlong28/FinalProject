import tkinter as tk
from tkinter import messagebox
import time
import re
import os
import threading
import socket
import json

class StudentCheckInSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("student checkn system")
        self.root.configure(bg="#262B33")

        self.studentidvar = tk.StringVar()
        self.starttime = None
        self.studentdata = self.read_studentdata()

        self.create_widgets()
        self.filemonitorthread = threading.Thread(target=self.check_student_file)
        self.filemonitorthread.daemon = True
        self.filemonitorthread.start()

        self.serveraddress = ('localhost', 65432)

    def create_widgets(self):
        fontstyle = ("Arial", 10, "bold")
        tk.Label(self.root, text="enter student ID:", bg="#262B33", fg="white", font=fontstyle).grid(row=0, column=0, padx=10, pady=10)
        self.studentidentry = tk.Entry(self.root, textvariable=self.studentidvar, font=fontstyle)
        self.studentidentry.grid(row=0, column=1, padx=10, pady=10)

        self.checkinbutton = tk.Button(self.root, text="check in", command=self.check_in, font=fontstyle, bg="#363e4a", fg="white")
        self.checkinbutton.grid(row=1, column=0, columnspan=2, pady=10)

        self.checkoutbutton = tk.Button(self.root, text="check out", command=self.check_out, state=tk.DISABLED, font=fontstyle, bg="#363e4a", fg="white")
        self.checkoutbutton.grid(row=2, column=0, columnspan=2, pady=10)

    def read_studentdata(self):
        studentdata = {}
        try:
            with open('StudentID.txt', 'r') as file:
                for line in file:
                    match = re.match(r'studentID:\((\d+)\),name\(([^,]+,[^,]+)\),history\(([^)]+)\),timeout\((\w+)\)', line.strip())
                    if match:
                        studentid, name, historystr, timeout = match.groups()
                        history = {key: int(value) for key, value in (item.split(':') for item in historystr.split(', '))}
                        studentdata[studentid] = (name, history, timeout == 'True')
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        except Exception as e:
            messagebox.showerror("error", f"error reading student data: {str(e)}")
        return studentdata

    def write_studentdata(self):
        with open('StudentID.txt', 'w') as file:
            for studentid, (name, historydict, timeout) in self.studentdata.items():
                historystr = ', '.join(f'{key}:{value}' for key, value in historydict.items())
                file.write(f'studentID:({studentid}),name({name}),history({historystr}),timeout({timeout})\n')

    def check_in(self):
        studentid = self.studentidvar.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter valid student ID")
            return

        if studentid not in self.studentdata:
            messagebox.showerror("error", "ptudent ID not found")
            return

        name, history, timeout = self.studentdata[studentid]

        if timeout:
            messagebox.showerror("error", "you are in timeout")
            return

        self.studentdata[studentid][1]['excuses'] += 1
        self.write_studentdata()

        self.starttime = time.time()
        self.checkinbutton.config(state=tk.DISABLED)
        self.checkoutbutton.config(state=tk.NORMAL)
        checkintime = time.strftime('%H:%M:%S', time.localtime(self.starttime))
        messagebox.showinfo("checked in", f"student ID {studentid} checked in at {checkintime}")

        self.send_status_update(studentid, "check_in")

    def check_out(self):
        if not self.starttime:
            messagebox.showerror("error", "you must check in first")
            return

        endtime = time.time()
        duration = endtime - self.starttime
        durationminutes = duration / 60
        studentid = self.studentidvar.get()
        checkouttime = time.strftime('%H:%M:%S', time.localtime(endtime))

        if durationminutes > 12:
            self.studentdata[studentid][1]['BathroomViolations'] += 1
            self.studentdata[studentid] = (self.studentdata[studentid][0], self.studentdata[studentid][1], True)

        with open('checkinlog.txt', 'a') as file:
            file.write(f'studentID:({studentid}),timeinbathroom({durationminutes:.2f} minutes),timeofcheckin({checkouttime})\n')

        messagebox.showinfo("checked out", f"student ID {studentid} checked out. duration: {durationminutes:.2f} minutes")

        self.write_studentdata()

        self.starttime = None
        self.studentidvar.set("")
        self.checkinbutton.config(state=tk.NORMAL)
        self.checkoutbutton.config(state=tk.DISABLED)

        self.send_status_update(studentid, "check_out")

    def send_status_update(self, studentid, action):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.serveraddress)
                message = json.dumps({"studentid": studentid, "action": action})
                sock.sendall(message.encode('utf-8'))
        except ConnectionRefusedError:
            messagebox.showerror("error", "could not connect to teacher UI")

    def check_student_file(self):
        try:
            lastmodified = os.path.getmtime('StudentID.txt')
            while True:
                if os.path.getmtime('StudentID.txt') > lastmodified:
                    self.studentdata = self.read_studentdata()
                    lastmodified = os.path.getmtime('StudentID.txt')
                time.sleep(1)
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCheckInSystem(root)
    root.mainloop()
