import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import time

class StudentInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("security log")
        self.root.configure(bg='#262B33')

        self.timeoutstudents = {}
        self.create_widgets()
        self.update_logs()

    def create_widgets(self):
        boldfont = ('Helvetica', 10, 'bold')
        textbgcolor = '#1F2328'

        tk.Label(self.root, text="enter student ID:", bg='#262B33', fg='white', font=boldfont).grid(row=0, column=0, padx=10, pady=10)
        self.studentidentry = tk.Entry(self.root)
        self.studentidentry.grid(row=0, column=1, padx=10, pady=10)
        self.fetchinfobutton = tk.Button(self.root, text="fetch info", bg='#363e4a', fg='white', command=self.fetch_studentinfo, font=boldfont)
        self.fetchinfobutton.grid(row=0, column=2, padx=10, pady=10)

        self.timeoutbutton = tk.Button(self.root, text="timeout", bg='#363e4a', fg='white', command=self.timeout_student, font=boldfont)
        self.timeoutbutton.grid(row=0, column=3, padx=10, pady=10)

        self.recalltimeoutbutton = tk.Button(self.root, text="recall timeout", bg='#363e4a', fg='white', command=self.revoke_timeout, font=boldfont)
        self.recalltimeoutbutton.grid(row=0, column=4, padx=10, pady=10)

        tk.Label(self.root, text="student info:", bg='#262B33', fg='white', font=boldfont).grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.studentinfotext = scrolledtext.ScrolledText(self.root, width=50, height=10, font=boldfont, bg=textbgcolor, fg='white')
        self.studentinfotext.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="student logs:", bg='#262B33', fg='white', font=boldfont).grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.studentlogstext = scrolledtext.ScrolledText(self.root, width=50, height=10, font=boldfont, bg=textbgcolor, fg='white')
        self.studentlogstext.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="all logs:", bg='#262B33', fg='white', font=boldfont).grid(row=0, column=5, columnspan=2, padx=10, pady=10)
        self.alllogstext = scrolledtext.ScrolledText(self.root, width=60, height=20, font=boldfont, bg=textbgcolor, fg='white')
        self.alllogstext.grid(row=1, column=5, rowspan=4, columnspan=2, padx=10, pady=10)

    def fetch_studentinfo(self):
        studentid = self.studentidentry.get().strip()
        if not studentid.isdigit():
            messagebox.showerror("error", "please enter valid student ID")
            return

        studentdata = self.read_studentdata()
        if studentid in studentdata:
            name, history, timeout = studentdata[studentid]
            info = f"Student ID: {studentid}\nName: {name}\nTimeout: {'Yes' if timeout else 'No'}\nHistory: {history}"
            self.studentinfotext.delete(1.0, tk.END)
            self.studentinfotext.insert(tk.END, info)
        else:
            messagebox.showerror("error", "student ID not found")

    def timeout_student(self):
        studentid = self.studentidentry.get().strip()
        studentdata = self.read_studentdata()
        if studentid in studentdata:
            self.timeoutstudents[studentid] = time.time()
            messagebox.showinfo("timeout", f"student ID {studentid} is in timeout")
        else:
            messagebox.showerror("error", "student ID not found")

    def revoke_timeout(self):
        studentid = self.studentidentry.get().strip()
        if studentid in self.timeoutstudents:
            del self.timeoutstudents[studentid]
            messagebox.showinfo("timeout revoked", f"timeout revoked for Student ID {studentid}")
        else:
            messagebox.showerror("error", "student ID not in timeout")

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

    def update_logs(self):
        try:
            with open('checkinlog.txt', 'r') as file:
                logs = file.read()
            self.alllogstext.delete(1.0, tk.END)
            self.alllogstext.insert(tk.END, logs)
        except FileNotFoundError:
            self.alllogstext.delete(1.0, tk.END)
            self.alllogstext.insert(tk.END, "no logs found")

        self.root.after(10000, self.update_logs)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentInfoApp(root)
    root.mainloop()
