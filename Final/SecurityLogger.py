import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import time

class StudentInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("security log placeholder")
        self.root.configure(bg='#262B33')

        self.timeoutstudents = {}
        self.createwidgets()
        self.updatelogs()

    def createwidgets(self):
        boldfont = ('Helvetica', 10, 'bold')
        textbgcolor = '#1F2328'

        tk.Label(self.root, text="enter student ID:", bg='#262B33', fg='white', font=boldfont).grid(row=0, column=0, padx=10, pady=10)
        self.studentidentry = tk.Entry(self.root)
        self.studentidentry.grid(row=0, column=1, padx=10, pady=10)
        self.fetchinfobutton = tk.Button(self.root, text="grab info", bg='#363e4a', fg='white', command=self.fetchstudentinfo, font=boldfont)
        self.fetchinfobutton.grid(row=0, column=2, padx=10, pady=10)

        self.timeoutbutton = tk.Button(self.root, text="timeout", bg='#363e4a', fg='white', command=self.timeoutstudent, font=boldfont)
        self.timeoutbutton.grid(row=0, column=3, padx=10, pady=10)

        self.recalltimeoutbutton = tk.Button(self.root, text="recall timeout", bg='#363e4a', fg='white', command=self.revoketimeout, font=boldfont)
        self.recalltimeoutbutton.grid(row=0, column=4, padx=10, pady=10)

        tk.Label(self.root, text="student info:", bg='#262B33', fg='white', font=boldfont).grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.studentinfotext = scrolledtext.ScrolledText(self.root, width=50, height=10, font=boldfont, bg=textbgcolor, fg='white')
        self.studentinfotext.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="student logs:", bg='#262B33', fg='white', font=boldfont).grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.studentlogstext = scrolledtext.ScrolledText(self.root, width=50, height=10, font=boldfont, bg=textbgcolor, fg='white')
        self.studentlogstext.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="all logs:", bg='#262B33', fg='white', font=boldfont).grid(row=0, column=5, padx=10, pady=10)
        self.alllogstext = scrolledtext.ScrolledText(self.root, width=50, height=20, font=boldfont, bg=textbgcolor, fg='white')
        self.alllogstext.grid(row=1, column=5, rowspan=4, padx=10, pady=10)

    def fetchstudentinfo(self):
        studentid = self.studentidentry.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        studentinfo = self.getstudentinfo(studentid)
        studentlogs = self.getstudentlogs(studentid)

        self.studentinfotext.delete(1.0, tk.END)
        self.studentlogstext.delete(1.0, tk.END)

        if studentinfo:
            self.studentinfotext.insert(tk.END, studentinfo)
        else:
            self.studentinfotext.insert(tk.END, "student ID not found")

        if studentlogs:
            self.studentlogstext.insert(tk.END, studentlogs)
        else:
            self.studentlogstext.insert(tk.END, "no logs found for student")

    def getstudentinfo(self, studentid):
        try:
            with open('StudentID.txt', 'r') as file:
                for line in file:
                    match = re.match(r'studentID:\((\d+)\),name\(([^)]+)\),history\(([^)]+)\),timeout\((\w+)\)', line.strip())
                    if match and match.group(1) == studentid:
                        name = match.group(2)
                        history = match.group(3)
                        timeout = match.group(4)
                        return f"mame: {name}\nhistory: {history}\ntimeout: {timeout}"

        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        return None

    def getstudentlogs(self, studentid):
        logs = []
        try:
            with open('checkinlog.txt', 'r') as file:
                for line in file:
                    if f'studentID:({studentid})' in line:
                        logs.append(line.strip())

        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")

        return "\n".join(logs) if logs else None

    def loadalllogs(self):
        try:
            with open('checkinlog.txt', 'r') as file:
                alllogs = file.read()
                self.alllogstext.delete(1.0, tk.END)
                self.alllogstext.insert(tk.END, alllogs)

        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")

    def updatelogs(self):
        scrollposition = self.alllogstext.yview()[0]
        self.loadalllogs()
        self.alllogstext.yview_moveto(scrollposition)
        self.root.after(1000, self.updatelogs)

    def timeoutstudent(self):
        studentid = self.studentidentry.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        timeoutduration = 6000
        self.timeoutstudents[studentid] = time.time() + timeoutduration

        self.updatetimeoutstatus(studentid, True)
        messagebox.showinfo("timed out", f"student ID {studentid} timed out")

    def revoketimeout(self):
        studentid = self.studentidentry.get()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        if studentid in self.timeoutstudents:
            del self.timeoutstudents[studentid]
            self.updatetimeoutstatus(studentid, False)
            messagebox.showinfo("timeout revoked", f"timeout for student ID {studentid} has been revoked")

    def updatetimeoutstatus(self, studentid, status):
        try:
            with open('StudentID.txt', 'r') as file:
                lines = file.readlines()

            with open('StudentID.txt', 'w') as file:
                for line in lines:
                    match = re.match(r'studentID:\((\d+)\),name\(([^)]+)\),history\(([^)]+)\),timeout\((\w+)\)', line.strip())
                    if match and match.group(1) == studentid:
                        line = f"studentID:({studentid}),name({match.group(2)}),history({match.group(3)}),timeout({status})\n"
                    file.write(line)

        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentInfoApp(root)
    root.mainloop()
