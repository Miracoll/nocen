import mysql.connector as mysql
from django.conf import settings
from mysql.connector import Error

from hostel.functions import numberToAlphabet, tupleToDict

def connectDB():
    HOST = settings.DB_HOST
    DATABASE = settings.DB_DATABASE
    USER = settings.DB_USER
    PASSWORD = settings.DB_PASSWORD

    try:
        db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
        print("Connected to:", db_connection.get_server_info())
        return db_connection
    except Error as e:
        print(f"Error: {e}")
        return None
    
def connectPreviousDB(regNum):

    databases = ['hostel_2021','hostel_2022']
    output = None

    for database in databases:

        HOST = 'localhost'
        DATABASE = database
        USER = 'root'
        PASSWORD = ''

        try:
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
            # dbCursor = db_connection.cursor()
            rawOutput = getSingleRecord(db_connection,'students','reg_no',regNum)
            if rawOutput:
                outputField = (
                    'id', 'surname', 'first_name', 'other_name', 'phone', 'email', 
                    'programme', 'department', 'school', 'reg_no', 'gender', 
                    'level', 'status', 'curtime', 'rrr', 'order_id'
                )
                output = tupleToDict(outputField, rawOutput)
                db_connection.close()
                print(output)
                return output
            db_connection.close()
        except Error as e:
            print(f"Error: {e}")
            return None

def getSingleRecord(db_connection, table, field, data):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    try:
        dbCursor = db_connection.cursor()
        sql = f"SELECT * FROM {table} WHERE {field} = %s"
        dbCursor.execute(sql, (data,))
        output = dbCursor.fetchone()
        return output
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    
def getHostelRecordName(db_connection):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    try:
        output = []
        dbCursor = db_connection.cursor()
        sql = f"SELECT * FROM hostel_settings"
        dbCursor.execute(sql)
        rawOutput = dbCursor.fetchall()
        for i in rawOutput:
            tupleOutput = tupleToDict(('id','hostel_name'), i[:2])
            output.append(tupleOutput)
        return output
    except Error as e:
        print(f"Error executing query: {e}")
        return None

def getDepartment(db_connection, deptId):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    try:
        dbCursor = db_connection.cursor()
        sql = "SELECT * FROM departments WHERE department_id = %s"
        dbCursor.execute(sql, (deptId,))
        output = dbCursor.fetchone()
        if output:
            department_name = output[3].upper()
            return department_name
        else:
            print("No record found for the given department ID.")
            return None
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    
def checkStudent(db_connection, fieldName, table, regNum):
    if not db_connection:
        print("Database connection failed.")
        return False

    try:
        with db_connection.cursor() as dbCursor:
            sql = f"SELECT * FROM {table} WHERE {fieldName} = %s"
            dbCursor.execute(sql, (regNum,))

            output = dbCursor.fetchall()
            
            if output:
                return True
            else:
                print("No record")
                return False
    except Exception as e:
        print(f"Error executing query: {e}")
        return False
    
def checkAllocationStatus(db_connection, regNum):
    if not db_connection:
        print("Database connection failed.")
        return False

    try:
        with db_connection.cursor() as dbCursor:
            sql = "SELECT * FROM records WHERE student_reg = %s"
            dbCursor.execute(sql, (regNum, ))
        
            output = dbCursor.fetchall()
        
            if output:
                return True
            else:
                print("No record")
                return False
    except Exception as e:
        print(f"Error executing query: {e}")
        return False

def removeRRR(db_connection, regNum):
    if not db_connection:
        print("Database connection failed.")
        return None
    try:
        print(regNum)
        dbCursor = db_connection.cursor()

        # Check if the student has done allocation
        if checkAllocationStatus(db_connection, regNum):
            print('Student already done hostel allocation')
            return False

        sql = "UPDATE students SET rrr = NULL, order_id = NULL WHERE reg_no = %s"
        dbCursor.execute(sql, (regNum,))
        
        # Check if any rows were affected
        if dbCursor.rowcount > 0:
            db_connection.commit()
            return True
        else:
            print("No record found for the given registration number.")
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def clearTuitionFee(db_connection, regNum, rrr):
    if not db_connection:
        print("Database connection failed.")
        return False

    try:
        with db_connection.cursor() as dbCursor:
            # First check if the student exist in the table
            if checkStudent(db_connection,'reg_no','students_sf',regNum):
                print("Record already exist!!!!")
                return False

            sql = "INSERT INTO students_sf (reg_no, rrr) VALUES (%s, %s)"
            dbCursor.execute(sql, (regNum, rrr))
        
            if dbCursor.rowcount > 0:
                db_connection.commit()
                return True
            else:
                print("Record not added")
                return False
                
    except Exception as e:
        print(f"Error executing query: {e}")
        return False

