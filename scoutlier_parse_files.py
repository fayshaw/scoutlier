#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 20:58:35 2023

@author: fayshaw
"""

# Load packages
import pandas as pd
import numpy as np
import re
import os
from datetime import datetime


# functions
def parse_row_headers(step_info_df):
    """
    From raw data, parse row headers into separate rows: 
    'Task (1) Desc Text' becomes Task Number: 1, Task Description: Desc Text
    Returns increment step column (Inc Step)
    Returns lesson data - this is common for each student

    """
    lesson_data = []

    inc_col = [] # column of incremental step numbers

    for row_head in step_info_df:
        new_row = []

        if row_head == 'Assignment Name':
            inc_ind = 'a'
            inc_col.append(inc_ind)

        elif row_head in student_lesson_cols:  # Student lesson stats 
            inc_ind = 0
            inc_col.append(inc_ind)

        elif row_head in student_grade_cols: # Completed, Time Spent, etc
            inc_col.append(inc_ind)           

        else: # if '(' in row_head, split into step, number, and description
            splits = re.split(r'(\(\d+\)|\s-\s)', row_head)

            step = splits[0].strip()
            num = re.sub(r"\(|\)", "", splits[1]) #strip ( ) from number
            desc = splits[2].strip()

            if step == 'Task':  # set task and description for following entries
                task_num = num
                task_desc = desc
                inc_col.append('t' + num)
                continue

            if step in step_type_list:
                if step == 'Accessed':
                    inc_ind += 1
                    step_num = 'A' + num
                    step_type = 'Accessed'    

            elif step == 'Step':
                inc_ind += 1
                step_num = num

                if len(splits) > 3:
                    step_type = splits[-1].strip()
                    new_row.append(step_type.strip())

                    if step_type == 'Audio':
                        print(lesson_num, '\b: audio')
                    elif step_type == 'Video':
                        print(lesson_num, '\b: video')


                else:
                    new_row.append("")

            inc_col.append(inc_ind)        
            lesson_data.append([inc_ind, task_num, task_desc, step_num, desc, step_type])

    return lesson_data, inc_col


def reshape_student_data(student_number):
    """
    Populates dictionary with student data and reshapes it to a table 
    """
    # Initialize a dictionary to store the reshaped student data
    student_data_dict = {}

    # Iterate through the original data and organize it in the dictionary
    for index, row in data_df[['Inc step', 'Step Info', student_number]].iterrows():
        index, header, value = row

        if not str(index).isnumeric() or index == 0:
            continue

        if index not in student_data_dict:  # if empty, make a new row
            student_data_dict[index] = {'Inc step': index}            

        if 'Accessed' in header:
            student_data_dict[index]['Completed'] = value
#        elif 'Video Length' in header:
#            student_data_dict[index]['Paragraph Length'] = value        
        else:
            student_data_dict[index][header] = value

    # Convert the dictionary back to a list of lists
    reshaped_student_data = [[row.get(s, '') for s in student_grade_cols_numbered[1:]] for row in student_data_dict.values()]

    return reshaped_student_data


def parse_time(str_sec):    
    splits = re.split('m|s', str_sec)
    num_minutes = splits[0]
    num_seconds = splits[1]
    total_seconds = int(num_minutes)*60 + int(num_seconds)
    return total_seconds

def parse_chars(str_char):
    num_chars = re.split('Character', str_char)[0]    
    return num_chars


def read_class_data(data_df):
    """
    Read all students in a classroom, writes to table
    """
    student_grades = []
    all_student_data = []

    student_numbers = data_df.columns[2:-2] # student number list, omit last columns with averages 

    for sn in student_numbers:    
        # st_lesson_info format is lesson_num + student_lesson_cols    
        time_spent = data_df[sn][2] 
        if isinstance (time_spent, str):
            data_df[sn][2] = parse_time(time_spent) 
        st_lesson_info = list(data_df[sn][0:5])  # same for all rows for one student

        # Reformat date string to MM-DD-YY
        date_string = st_lesson_info[1]
        if date_string is not np.nan:
            # Convert string to datetime object
            datetime_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

            # Format datetime object to the desired format
            formatted_date = datetime_object.strftime('%m/%d/%y')
            st_lesson_info[1] = formatted_date

        # Reformat completion percent at string with %
        grade = st_lesson_info[3]
        if grade is not np.nan:
            decimal_value = float(grade)
            percent_string = "{:.0%}".format(decimal_value)
            st_lesson_info[3] = percent_string

        # Create current row
        current_student_row = [teacher, sn]  
        current_student_row.extend(st_lesson_info)
        student_grades.append(current_student_row)

        student_data_table = reshape_student_data(sn)
        current_student_data = [current_student_row + row1 + row2 for row1, row2 in zip(lesson_data, student_data_table)]

        all_student_data.extend(current_student_data)

    return all_student_data


# File path
f_splits = re.split('\(|\)|\s', folder_path)
teacher = f_splits[4]

# List all files in the folder
files = os.listdir(folder_path)


# This data will be the same for each row of one student
student_lesson_cols     = ['Last Date Worked on', 'Time Spent on Lesson', 'Percent Complete', 'Grade']
student_lesson_cols_out = [student_lesson_cols[0], 'Time Spent on Lesson (sec)'] + student_lesson_cols[2:] # added sec

student_grade_cols     =  ['Completed', 'Time Spent on Step', 'Reviewed Peer Responses', 'Paragraph Length',
                           'Video Length', 'Audio Length']
student_grade_cols_out =  ['Completed', 'Time Spent on Step (sec)', 'Reviewed Peer Responses', 'Paragraph Length (char)',
                           'Video Length (sec)', 'Audio Length (sec)'] # added sec, char

# student completion is similar except with Inc Step Num and without Video and Audio Length
student_grade_cols_numbered = ['Inc Step Num'] + student_grade_cols  # Do I need this?


step_type_list = ['Accessed', 'Paragraph', 'Single Select', 'Image', 'Table', 'Video', 'Audio']

# This lesson data will be same for each student
lesson_cols = ['Inc Step Num', 'Task Number', 'Task Description', 'Step Number', 'Step Description', 'Step Type']

lessons = []

for f in files:

    # Lesson name from file
    pattern = r'-\s*(.*?)\.'
    lesson = re.search(pattern, f)
    lesson_num = lesson[1]
    lessons.append(lesson_num)
    
    # File names
    file_path = 'DI Copy of EngagementReport - ' + lesson_num + '.xlsx'

    # Read file
    data_df = pd.read_excel(folder_path + file_path, dtype=str) 

    # Initial processing
    data_df.columns = data_df.columns.astype(str)   # read student names as strings
    data_df = data_df.dropna(how='all')             # drop empty rows
    data_df = data_df.reset_index(drop=True)        # reset index, drop column called index 
    data_df = data_df.rename({'Student Name' : 'Step Info'}, axis='columns') # rename column header to better describe the data
    
    # Get lesson data that is common for the whole class that numbers all the steps
    lesson_data, inc_col = parse_row_headers(data_df['Step Info'])
    
    data_df.insert(0, 'Inc step', inc_col) # insert Inc step column into data_df
    
    # Write data to student dataframe
    new_col_titles = ['Teacher', 'Student Name'] + [lesson_num] + student_lesson_cols_out + lesson_cols + student_grade_cols_out
    all_df = pd.DataFrame(read_class_data(data_df), columns=new_col_titles)

    # Write files
    output_file_name = 'output_data_' + teacher + '_' + lesson_num

 #   all_df.to_excel(output_file_name + '.xlsx', index=False)
    all_df.to_csv(output_file_name + '.csv', index=False)


    lesson_df = pd.DataFrame(lesson_data, columns=lesson_cols)
    lesson_file_name = 'lesson_data_' + lesson_num

    # Write csv for each lesson
    #    lesson_df.to_csv(output_lesson_data + '.csv', index=False)

    # Write lesson data to one Excel sheet with one tab per lesson
    
    # Or use excel writer?
    lesson_df.to_excel('lesson_data.xlsx', sheet_name=lesson_num)

