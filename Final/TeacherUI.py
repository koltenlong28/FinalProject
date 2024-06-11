import tkinter as tk
from tkinter import messagebox
import re
import time
import threading
import socket
import json
import datetime

class TeacherUI:
    def __init__(self, root):
        self.root = root
        self.root.title("teacher UI")
        self.root.configure(bg="#262B33")

        self.studentframes = {}
        self.studentstatus = {}

        self.create_widgets()
        self.updatestudentstatusthread = threading.Thread(target=self.update_studentstatus)
        self.updatestudentstatusthread.daemon = True
        self.updatestudentstatusthread.start()

        self.start_socket_server()

    def create_widgets(self):
        fontstyle = ("Arial", 10, "bold")

        self.addstudententry = tk.Entry(self.root, font=fontstyle)
        self.addstudententry.grid(row=0, column=0, padx=10, pady=10)

        self.addstudentbutton = tk.Button(
            self.root, text="add student", command=self.add_student, 
            font=fontstyle, bg="#363e4a", fg="white"
        )
        self.addstudentbutton.grid(row=0, column=1, padx=10, pady=10)

    def add_student(self):
        studentid = self.addstudententry.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter valid student ID")
            return

        studentinfo = self.get_studentinfo(studentid)
        if not studentinfo:
            messagebox.showerror("error", "student ID not found")
            return

        if studentid not in self.studentframes:
            frame = tk.Frame(self.root, bg="grey", padx=10, pady=10)
            frame.grid(row=len(self.studentframes) + 1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            label = tk.Label(frame, text=studentinfo, bg="grey", fg="white", font=("Arial", 10, "bold"))
            label.pack(fill="x")

            self.studentframes[studentid] = frame
            self.studentstatus[studentid] = {"status": "grey", "starttime": None}

    def get_studentinfo(self, studentid):
        try:
            with open('StudentID.txt', 'r') as file:
                for line in file:
                    match = re.match(r'studentID:\((\d+)\),name\(([^,]+),([^,]+)\),history\(([^)]+)\),timeout\((\w+)\)', line.strip())
                    if match and match.group(1) == studentid:
                        lastname, firstname = match.group(2), match.group(3)
                        return f"{firstname} {lastname}"
        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        return None

    def update_studentstatus(self):
        while True:
            time.sleep(1)
            for studentid, statusinfo in self.studentstatus.items():
                if statusinfo["starttime"] is not None:
                    elapsedtime = datetime.datetime.now() - statusinfo["starttime"]
                    newstatus = "grey"
                    if elapsedtime.total_seconds() >= 420:
                        newstatus = "#de3c3c"
                    elif elapsedtime.total_seconds() >= 300:
                        newstatus = "#decb3c"
                    elif elapsedtime.total_seconds() >= 0:
                        newstatus = "#2cbf33"

                    if newstatus != statusinfo["status"]:
                        self.update_student_frame_color(studentid, newstatus)
                        self.studentstatus[studentid]["status"] = newstatus

    def update_student_frame_color(self, studentid, color):
        if studentid in self.studentframes:
            frame = self.studentframes[studentid]
            frame.configure(bg=color)
            label = frame.winfo_children()[0]
            label.configure(bg=color)

    def update_checkin_status(self, studentid):
        if studentid in self.studentstatus:
            self.studentstatus[studentid]["status"] = "#2cbf33"
            self.studentstatus[studentid]["starttime"] = datetime.datetime.now()
            self.update_student_frame_color(studentid, "#2cbf33")

    def update_checkout_status(self, studentid):
        if studentid in self.studentstatus:
            self.studentstatus[studentid]["status"] = "grey"
            self.studentstatus[studentid]["starttime"] = None
            self.update_student_frame_color(studentid, "grey")

    def start_socket_server(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', 65432))
        serversocket.listen(5)

        def handle_client(clientsocket):
            while True:
                try:
                    message = clientsocket.recv(1024).decode('utf-8')
                    if message:
                        data = json.loads(message)
                        studentid = data.get('studentid')
                        action = data.get('action')
                        if action == 'check_in':
                            self.update_checkin_status(studentid)
                        elif action == 'check_out':
                            self.update_checkout_status(studentid)
                    else:
                        break
                except Exception as e:
                    print(f"error: {e}")
                    break
            clientsocket.close()

        def accept_clients():
            while True:
                clientsocket, addr = serversocket.accept()
                clienthandler = threading.Thread(target=handle_client, args=(clientsocket,))
                clienthandler.daemon = True
                clienthandler.start()

        acceptthread = threading.Thread(target=accept_clients)
        acceptthread.daemon = True
        acceptthread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherUI(root)
    root.mainloop()