def studentStatus(db_connection, regNum):
    counter = 0

    if not db_connection:
        print("Database connection failed.")
        return False

    try:
        with db_connection.cursor() as dbCursor:
            # Check if the student exists in the 'students' table
            if not checkStudent(db_connection, 'reg_no', 'students', regNum):
                print("Student does not exist!")
                return False

            # Query 1: Check if the student exists in 'students_sf' table
            sql1 = "SELECT * FROM students_sf WHERE reg_no = %s"
            dbCursor.execute(sql1, (regNum,))
            if dbCursor.fetchone():
                counter += 1
                print("Found in students_sf:", counter)

            # Query 2: Check if the student exists in 'students' table
            sql2 = "SELECT * FROM students WHERE reg_no = %s"
            dbCursor.execute(sql2, (regNum,))
            if dbCursor.fetchone():
                counter += 1
                print("Found in students:", counter)

            # Query 3: Check if the student has data in the 'rrr' field
            sql3 = "SELECT * FROM students WHERE reg_no = %s AND (rrr IS NOT NULL AND rrr != '')"
            dbCursor.execute(sql3, (regNum,))
            if dbCursor.fetchone():
                counter += 1
                print("rrr field is populated:", counter)

            # Query 4: Check if there are records in 'records' table associated with student
            sql4 = "SELECT * FROM records WHERE student_reg = %s"
            dbCursor.execute(sql4, (regNum,))
            if dbCursor.fetchone():
                counter += 1
                print("Found in records:", counter)

            return counter

    except Exception as e:
        print(f"Error executing query: {e}")
        return False

def getHostelRecord(db_connection, data):
    if not db_connection:
        print("Database connection failed.")
        return None
    with db_connection.cursor() as dbCursor:
        fieldName = ('record_id','bed_id','bed_label','room_id','room_number','hostel_name','pin_price','student_reg','student_name','pin_serial','pin_number','gender','alloc_date','status')
        try:
            dbCursor = db_connection.cursor()
            sql = f"SELECT * FROM records WHERE student_reg = %s"
            dbCursor.execute(sql, (data,))
            rawOutput = dbCursor.fetchone()
            if rawOutput:
                output = tupleToDict(fieldName, rawOutput)
                print(output)
                return output
            else:
                print('No record found')
                return None
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        
def getRoomRecord(db_connection, roomId):
    if not db_connection:
        print("Database connection failed.")
        return None
    try:
        output = {}
        dbCursor = db_connection.cursor()

        sql = "SELECT * FROM rooms WHERE room_id = %s"
        dbCursor.execute(sql, (roomId,))
        rawOutput = dbCursor.fetchone()
        print(rawOutput)
        output['bsp_avail'] = rawOutput[6]
        output['bsp_occup'] = rawOutput[7]
        output['filled'] = rawOutput[8]
        return output

    except Exception as e:
        print(f"Error executing query: {e}")
        return None

        
def unallocateHostel(db_connection, regNum, roomId, bedId):
    if not db_connection:
        print("Database connection failed.")
        return None
    with db_connection.cursor() as dbCursor:
        try:
            # Fetch the room record
            room = getRoomRecord(db_connection, roomId)
            if room is None:
                print("Room record not found.")
                return None

            # Calculate new room values
            bsp_avail = int(room['bsp_avail']) + 1
            bsp_occup = int(room['bsp_occup']) - 1
            filled = 0 if int(room['filled']) == 1 else room['filled']

            # SQL queries
            sql1 = "UPDATE bedspace SET student_reg = NULL, pin = NULL, occupied = 0, date_occup = NULL WHERE bed_id = %s"
            sql2 = "UPDATE rooms SET bsp_avail = %s, bsp_occup = %s, filled = %s WHERE room_id = %s"
            sql3 = "DELETE FROM records WHERE student_reg = %s"
            sql4 = "DELETE FROM xpin WHERE student_reg = %s"

            # Execute the bedspace update
            dbCursor.execute(sql1, (bedId,))
            print(f"Rows affected by bedspace update: {dbCursor.rowcount}") 
            if dbCursor.rowcount > 0:
                # Execute the room update and deletion queries
                dbCursor.execute(sql2, (bsp_avail, bsp_occup, filled, roomId))
                dbCursor.execute(sql3, (regNum,))
                dbCursor.execute(sql4, (regNum,))
                
                # Commit all changes
                db_connection.commit()
                return True
            else:
                print("No record found for the given registration number.")
                return None

        except Exception as e:
            print(f"Error executing query: {e}")
            return None

