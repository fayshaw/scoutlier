# Scoutlier
Data cleaning and organization for Scoutlier project

Input data has a format with lesson data in row headers and student data as columns.  
Output is transposed with lesson data parsed as columns and student completion for each lesson description.

Output column headers are student_lesson_columns + lesson_colummns + student_grade_columns 
student_lesson_columns = ['Teacher', 'Student Name', 'Lesson', 'Last Date Worked on', 'Time Spent on Lesson', 'Percent Complete', 'Grade'] 
lesson_columns = ['Inc Step Num', 'Task Number', 'Task Description', 'Step Number', 'Step Description', 'Step Type']
student_grade_columns = ['Completed', 'Time Spent on Step (sec)', 'Reviewed Peer Responses', 'Paragraph Length (char)', 'Video Length (sec)', 'Audio Length (sec)']
