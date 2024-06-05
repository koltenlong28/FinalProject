import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import time

class StudentInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("security log placeholder")
        self.root.configure(bg='#262B33') 

        self.timeout_students = {} 
        self.create_widgets()
        self.update_logs() 

    def create_widgets(self):
        bold_font = ('Helvetica', 10, 'bold') 
        text_bg_color = '#1F2328'  

        tk.Label(self.root, text="enter student ID:", bg='#262B33', fg='white', font=bold_font).grid(row=0, column=0, padx=10, pady=10)
        self.studentID_entry = tk.Entry(self.root)
        self.studentID_entry.grid(row=0, column=1, padx=10, pady=10)
        self.fetch_info_button = tk.Button(self.root, text="grab info", bg='#363e4a', fg='white', command=self.fetch_student_info, font=bold_font)
        self.fetch_info_button.grid(row=0, column=2, padx=10, pady=10)

        self.timeout_button = tk.Button(self.root, text="timeout", bg='#363e4a', fg='white', command=self.timeout_student, font=bold_font)
        self.timeout_button.grid(row=0, column=3, padx=10, pady=10)

        self.recall_timeout_button = tk.Button(self.root, text="recall timeout", bg='#363e4a', fg='white', command=self.revoke_timeout, font=bold_font)
        self.recall_timeout_button.grid(row=0, column=4, padx=10, pady=10)

        tk.Label(self.root, text="student info:", bg='#262B33', fg='white', font=bold_font).grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.student_info_text = scrolledtext.ScrolledText(self.root, width=50, height=10, font=bold_font, bg=text_bg_color, fg='white')
        self.student_info_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="atudent logs:", bg='#262B33', fg='white', font=bold_font).grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.student_logs_text = scrolledtext.ScrolledText(self.root, width=50, height=10, font=bold_font, bg=text_bg_color, fg='white')
        self.student_logs_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="all logs:", bg='#262B33', fg='white', font=bold_font).grid(row=0, column=5, padx=10, pady=10)
        self.all_logs_text = scrolledtext.ScrolledText(self.root, width=50, height=20, font=bold_font, bg=text_bg_color, fg='white')
        self.all_logs_text.grid(row=1, column=5, rowspan=4, padx=10, pady=10)    

    def fetch_student_info(self):
        studentID = self.studentID_entry.get()
        if not studentID.isdigit():
            messagebox.showerror("error", "please enter valid student ID")
            return
        
        student_info = self.get_student_info(studentID)
        student_logs = self.get_student_logs(studentID)
        
        self.student_info_text.delete(1.0, tk.END)
        self.student_logs_text.delete(1.0, tk.END)
        
        if student_info:
            self.student_info_text.insert(tk.END, student_info)
        else:
            self.student_info_text.insert(tk.END, "student ID not found")
        
        if student_logs:
            self.student_logs_text.insert(tk.END, student_logs)
        else:
            self.student_logs_text.insert(tk.END, "no logs found for student")

    def get_student_info(self, studentID):
        try:
            with open('StudentID.txt', 'r') as file:
                for line in file:
                    match = re.match(r'studentID:\((\d+)\),Name\(([^)]+)\),History\(([^)]+)\)', line.strip())
                    if match and match.group(1) == studentID:
                        name = match.group(2)
                        history = match.group(3)
                        return f"name: {name}\nhistory: {history}"

        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        return None

    def get_student_logs(self, studentID):
        logs = []
        try:
            with open('checkinlog.txt', 'r') as file:
                for line in file:
                    if f'studentID:({studentID})' in line:
                        logs.append(line.strip())

        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")
        
        return "\n".join(logs) if logs else None

    def load_all_logs(self):
        try:
            with open('checkinlog.txt', 'r') as file:
                all_logs = file.read()
                self.all_logs_text.delete(1.0, tk.END)
                self.all_logs_text.insert(tk.END, all_logs)

        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")

    def update_logs(self):
        scroll_position = self.all_logs_text.yview()[0]
        self.load_all_logs()
        self.all_logs_text.yview_moveto(scroll_position)
        self.root.after(1000, self.update_logs) 

    def timeout_student(self):
        studentID = self.studentID_entry.get()
        if not studentID.isdigit():
            messagebox.showerror("error", "please enter a valid student ID")
            return

        timeout_duration = 6000
        self.timeout_students[studentID] = time.time() + timeout_duration
        messagebox.showinfo("timed out", f"student ID {studentID} timed out")

    def revoke_timeout(self):
        studentID = self.studentID_entry.get()
        if not studentID.isdigit():
            messagebox.showerror("error", "please wnter valid student ID")
            return

        if studentID in self.timeout_students:
            del self.timeout_students[studentID]
            messagebox.showinfo("timeout revoked", f"timeout student ID {studentID} has been revoked")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentInfoApp(root)
    root.mainloop()
