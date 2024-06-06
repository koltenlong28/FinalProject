import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import time
import threading
import socket
import json

class TeacherUI:
    def __init__(self, root):
        self.root = root
        self.root.title("teacher UI")
        self.root.configure(bg="#262B33")

        self.studentframes = {}
        self.studentstatus = {}

        self.createwidgets()
        self.updatestudentstatusthread = threading.Thread(target=self.updatestudentstatus)
        self.updatestudentstatusthread.daemon = True
        self.updatestudentstatusthread.start()

        self.startsocketserver()

    def createwidgets(self):
        fontstyle = ("Arial", 10, "bold")

        self.addstudententry = tk.Entry(self.root, font=fontstyle)
        self.addstudententry.grid(row=0, column=0, padx=10, pady=10)
        
        self.addstudentbutton = tk.Button(self.root, text="add student", command=self.addstudent, font=fontstyle, bg="#363e4a", fg="white")
        self.addstudentbutton.grid(row=0, column=1, padx=10, pady=10)

    def addstudent(self):
        studentid = self.addstudententry.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        studentinfo = self.getstudentinfo(studentid)
        if not studentinfo:
            messagebox.showerror("error", "student ID not found")
            return

        if studentid not in self.studentframes:
            frame = tk.Frame(self.root, bg="grey", padx=10, pady=10)
            frame.grid(row=len(self.studentframes)+1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            label = tk.Label(frame, text=studentinfo, bg="grey", fg="white", font=("Arial", 10, "bold"))
            label.pack(fill="x")

            self.studentframes[studentid] = frame
            self.studentstatus[studentid] = {"status": "grey", "starttime": None}

    def getstudentinfo(self, studentid):
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

    def updatestudentstatus(self):
        while True:
            time.sleep(1)
            for studentid, statusinfo in self.studentstatus.items():
                if statusinfo["starttime"] is not None:
                    elapsedtime = time.time() - statusinfo["starttime"]
                    newstatus = "grey"
                    if elapsedtime >= 420:  # 7 minutes in seconds
                        newstatus = "#de3c3c"
                    elif elapsedtime >= 300:  # 5 minutes in seconds
                        newstatus = "#decb3c"
                    elif elapsedtime >= 0:
                        newstatus = "#2cbf33"

                    if newstatus != statusinfo["status"]:
                        self.updatestudentframecolor(studentid, newstatus)
                        self.studentstatus[studentid]["status"] = newstatus

    def updatestudentframecolor(self, studentid, color):
        if studentid in self.studentframes:
            frame = self.studentframes[studentid]
            frame.configure(bg=color)
            label = frame.winfo_children()[0]
            label.configure(bg=color)

    def updatecheckinstatus(self, studentid):
        if studentid in self.studentstatus:
            self.studentstatus[studentid]["status"] = "#2cbf33"
            self.studentstatus[studentid]["starttime"] = time.time()
            self.updatestudentframecolor(studentid, "#2cbf33")

    def updatecheckoutstatus(self, studentid):
        if studentid in self.studentstatus:
            self.studentstatus[studentid]["status"] = "grey"
            self.studentstatus[studentid]["starttime"] = None
            self.updatestudentframecolor(studentid, "grey")

    def startsocketserver(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', 65432))
        serversocket.listen(5)

        def handleclient(clientsocket):
            while True:
                try:
                    message = clientsocket.recv(1024).decode('utf-8')
                    if message:
                        data = json.loads(message)
                        studentid = data.get('student_id') 
                        action = data.get('action')
                        if action == 'check_in':  
                            self.updatecheckinstatus(studentid)
                        elif action == 'check_out':  
                            self.updatecheckoutstatus(studentid)
                    else:
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    break
            clientsocket.close()

        def acceptclients():
            while True:
                clientsocket, addr = serversocket.accept()
                clienthandler = threading.Thread(target=handleclient, args=(clientsocket,))
                clienthandler.daemon = True
                clienthandler.start()

        acceptthread = threading.Thread(target=acceptclients)
        acceptthread.daemon = True
        acceptthread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherUI(root)
    root.mainloop()
