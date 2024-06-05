import tkinter as tk
from tkinter import messagebox, scrolledtext
import re

class StudentInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("security logs placeholder")
        self.root.configure(bg='#262B33') 

        self.create_widgets()

    def create_widgets(self):
        bold_font = ('Helvetica', 10, 'bold') 
        text_bg_color = '#1F2328'  
#---------------wdget customize---------------#
        tk.Label(self.root, text="enter student ID:", bg='#262B33', fg='white', font=bold_font).grid(row=0, column=0, padx=10, pady=10)
        self.student_id_entry = tk.Entry(self.root)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=10)
        self.fetch_info_button = tk.Button(self.root, text="grab info",bg='#363e4a', fg='white', command=self.fetch_student_info, font=bold_font)
        self.fetch_info_button.grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="student info:", bg='#262B33', fg='white', font=bold_font).grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.student_info_text = scrolledtext.ScrolledText(self.root, width=50, height=10, font=bold_font, bg=text_bg_color, fg='white')
        self.student_info_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="student logs:", bg='#262B33', fg='white', font=bold_font).grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.student_logs_text = scrolledtext.ScrolledText(self.root, width=50, height=10, font=bold_font, bg=text_bg_color, fg='white')
        self.student_logs_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="all logs:", bg='#262B33', fg='white', font=bold_font).grid(row=0, column=3, padx=10, pady=10)
        self.all_logs_text = scrolledtext.ScrolledText(self.root, width=50, height=20, font=bold_font, bg=text_bg_color, fg='white')
        self.all_logs_text.grid(row=1, column=3, rowspan=4, padx=10, pady=10)

        self.load_all_logs()

    def fetch_student_info(self):
        student_id = self.student_id_entry.get()
        if not student_id.isdigit():
            messagebox.showerror("error", "please enter valid student ID")
            return
        
        student_info = self.get_student_info(student_id)
        student_logs = self.get_student_logs(student_id)
        
        self.student_info_text.delete(1.0, tk.END)
        self.student_logs_text.delete(1.0, tk.END)
        
        if student_info:
            self.student_info_text.insert(tk.END, student_info)
        else:
            self.student_info_text.insert(tk.END, "student ID not found")
        
        if student_logs:
            self.student_logs_text.insert(tk.END, student_logs)
        else:
            self.student_logs_text.insert(tk.END, "mo logs found for this student")

    def get_student_info(self, student_id):
        try:
            with open('studentID.txt', 'r') as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip()
                if re.match(f'^studentID:\({student_id}\)', line):
                    name_match = re.search(r'Name\((.*?)\)', line)
                    history_match = re.search(r'History\((.*?)\)', line)

                    if name_match and history_match:
                        name = name_match.group(1)
                        history = history_match.group(1)
                        return f"Name: {name}\nHistory: {history}"

        except FileNotFoundError:
            messagebox.showerror("error", "StudentID.txt file not found")
        return None

    def get_student_logs(self, student_id):
        logs = []
        try:
            with open('checkinlog.txt', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if f'studentid:({student_id})' in line:
                        logs.append(line.strip())
        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")
        
        return "\n".join(logs) if logs else None

    def load_all_logs(self):
        try:
            with open('checkinlog.txt', 'r') as file:
                all_logs = file.read()
                self.all_logs_text.insert(tk.END, all_logs)
        except FileNotFoundError:
            messagebox.showerror("error", "checkinlog.txt file not found")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentInfoApp(root)
    root.mainloop()
