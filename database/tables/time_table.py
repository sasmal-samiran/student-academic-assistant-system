### INSERT INTO -----
# faculty
# subject_allocation
# period_timeslot
# class_session
# timetable

import pandas as pd
def time_table(cursor):
    df = pd.read_csv("datasets/teachers.csv")
    for i in range(df.shape[0]):
        row=df.loc[i]
        department = str(row['department']).lower()
        faculty_name = str(row['faculty_name']).lower()
        designation = str(row['designation']).lower()
        cursor.execute("""INSERT INTO faculty (department, faculty_name, designation) VALUES (?, ?, ?);"""
                       , (department, faculty_name, designation))
        

    cursor.execute("""
        INSERT INTO subject_allocation (subject_code, faculty_id, section, semester) VALUES
        -- IoT Subject
        ('6CSECSDSVAC01', 1, 'A',  6),
                   ('6CSECSDSVAC01', 1, 'B',  6),
                   ('6CSECSDSVAC01', 1, 'C',  6),
                   ('6CSECSDSVAC01', 1, 'D',  6),
        ('6CSECSDSVAC01', 15, 'A', 6),
                   ('6CSECSDSVAC01', 15, 'B', 6),
                   ('6CSECSDSVAC01', 15, 'C', 6),
                   ('6CSECSDSVAC01', 15, 'D', 6),
        ('6CSECSDSVAC01', 8, 'A', 6),
                   ('6CSECSDSVAC01', 8, 'B', 6),
                   ('6CSECSDSVAC01', 8, 'C', 6),
                   ('6CSECSDSVAC01', 8, 'D', 6),

        -- PCC-CSD601
        ('PCC-CSD601', 1, 'A', 6),
        ('PCC-CSD601', 9, 'B', 6),
        ('PCC-CSD601', 8, 'C', 6),
        ('PCC-CSD601', 8, 'D', 6),

        -- PCC-CSD602
        ('PCC-CSD602', 2, 'A', 6),
        ('PCC-CSD602', 2, 'C', 6),
        ('PCC-CSD602', 17, 'D', 6),
        ('PCC-CSD602', 21, 'B', 6),

        -- PCC-CSD691 (ML Lab)
        ('PCC-CSD691', 1, 'A', 6),
        ('PCC-CSD691', 8, 'C', 6),
        ('PCC-CSD691', 9, 'C', 6),
        ('PCC-CSD691', 8, 'D', 6),
        ('PCC-CSD691', 9, 'D', 6),
        ('PCC-CSD691', 9, 'B', 6),
        ('PCC-CSD691', 6, 'A', 6),
        ('PCC-CSD691', 22, 'B', 6),

        -- PCC-CSD692 (DM Lab)
        ('PCC-CSD692', 2, 'C', 6),
        ('PCC-CSD692', 2, 'A', 6),
        ('PCC-CSD692', 17, 'D', 6),
        ('PCC-CSD692', 18, 'D', 6),
        ('PCC-CSD692', 18, 'A', 6),
        ('PCC-CSD692', 21, 'B', 6),
        ('PCC-CSD692', 5, 'B', 6),
        ('PCC-CSD692', 5, 'C', 6),

        -- PEC-CSD601A
        ('PEC-CSD601A', 10, 'A', 6),
        ('PEC-CSD601A', 10, 'B', 6),
        ('PEC-CSD601A', 10, 'C', 6),
        ('PEC-CSD601A', 10, 'D', 6),

        -- PEC-CSD601B
        ('PEC-CSD601B', 11, 'A', 6),
        ('PEC-CSD601B', 11, 'B', 6),
        ('PEC-CSD601B', 11, 'C', 6),
        ('PEC-CSD601B', 11, 'D', 6),

        -- PEC-CSD601C
        ('PEC-CSD601C', 3, 'B', 6),
        ('PEC-CSD601C', 12, 'A', 6),
        ('PEC-CSD601C', 12, 'C', 6),
        ('PEC-CSD601C', 12, 'D', 6),

        -- PEC-CSD602A
        ('PEC-CSD602A', 3, 'B', 6),
        ('PEC-CSD602A', 3, 'B', 6),
        ('PEC-CSD602A', 3, 'B', 6),
        ('PEC-CSD602A', 3, 'B', 6),

        -- PEC-CSD602B
        ('PEC-CSD602B', 13, 'A', 6),
        ('PEC-CSD602B', 13, 'B', 6),
        ('PEC-CSD602B', 13, 'C', 6),
        ('PEC-CSD602B', 13, 'D', 6),

        -- PEC-CSD602C
        ('PEC-CSD602C', 4, 'A', 6),
        ('PEC-CSD602C', 4, 'B', 6),
        ('PEC-CSD602C', 4, 'C', 6),
        ('PEC-CSD602C', 4, 'D', 6),

        -- PEC-CSD691A
        ('PEC-CSD691A', 10, 'A', 6),
        ('PEC-CSD691A', 11, 'A', 6),
        ('PEC-CSD691A', 10, 'B', 6),
        ('PEC-CSD691A', 11, 'B', 6),
        ('PEC-CSD691A', 10, 'C', 6),
        ('PEC-CSD691A', 11, 'C', 6),
        ('PEC-CSD691A', 10, 'D', 6),
        ('PEC-CSD691A', 11, 'D', 6),

        -- PEC-CSD691B
        ('PEC-CSD691B', 11, 'A', 6),
        ('PEC-CSD691B', 14, 'A', 6),
        ('PEC-CSD691B', 11, 'B', 6),
        ('PEC-CSD691B', 14, 'B', 6),
        ('PEC-CSD691B', 11, 'C', 6),
        ('PEC-CSD691B', 14, 'C', 6),
        ('PEC-CSD691B', 11, 'D', 6),
        ('PEC-CSD691B', 14, 'D', 6),

        -- PEC-CSD691C
        ('PEC-CSD691C', 3, 'A', 6),
        ('PEC-CSD691C', 12, 'A', 6),
        ('PEC-CSD691C', 3, 'B', 6),
        ('PEC-CSD691C', 12, 'B', 6),
        ('PEC-CSD691C', 6, 'C', 6),
        ('PEC-CSD691C', 12, 'C', 6),
        ('PEC-CSD691C', 6, 'D', 6),
        ('PEC-CSD691C', 12, 'D', 6),

        -- OEC Subjects
        ('OEC-CSD601A', 5, 'A', 6),
        ('OEC-CSD601A', 5, 'B', 6),
        ('OEC-CSD601A', 5, 'C', 6),
        ('OEC-CSD601A', 5, 'D', 6),
        ('OEC-CSD601B', 6, 'A', 6),
        ('OEC-CSD601B', 6, 'B', 6),
        ('OEC-CSD601B', 6, 'C', 6),
        ('OEC-CSD601B', 6, 'D', 6),
        ('OEC-CSD601C', 7, 'A', 6),
        ('OEC-CSD601C', 7, 'B', 6),
        ('OEC-CSD601C', 7, 'C', 6),
        ('OEC-CSD601C', 7, 'D', 6),

        -- Aptitude
        ('APT-601', 16, 'C', 6),
        ('APT-601', 20, 'B', 6),
        ('APT-601', 16, 'D', 6),
        ('APT-601', 20, 'A', 6),
                   
        -- VAC
        ('6BWUVAC01', 18, 'A', 6),
        ('6BWUVAC01', 5, 'B', 6),
        ('6BWUVAC01', 5, 'C', 6),
        ('6BWUVAC01', 18, 'D', 6);"""
    )

    df = pd.read_csv("datasets/period_timeslot.csv")
    for i in range(df.shape[0]):
        row=df.loc[i]
        period_id = int(row['period_id'])
        start_time = str(row['start_time'])
        end_time = str(row['end_time'])  
        cursor.execute("""INSERT INTO period_timeslot VALUES (?, ?, ?);""", (period_id, start_time, end_time))   


    df = pd.read_csv("datasets/class_session.csv")
    for i in range(df.shape[0]):
        row=df.loc[i]
        section = str(row['section'])
        subject_code = str(row['subject_code'])
        faculty_id = int(row['faculty_id'])
        building = str(row['building'])
        room_number= int(row['room_number'])
        day_of_week= str(row['day_of_week'])

        cursor.execute("""INSERT INTO class_session (section, subject_code, faculty_id, building, room_number, day_of_week) VALUES (?, ?, ?,?,?,?);"""
                       , (section, subject_code, faculty_id, building, room_number, day_of_week))
        

    df = pd.read_csv("datasets/timetable.csv")
    for i in range(df.shape[0]):
        row=df.loc[i]
        session_id, period_id = str(row['session_id']), str(row['period_id'])
        cursor.execute("""INSERT INTO timetable VALUES (?, ?);""", (session_id, period_id)) 
