import re

def get_student_info(student_id):
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
                

                print(f"name({name}),history({history})")
                return
            
    print("student ID not found")

input_student_id = input("enter student ID: ")

get_student_info(input_student_id)
