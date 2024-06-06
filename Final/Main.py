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
        self.root.title("student checkin system")
        self.root.configure(bg="#262B33")

        self.studentidvar = tk.StringVar()
        self.starttime = None
        self.studentdata = self.readstudentdata()

        self.createwidgets()
        self.filemonitorthread = threading.Thread(target=self.checkstudentfile)
        self.filemonitorthread.daemon = True
        self.filemonitorthread.start()

        self.serveraddress = ('localhost', 65432)

    def createwidgets(self):
        fontstyle = ("Arial", 10, "bold")
        tk.Label(self.root, text="enter student ID:", bg="#262B33", fg="white", font=fontstyle).grid(row=0, column=0, padx=10, pady=10)
        self.studentidentry = tk.Entry(self.root, textvariable=self.studentidvar, font=fontstyle)
        self.studentidentry.grid(row=0, column=1, padx=10, pady=10)

        self.checkinbutton = tk.Button(self.root, text="check in", command=self.checkin, font=fontstyle, bg="#363e4a", fg="white")
        self.checkinbutton.grid(row=1, column=0, columnspan=2, pady=10)

        self.checkoutbutton = tk.Button(self.root, text="check out", command=self.checkout, state=tk.DISABLED, font=fontstyle, bg="#363e4a", fg="white")
        self.checkoutbutton.grid(row=2, column=0, columnspan=2, pady=10)

    def readstudentdata(self):
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
            messagebox.showerror("error", "studentID.txt file not found")
        except Exception as e:
            messagebox.showerror("error", f"error reading student data: {str(e)}")
        return studentdata

    def writestudentdata(self):
        with open('StudentID.txt', 'w') as file:
            for studentid, (name, historydict, timeout) in self.studentdata.items():
                historystr = ', '.join(f'{key}:{value}' for key, value in historydict.items())
                file.write(f'studentID:({studentid}),name({name}),history({historystr}),timeout({timeout})\n')

    def checkin(self):
        studentid = self.studentidvar.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        if studentid not in self.studentdata:
            messagebox.showerror("error", "student ID not found")
            return

        name, history, timeout = self.studentdata[studentid]

        if timeout:
            messagebox.showerror("error", "you are in timeout")
            return

        self.studentdata[studentid][1]['excuses'] += 1
        self.writestudentdata()

        self.starttime = time.time()
        self.checkinbutton.config(state=tk.DISABLED)
        self.checkoutbutton.config(state=tk.NORMAL)
        checkintime = time.strftime('%H:%M:%S', time.localtime(self.starttime))
        messagebox.showinfo("checked in", f"student ID {studentid} checked in at {checkintime}")

        self.sendstatusupdate(studentid, "check_in")

    def checkout(self):
        if not self.starttime:
            messagebox.showerror("error", "you must check in first")
            return

        endtime = time.time()
        duration = endtime - self.starttime
        durationminutes = duration / 60
        studentid = self.studentidvar.get()
        checkouttime = time.strftime('%H:%M:%S', time.localtime(endtime))

        if durationminutes > 7:
            self.studentdata[studentid][1]['bathroomviolations'] += 1
            self.studentdata[studentid] = (self.studentdata[studentid][0], self.studentdata[studentid][1], True)

        with open('checkinlog.txt', 'a') as file:
            file.write(f'studentID:({studentid}),timeinbathroom({durationminutes:.2f} minutes),timeofcheckin({checkouttime})\n')

        messagebox.showinfo("checked out", f"student ID {studentid} checked out. duration: {durationminutes:.2f} minutes")

        self.writestudentdata()

        self.starttime = None
        self.studentidvar.set("")
        self.checkinbutton.config(state=tk.NORMAL)
        self.checkoutbutton.config(state=tk.DISABLED)

        self.sendstatusupdate(studentid, "check_out")

    def sendstatusupdate(self, studentid, action):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.serveraddress)
                message = json.dumps({"student_id": studentid, "action": action})
                sock.sendall(message.encode('utf-8'))
        except ConnectionRefusedError:
            messagebox.showerror("error", "could not conect teacher UI")

    def checkstudentfile(self):
        try:
            lastmodified = os.path.getmtime('StudentID.txt')
            while True:
                if os.path.getmtime('StudentID.txt') > lastmodified:
                    self.studentdata = self.readstudentdata()
                    lastmodified = os.path.getmtime('StudentID.txt')
                time.sleep(1)
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCheckInSystem(root)
    root.mainloop()