def availableHostel(db_connection):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    with db_connection.cursor() as dbCursor:
        try:
            hostels = []
            dbCursor = db_connection.cursor()
            sql = f"SELECT * FROM rooms WHERE filled = 0 AND status = 1"
            dbCursor.execute(sql)
            rawOutput = dbCursor.fetchall()
            fieldNames = ('room_id','room_number','floor','hostel_id','hostel_name','bsp_total','bsp_avail','bsp_occup','filled','status')
            for i in rawOutput:
                tupleOutput = tupleToDict(fieldNames, i)
                hostels.append(tupleOutput)
            return hostels
        except Error as e:
            print(f"Error executing query: {e}")
        return None

def allocatedStudent(db_connection):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    with db_connection.cursor() as dbCursor:
        try:
            students = []
            dbCursor = db_connection.cursor()
            sql = f"SELECT * FROM records"
            dbCursor.execute(sql)
            rawOutput = dbCursor.fetchall()
            fieldNames = ('record_id','bed_id','bed_label','room_id','room_number','hostel_name','pin_price','student_reg','student_name','pin_serial','pin_number','gender','alloc_date','status')
            for i in rawOutput:
                tupleOutput = tupleToDict(fieldNames, i)
                students.append(tupleOutput)
            return students
        except Error as e:
            print(f"Error executing query: {e}")
            return None

def registeredStudents(db_connection):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    with db_connection.cursor() as dbCursor:
        try:
            students = []
            dbCursor = db_connection.cursor()
            sql = f"SELECT * FROM students"
            dbCursor.execute(sql)
            rawOutput = dbCursor.fetchall()
            outputField = (
                'id', 'surname', 'first_name', 'other_name', 'phone', 'email', 
                'programme', 'department', 'school', 'reg_no', 'gender', 
                'level', 'status', 'curtime', 'rrr', 'order_id'
            )
            for i in rawOutput:
                tupleOutput = tupleToDict(outputField, i)
                students.append(tupleOutput)
            return students
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        
def bedspace(db_connection):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    with db_connection.cursor() as dbCursor:
        try:
            dbCursor = db_connection.cursor()
            sql = f"SELECT * FROM bedspace WHERE occupied = 0 AND status = 1"
            dbCursor.execute(sql)
            rawOutput = dbCursor.fetchall()
            return rawOutput
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        
def getRoomId(db_connection, hostelName, roomNumber):
    if not db_connection:
        print("Database connection failed.")
        return None
    
    try:
        dbCursor = db_connection.cursor()
        sql = "SELECT * FROM rooms WHERE hostel_name = %s AND room_number = %s"
        dbCursor.execute(sql, (hostelName,roomNumber))
        rawOutput = dbCursor.fetchone()[0]
        return rawOutput
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    
def addRoomToHostel(db_connection, roomNum, floor, hostelId, hostelName, bedspace, incrementRoomBy):
    if not db_connection:
        print("Database connection failed.")
        return None

    try:
        with db_connection.cursor() as dbCursor:
            # Add to rooms table
            for i in range(floor):
                for j in range(incrementRoomBy):
                    newRoomNum = roomNum + j
                    sql1 = """
                        INSERT INTO rooms 
                        (room_number, floor, hostel_id, hostel_name, bsp_total, bsp_avail, bsp_occup, filled, status) 
                        VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 1)
                    """
                    dbCursor.execute(sql1, (newRoomNum, i, hostelId, hostelName, bedspace, bedspace))
                    db_connection.commit()
                    # Add bedspace record
                    for k in range(bedspace):
                        bsp = numberToAlphabet(k+1)
                        print(hostelName,newRoomNum)
                        roomId = getRoomId(db_connection, hostelName,newRoomNum)
                        print(roomId)
                        sql2 = """
                            INSERT INTO bedspace 
                            (bsp_label, room_id, hostel_name, student_reg, pin, occupied, date_occup, date_vac, status) 
                            VALUES (%s, %s, %s, NULL, NULL, 0, NULL, NULL, 1)
                        """
                        dbCursor.execute(sql2, (bsp, roomId, hostelName))
                roomNum += 100
            db_connection.commit()
    except Error as e:
        db_connection.rollback()  # Rollback in case of error
        print(f"Error executing query: {e}")
        return None
    
