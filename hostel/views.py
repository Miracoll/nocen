from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from account.decorators import allowed_users
from hostel.functions import backupMysqlDatabase, createLog, sendFile, tupleToDict
from . import db

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def home(request):
    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('register-student')
    availableHostel = db.availableHostel(db_connection)
    allocatedStudents = db.allocatedStudent(db_connection)
    registeredStudents = db.registeredStudents(db_connection)
    bedspace = db.bedspace(db_connection)
    context = {
        'hostel':len(availableHostel),
        'students':len(allocatedStudents),
        'register':len(registeredStudents),
        'bedspace':len(bedspace)
    }
    return render(request, 'hostel/index.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def getRRR(request):
    data = request.GET.get('student')
    output = None
    
    if data is not None:
        db_connection = db.connectDB()
        if not db_connection:
            createLog(f'Tried to get student<{data}> RRR', False, request.user)
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('get-rrr')
        try:
            outputField = (
                'id', 'surname', 'first_name', 'other_name', 'phone', 'email', 
                'programme', 'department', 'school', 'reg_no', 'gender', 
                'level', 'status', 'curtime', 'rrr', 'order_id'
            )
            rawOutput = db.getSingleRecord(db_connection, 'students', 'reg_no', data)
            
            if rawOutput:
                output = tupleToDict(outputField, rawOutput)
                decryptDept = db.getDepartment(db_connection, output['department'])
                output['department'] = decryptDept
                print(output)
                createLog(f'Got student<{data}> RRR', True, request.user)
            else:
                print("No student found with the provided registration number.")
                messages.error(request, 'Student not found')
                return redirect('get-rrr')
        except Exception as e:
            print(f"Error fetching student record: {e}")
            messages.error(request, 'Error fetching student record')
            return redirect('get-rrr')

        finally:
            db_connection.close()
            
    
    context = {'student': output}
    return render(request, 'hostel/get-rrr.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def removeRRRInit(request):
    data = request.GET.get('student')
    output = None
    
    if data is not None:
        db_connection = db.connectDB()
        if not db_connection:
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('remove-rrr')
        try:
            outputField = (
                'id', 'surname', 'first_name', 'other_name', 'phone', 'email', 
                'programme', 'department', 'school', 'reg_no', 'gender', 
                'level', 'status', 'curtime', 'rrr', 'order_id'
            )
            rawOutput = db.getSingleRecord(db_connection, 'students', 'reg_no', data)
            
            if rawOutput:
                output = tupleToDict(outputField, rawOutput)
                print(output)
                createLog(f'Initiate student<{data}> RRR removal', True, request.user)
            else:
                print("No student found with the provided registration number.")
                messages.error(request, 'Student not found')
                return redirect('remove-rrr')
        except Exception as e:
            print(f"Error fetching student record: {e}")
            messages.error(request, 'Error fetching student record')
            return redirect('remove-rrr')

        finally:
            db_connection.close()

    context = {'student': output}
    return render(request, 'hostel/remove-rrr.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def removeRRR(request, reg):

    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('remove-rrr')
    try:
        
        rawOutput = db.removeRRR(db_connection,  reg)
        
        if rawOutput:
            messages.success(request, 'Done')
            createLog(f'Removed student<{reg}>', True, request.user)
            return redirect('remove-rrr')
        else:
            print("No student found with the provided registration number or student has already done hostel allocation.")
            messages.error(request, 'Student not found or allocation done for the student')
            return redirect('remove-rrr')
    except Exception as e:
        print(f"Error fetching student record: {e}")
        messages.error(request, 'Error fetching student record')
        return redirect('remove-rrr')

    finally:
        db_connection.close()

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def clearStudentTuitionFee(request):
    if request.method == 'POST':

        data = request.POST.get('student')
        rrr = request.POST.get('rrr')
    
        db_connection = db.connectDB()
        if not db_connection:
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('clear-rrr')
        try:
            output = db.clearTuitionFee(db_connection, data, rrr)
            
            if output:
                print(output)
                createLog(f'Cleared student<{data}> for hostel', True, request.user)
                messages.success(request, 'Student cleared')
                return redirect('clear-rrr')
            else:
                print("Student already exist or db connection issues")
                messages.error(request, 'Student already exist or db connection issues')
                return redirect('clear-rrr')
        except Exception as e:
            print(f"Error adding student record: {e}")
            messages.error(request, 'Error adding student record')
            return redirect('clear-rrr')

        finally:
            db_connection.close()

    context = {}
    return render(request, 'hostel/clear-rrr.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def studentHostelStatus(request):
    data = request.GET.get('student')
    output = None
    
    if data is not None:
        db_connection = db.connectDB()
        if not db_connection:
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('student-status')
        try:
            rawOutput = db.studentStatus(db_connection, data)
            print(rawOutput)
            
            if rawOutput:
                output = rawOutput
                print(output)
                createLog(f'Viewed student<{data}> status', True, request.user)
            else:
                print("No student found with the provided registration number.")
                messages.error(request, 'Student not found')
                return redirect('student-status')
        except Exception as e:
            print(f"Error fetching student record: {e}")
            messages.error(request, 'Error fetching student record')
            return redirect('student-status')

        finally:
            db_connection.close()

    context = {'student': output}
    return render(request, 'hostel/student-status.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def unallocateStudentInit(request):
    data = request.GET.get('student')
    output = None
    
    if data is not None:
        db_connection = db.connectDB()
        if not db_connection:
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('student-unallocate-init')
        try:
            output = db.getHostelRecord(db_connection, data)
            createLog(f'Initiate student<{data}> hostel unallocation', True, request.user)
            
            if output:
                print(output)
            else:
                print("No student found with the provided registration number.")
                messages.error(request, 'Student not found')
                return redirect('student-unallocate-init')
        except Exception as e:
            print(f"Error fetching student record: {e}")
            messages.error(request, 'Error fetching student record')
            return redirect('student-unallocate-init')

        finally:
            db_connection.close()

    context = {'student': output}
    return render(request, 'hostel/student-unallocate.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def unallocateStudent(request, reg, room, bed):

    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('student-unallocate-init')
    try:
        
        rawOutput = db.unallocateHostel(db_connection, reg, room, bed)
        createLog(f'Unallocate student<{reg}>', True, request.user)
        
        if rawOutput:
            messages.success(request, 'Done')
            return redirect('student-unallocate-init')
        else:
            print("No student found with the provided registration number or student has already done hostel allocation.")
            messages.error(request, 'Student not found')
            return redirect('student-unallocate-init')
    except Exception as e:
        print(f"Error fetching student record: {e}")
        messages.error(request, 'Error fetching student record')
        return redirect('student-unallocate-init')

    finally:
        db_connection.close()

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def registerStudentInit(request):
    data = request.GET.get('student')
    output = None
    
    if data is not None:
        db_connection = db.connectDB()
        if not db_connection:
            print("Failed to connect to the database.")
            messages(request, "Can't connect to the database at the moment")
            return redirect('register-student')
        try:
            output = db.connectPreviousDB(data)
            
            if output:
                print(output)
            else:
                print("No student found with the provided registration number.")
                messages.error(request, 'Student not found')
                return redirect('register-student')
        except Exception as e:
            print(f"Error fetching student record: {e}")
            messages.error(request, 'Error fetching student record')
            return redirect('register-student')

        finally:
            db_connection.close()

    context = {'student': output}
    return render(request, 'hostel/student-register.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def availableHostel(request):
    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('register-student')
    output = db.availableHostel(db_connection)
    context = {'hostels':output}
    return render(request, 'hostel/available-hostel.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def allocatedStudents(request):
    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('allocated-student')
    output = db.allocatedStudent(db_connection)
    context = {'students':output}
    return render(request, 'hostel/allocated-students.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['user','admin'])
def addRoom(request):
    db_connection = db.connectDB()
    if not db_connection:
        print("Failed to connect to the database.")
        messages(request, "Can't connect to the database at the moment")
        return redirect('add-room')
    output = db.getHostelRecordName(db_connection)
    if request.method == 'POST':
        hostel = request.POST.get('hostel').split(',')
        floorNum = request.POST.get('floorNum')
        rmNum = request.POST.get('rmNum')
        incrementRoomBy = request.POST.get('increment')
        bedspace = request.POST.get('bedspace')

        db.addRoomToHostel(db_connection,int(rmNum),int(floorNum),hostel[0],hostel[1],int(bedspace),int(incrementRoomBy))
        createLog(f'Add room {hostel[0]}, {rmNum}, {incrementRoomBy}, {bedspace}', True, request.user)
        messages.success(request, 'Done')
        return redirect('add-room')

    context = {'hostels':output}
    return render(request, 'hostel/add-room.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def backUpDb(request):
    if request.method == 'POST':
        email = request.POST.get('mail')
        DATABASE = settings.DB_DATABASE
        PATH = settings.BASE_DIR / 'databases'
        output = backupMysqlDatabase(DATABASE,PATH)

        if not output:
            messages.error(request, 'Not successful')
            return redirect('backup')
        
        sendFile(output,'BACKUP DATA','SAVING DATA IS OUR PRIORITY!!!',email)
        createLog('Backed up database', True, request.user)
        messages.success(request, 'Done')
        return redirect('backup')
            
    context = {}
    return render(request, 'hostel/backup.html', context)