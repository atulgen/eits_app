# import frappe
# from datetime import datetime, time, timedelta
# from frappe import _

# @frappe.whitelist()
# def get_employee_availability(date, start_time=None, end_time=None):
#     """
#     Get employee availability for a specific date
    
#     Args:
#         date: Date to check availability (YYYY-MM-DD format)
#         start_time: Optional start time to filter (HH:MM format)
#         end_time: Optional end time to filter (HH:MM format)
    
#     Returns:
#         List of employees with their availability slots
#     """
#     try:
#         # Validate date format
#         selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        
#         # Get all active employees
#         employees = frappe.get_all('Employee', 
#             filters={'status': 'Active'}, 
#             fields=['name', 'employee_name', 'department']
#         )
        
#         employee_availability = []
        
#         for employee in employees:
#             availability = get_employee_time_slots(employee['name'], selected_date)
#             employee_availability.append({
#                 'employee_id': employee['name'],
#                 'employee_name': employee['employee_name'],
#                 'department': employee['department'],
#                 'date': date,
#                 'availability': availability
#             })
        
#         return {
#             'status': 'success',
#             'data': employee_availability,
#             'message': f'Employee availability for {date}'
#         }
        
#     except ValueError as e:
#         frappe.throw(_('Invalid date format. Please use YYYY-MM-DD format'))
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), 'Employee Availability API Error')
#         frappe.throw(_('An error occurred while fetching employee availability'))

# def get_employee_time_slots(employee_id, date):
#     """
#     Get time slots for a specific employee on a given date
    
#     Args:
#         employee_id: Employee ID
#         date: Date object
    
#     Returns:
#         Dictionary with occupied and free time slots
#     """
#     # Get work allocations for the employee on the specified date
#     allocations = frappe.get_all('Daily Work Allocation',
#         filters={
#             'employee_name': employee_id,
#             'date': date
#         },
#         fields=['name']
#     )
    
#     occupied_slots = []
    
#     # Get detailed work allocation data
#     for allocation in allocations:
#         try:
#             # Get the parent document
#             parent_doc = frappe.get_doc('Daily Work Allocation', allocation['name'])
            
#             # Access the child table - try common field names for the child table
#             work_items = []
            
#             # Try different possible field names for the child table
#             possible_fieldnames = ['work_allocation', 'work_items', 'items', 'allocations', 'work_details', 'work']
            
#             for fieldname in possible_fieldnames:
#                 if hasattr(parent_doc, fieldname) and parent_doc.get(fieldname):
#                     child_table = parent_doc.get(fieldname)
#                     for item in child_table:
#                         # Use the exact field names from the Work DocType
#                         start_time = item.get('expected_start_date')
#                         duration = item.get('expected_time_in_hours')
                        
#                         if start_time and duration:
#                             work_items.append({
#                                 'start_time': start_time,
#                                 'duration_in_hours': duration
#                             })
                    
#                     if work_items:
#                         break
            
#             # If still no work items found, try direct database query approach
#             if not work_items:
#                 # Get child table records directly from the Work DocType
#                 work_records = frappe.get_all('Work',
#                     filters={'parent': allocation['name']},
#                     fields=['expected_start_date', 'expected_time_in_hours'],
#                     order_by='expected_start_date'
#                 )
                
#                 for work in work_records:
#                     if work['expected_start_date'] and work['expected_time_in_hours']:
#                         work_items.append({
#                             'start_time': work['expected_start_date'],
#                             'duration_in_hours': work['expected_time_in_hours']
#                         })
                            
#         except Exception as e:
#             frappe.log_error(f"Error processing allocation {allocation['name']}: {str(e)}", "Work Allocation Processing")
#             continue
        
#         # Process the work items to create occupied slots
#         for work in work_items:
#             if work['start_time'] and work['duration_in_hours']:
#                 start_time = work['start_time']
                
#                 # Convert duration to timedelta and calculate end time
#                 duration_hours = float(work['duration_in_hours'])
#                 duration = timedelta(hours=duration_hours)
                
#                 # Handle different start_time formats
#                 if isinstance(start_time, time):
#                     start_datetime = datetime.combine(date, start_time)
#                 elif isinstance(start_time, str):
#                     # Handle string time format like "10:00:00"
#                     try:
#                         time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
#                         start_datetime = datetime.combine(date, time_obj)
#                     except ValueError:
#                         # Try other time formats
#                         try:
#                             time_obj = datetime.strptime(start_time, '%H:%M').time()
#                             start_datetime = datetime.combine(date, time_obj)
#                         except ValueError:
#                             continue  # Skip this work item if time format is invalid
#                 elif isinstance(start_time, timedelta):
#                     # Handle timedelta - convert to time by adding to start of day
#                     start_datetime = datetime.combine(date, time(0, 0)) + start_time
#                 elif isinstance(start_time, datetime):
#                     # If it's already a datetime, just use the time part
#                     start_datetime = datetime.combine(date, start_time.time())
#                 else:
#                     # Try to get time attribute
#                     try:
#                         start_datetime = datetime.combine(date, start_time.time())
#                     except AttributeError:
#                         continue  # Skip this work item if we can't convert
                
#                 end_datetime = start_datetime + duration
                
#                 occupied_slots.append({
#                     'start': start_datetime.strftime('%H:%M'),
#                     'end': end_datetime.strftime('%H:%M'),
#                     'start_datetime': start_datetime,
#                     'end_datetime': end_datetime
#                 })
    
#     # Sort occupied slots by start time
#     occupied_slots.sort(key=lambda x: x['start_datetime'])
    
#     # Merge overlapping slots
#     merged_occupied_slots = merge_overlapping_slots(occupied_slots)
    
#     # Calculate free slots (assuming 24-hour availability: 00:00 to 23:59)
#     free_slots = calculate_free_slots(merged_occupied_slots, date)
    
#     return {
#         'occupied_slots': [{'start': slot['start'], 'end': slot['end']} for slot in merged_occupied_slots],
#         'free_slots': free_slots,
#         'is_completely_free': len(merged_occupied_slots) == 0,
#         'total_occupied_hours': sum([
#             (slot['end_datetime'] - slot['start_datetime']).total_seconds() / 3600 
#             for slot in merged_occupied_slots
#         ])
#     }

# def merge_overlapping_slots(slots):
#     """
#     Merge overlapping time slots
    
#     Args:
#         slots: List of time slot dictionaries
    
#     Returns:
#         List of merged time slots
#     """
#     if not slots:
#         return []
    
#     merged = [slots[0]]
    
#     for current in slots[1:]:
#         last_merged = merged[-1]
        
#         # Check if current slot overlaps with the last merged slot
#         if current['start_datetime'] <= last_merged['end_datetime']:
#             # Merge slots by extending the end time
#             if current['end_datetime'] > last_merged['end_datetime']:
#                 merged[-1]['end_datetime'] = current['end_datetime']
#                 merged[-1]['end'] = current['end']
#         else:
#             # No overlap, add as new slot
#             merged.append(current)
    
#     return merged

# def calculate_free_slots(occupied_slots, date):
#     """
#     Calculate free time slots based on occupied slots
    
#     Args:
#         occupied_slots: List of occupied time slots
#         date: Date object
    
#     Returns:
#         List of free time slots
#     """
#     # Define working hours (00:00 to 23:59)
#     day_start = datetime.combine(date, time(0, 0))
#     day_end = datetime.combine(date, time(23, 59))
    
#     free_slots = []
    
#     if not occupied_slots:
#         # Completely free day
#         return [{
#             'start': '00:00',
#             'end': '23:59',
#             'duration_hours': 24
#         }]
    
#     # Check for free time before first occupied slot
#     first_occupied = occupied_slots[0]
#     if first_occupied['start_datetime'] > day_start:
#         duration = (first_occupied['start_datetime'] - day_start).total_seconds() / 3600
#         free_slots.append({
#             'start': day_start.strftime('%H:%M'),
#             'end': first_occupied['start'],
#             'duration_hours': round(duration, 2)
#         })
    
#     # Check for free time between occupied slots
#     for i in range(len(occupied_slots) - 1):
#         current_end = occupied_slots[i]['end_datetime']
#         next_start = occupied_slots[i + 1]['start_datetime']
        
#         if next_start > current_end:
#             duration = (next_start - current_end).total_seconds() / 3600
#             free_slots.append({
#                 'start': current_end.strftime('%H:%M'),
#                 'end': next_start.strftime('%H:%M'),
#                 'duration_hours': round(duration, 2)
#             })
    
#     # Check for free time after last occupied slot
#     last_occupied = occupied_slots[-1]
#     if last_occupied['end_datetime'] < day_end:
#         duration = (day_end - last_occupied['end_datetime']).total_seconds() / 3600
#         free_slots.append({
#             'start': last_occupied['end'],
#             'end': day_end.strftime('%H:%M'),
#             'duration_hours': round(duration, 2)
#         })
    
#     return free_slots

# @frappe.whitelist()
# def get_employee_availability_summary(date, required_duration=None):
#     """
#     Get a summary of employee availability with filtering options
    
#     Args:
#         date: Date to check availability (YYYY-MM-DD format)
#         required_duration: Minimum required free time in hours (optional)
    
#     Returns:
#         Summary of available employees
#     """
#     try:
#         availability_data = get_employee_availability(date)
        
#         if availability_data['status'] != 'success':
#             return availability_data
        
#         summary = {
#             'date': date,
#             'total_employees': len(availability_data['data']),
#             'completely_free': [],
#             'partially_free': [],
#             'completely_occupied': []
#         }
        
#         for emp_data in availability_data['data']:
#             availability = emp_data['availability']
            
#             if availability['is_completely_free']:
#                 summary['completely_free'].append({
#                     'employee_id': emp_data['employee_id'],
#                     'employee_name': emp_data['employee_name'],
#                     'department': emp_data['department']
#                 })
#             elif len(availability['free_slots']) > 0:
#                 # Check if employee has required duration if specified
#                 has_required_duration = True
#                 if required_duration:
#                     max_free_duration = max([slot['duration_hours'] for slot in availability['free_slots']])
#                     has_required_duration = max_free_duration >= float(required_duration)
                
#                 if has_required_duration:
#                     summary['partially_free'].append({
#                         'employee_id': emp_data['employee_id'],
#                         'employee_name': emp_data['employee_name'],
#                         'department': emp_data['department'],
#                         'free_slots': availability['free_slots'],
#                         'occupied_slots': availability['occupied_slots']
#                     })
#             else:
#                 summary['completely_occupied'].append({
#                     'employee_id': emp_data['employee_id'],
#                     'employee_name': emp_data['employee_name'],
#                     'department': emp_data['department'],
#                     'occupied_slots': availability['occupied_slots']
#                 })
        
#         summary['available_count'] = len(summary['completely_free']) + len(summary['partially_free'])
#         summary['occupied_count'] = len(summary['completely_occupied'])
        
#         return {
#             'status': 'success',
#             'data': summary,
#             'message': f'Employee availability summary for {date}'
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), 'Employee Availability Summary API Error')
#         frappe.throw(_('An error occurred while generating availability summary'))

# # Additional debugging function to help identify the correct field names
# @frappe.whitelist()
# def debug_work_allocation_structure(allocation_name):
#     """
#     Debug function to help identify the structure of Daily Work Allocation DocType
#     """
#     try:
#         doc = frappe.get_doc('Daily Work Allocation', allocation_name)
#         doc_dict = doc.as_dict()
        
#         result = {
#             'main_fields': {},
#             'child_tables': {}
#         }
        
#         for key, value in doc_dict.items():
#             if isinstance(value, list) and len(value) > 0:
#                 # This is likely a child table
#                 child_item = value[0]
#                 if hasattr(child_item, 'as_dict'):
#                     result['child_tables'][key] = list(child_item.as_dict().keys())
#                 else:
#                     result['child_tables'][key] = list(child_item.keys()) if isinstance(child_item, dict) else str(type(child_item))
#             else:
#                 result['main_fields'][key] = str(type(value))
        
#         return result
        
#     except Exception as e:
#         return {'error': str(e)}



import frappe
from datetime import datetime, time, timedelta
from frappe import _

@frappe.whitelist()
def get_employee_availability(date, start_time=None, end_time=None):
    """
    Get employee availability for a specific date
    
    Args:
        date: Date to check availability (YYYY-MM-DD format)
        start_time: Optional start time to filter (HH:MM format)
        end_time: Optional end time to filter (HH:MM format)
    
    Returns:
        List of employees with their availability slots
    """
    try:
        # Validate date format
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all active employees
        employees = frappe.get_all('Employee', 
            filters={'status': 'Active'}, 
            fields=['name', 'employee_name', 'department']
        )
        
        employee_availability = []
        
        for employee in employees:
            availability = get_employee_time_slots(employee['name'], selected_date)
            employee_availability.append({
                'employee_id': employee['name'],
                'employee_name': employee['employee_name'],
                'department': employee['department'],
                'date': date,
                'availability': availability
            })
        
        return {
            'status': 'success',
            'data': employee_availability,
            'message': f'Employee availability for {date}'
        }
        
    except ValueError as e:
        frappe.throw(_('Invalid date format. Please use YYYY-MM-DD format'))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Employee Availability API Error')
        frappe.throw(_('An error occurred while fetching employee availability'))

def get_employee_time_slots(employee_id, date):
    """
    Get time slots for a specific employee on a given date
    
    Args:
        employee_id: Employee ID
        date: Date object
    
    Returns:
        Dictionary with occupied and free time slots
    """
    # Get work allocations for the employee on the specified date
    allocations = frappe.get_all('Daily Work Allocation',
        filters={
            'employee_name': employee_id,
            'date': date
        },
        fields=['name']
    )
    
    occupied_slots = []
    
    # Get detailed work allocation data
    for allocation in allocations:
        try:
            # Get the parent document
            parent_doc = frappe.get_doc('Daily Work Allocation', allocation['name'])
            
            # Access the child table - try common field names for the child table
            work_items = []
            
            # Try different possible field names for the child table
            possible_fieldnames = ['work_allocation', 'work_items', 'items', 'allocations', 'work_details', 'work']
            
            for fieldname in possible_fieldnames:
                if hasattr(parent_doc, fieldname) and parent_doc.get(fieldname):
                    child_table = parent_doc.get(fieldname)
                    for item in child_table:
                        # Use the exact field names from the Work DocType
                        start_time = item.get('expected_start_date')
                        duration = item.get('expected_time_in_hours')
                        
                        if start_time and duration:
                            work_items.append({
                                'start_time': start_time,
                                'duration_in_hours': duration
                            })
                    
                    if work_items:
                        break
            
            # If still no work items found, try direct database query approach
            if not work_items:
                # Get child table records directly from the Work DocType
                work_records = frappe.get_all('Work',
                    filters={'parent': allocation['name']},
                    fields=['expected_start_date', 'expected_time_in_hours'],
                    order_by='expected_start_date'
                )
                
                for work in work_records:
                    if work['expected_start_date'] and work['expected_time_in_hours']:
                        work_items.append({
                            'start_time': work['expected_start_date'],
                            'duration_in_hours': work['expected_time_in_hours']
                        })
                            
        except Exception as e:
            frappe.log_error(f"Error processing allocation {allocation['name']}: {str(e)}", "Work Allocation Processing")
            continue
        
        # Process the work items to create occupied slots
        for work in work_items:
            if work['start_time'] and work['duration_in_hours']:
                start_time = work['start_time']
                
                # Convert duration to timedelta and calculate end time
                duration_hours = float(work['duration_in_hours'])
                duration = timedelta(hours=duration_hours)
                
                # Handle different start_time formats
                if isinstance(start_time, time):
                    start_datetime = datetime.combine(date, start_time)
                elif isinstance(start_time, str):
                    # Handle string time format like "10:00:00"
                    try:
                        time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
                        start_datetime = datetime.combine(date, time_obj)
                    except ValueError:
                        # Try other time formats
                        try:
                            time_obj = datetime.strptime(start_time, '%H:%M').time()
                            start_datetime = datetime.combine(date, time_obj)
                        except ValueError:
                            continue  # Skip this work item if time format is invalid
                elif isinstance(start_time, timedelta):
                    # Handle timedelta - convert to time by adding to start of day
                    start_datetime = datetime.combine(date, time(0, 0)) + start_time
                elif isinstance(start_time, datetime):
                    # If it's already a datetime, just use the time part
                    start_datetime = datetime.combine(date, start_time.time())
                else:
                    # Try to get time attribute
                    try:
                        start_datetime = datetime.combine(date, start_time.time())
                    except AttributeError:
                        continue  # Skip this work item if we can't convert
                
                end_datetime = start_datetime + duration
                
                occupied_slots.append({
                    'start': start_datetime.strftime('%H:%M'),
                    'end': end_datetime.strftime('%H:%M'),
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime
                })
    
    # Sort occupied slots by start time
    occupied_slots.sort(key=lambda x: x['start_datetime'])
    
    # Filter occupied slots to only include work shift hours (9 AM to 6 PM)
    shift_start = datetime.combine(date, time(9, 0))
    shift_end = datetime.combine(date, time(18, 0))
    
    filtered_occupied_slots = []
    for slot in occupied_slots:
        slot_start = max(slot['start_datetime'], shift_start)
        slot_end = min(slot['end_datetime'], shift_end)
        
        # Only include if the slot overlaps with work hours
        if slot_start < slot_end:
            filtered_occupied_slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
                'start_datetime': slot_start,
                'end_datetime': slot_end
            })
    
    # Merge overlapping slots
    merged_occupied_slots = merge_overlapping_slots(filtered_occupied_slots)
    
    # Calculate free slots during work shift hours (9 AM to 6 PM)
    free_slots = calculate_free_slots(merged_occupied_slots, date)
    
    return {
        'occupied_slots': [{'start': slot['start'], 'end': slot['end']} for slot in merged_occupied_slots],
        'free_slots': free_slots,
        'is_completely_free': len(merged_occupied_slots) == 0,
        'total_occupied_hours': sum([
            (slot['end_datetime'] - slot['start_datetime']).total_seconds() / 3600 
            for slot in merged_occupied_slots
        ])
    }

def merge_overlapping_slots(slots):
    """
    Merge overlapping time slots
    
    Args:
        slots: List of time slot dictionaries
    
    Returns:
        List of merged time slots
    """
    if not slots:
        return []
    
    merged = [slots[0]]
    
    for current in slots[1:]:
        last_merged = merged[-1]
        
        # Check if current slot overlaps with the last merged slot
        if current['start_datetime'] <= last_merged['end_datetime']:
            # Merge slots by extending the end time
            if current['end_datetime'] > last_merged['end_datetime']:
                merged[-1]['end_datetime'] = current['end_datetime']
                merged[-1]['end'] = current['end']
        else:
            # No overlap, add as new slot
            merged.append(current)
    
    return merged

def calculate_free_slots(occupied_slots, date):
    """
    Calculate free time slots based on occupied slots during work shift hours
    
    Args:
        occupied_slots: List of occupied time slots
        date: Date object
    
    Returns:
        List of free time slots during work hours (9:00 AM to 6:00 PM)
    """
    # Define working hours (9:00 AM to 6:00 PM)
    shift_start = datetime.combine(date, time(9, 0))  # 9:00 AM
    shift_end = datetime.combine(date, time(18, 0))   # 6:00 PM
    
    free_slots = []
    
    # Filter occupied slots to only include those within work hours
    work_hour_occupied_slots = []
    for slot in occupied_slots:
        slot_start = max(slot['start_datetime'], shift_start)
        slot_end = min(slot['end_datetime'], shift_end)
        
        # Only include if the slot overlaps with work hours
        if slot_start < slot_end:
            work_hour_occupied_slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
                'start_datetime': slot_start,
                'end_datetime': slot_end
            })
    
    if not work_hour_occupied_slots:
        # Completely free during work hours
        return [{
            'start': '09:00',
            'end': '18:00',
            'duration_hours': 9
        }]
    
    # Check for free time before first occupied slot (but after shift start)
    first_occupied = work_hour_occupied_slots[0]
    if first_occupied['start_datetime'] > shift_start:
        duration = (first_occupied['start_datetime'] - shift_start).total_seconds() / 3600
        free_slots.append({
            'start': shift_start.strftime('%H:%M'),
            'end': first_occupied['start'],
            'duration_hours': round(duration, 2)
        })
    
    # Check for free time between occupied slots
    for i in range(len(work_hour_occupied_slots) - 1):
        current_end = work_hour_occupied_slots[i]['end_datetime']
        next_start = work_hour_occupied_slots[i + 1]['start_datetime']
        
        if next_start > current_end:
            duration = (next_start - current_end).total_seconds() / 3600
            free_slots.append({
                'start': current_end.strftime('%H:%M'),
                'end': next_start.strftime('%H:%M'),
                'duration_hours': round(duration, 2)
            })
    
    # Check for free time after last occupied slot (but before shift end)
    last_occupied = work_hour_occupied_slots[-1]
    if last_occupied['end_datetime'] < shift_end:
        duration = (shift_end - last_occupied['end_datetime']).total_seconds() / 3600
        free_slots.append({
            'start': last_occupied['end'],
            'end': shift_end.strftime('%H:%M'),
            'duration_hours': round(duration, 2)
        })
    
    return free_slots

@frappe.whitelist()
def get_employee_availability_summary(date, required_duration=None):
    """
    Get a summary of employee availability with filtering options
    
    Args:
        date: Date to check availability (YYYY-MM-DD format)
        required_duration: Minimum required free time in hours (optional)
    
    Returns:
        Summary of available employees
    """
    try:
        availability_data = get_employee_availability(date)
        
        if availability_data['status'] != 'success':
            return availability_data
        
        summary = {
            'date': date,
            'total_employees': len(availability_data['data']),
            'completely_free': [],
            'partially_free': [],
            'completely_occupied': []
        }
        
        for emp_data in availability_data['data']:
            availability = emp_data['availability']
            
            if availability['is_completely_free']:
                summary['completely_free'].append({
                    'employee_id': emp_data['employee_id'],
                    'employee_name': emp_data['employee_name'],
                    'department': emp_data['department']
                })
            elif len(availability['free_slots']) > 0:
                # Check if employee has required duration if specified
                has_required_duration = True
                if required_duration:
                    max_free_duration = max([slot['duration_hours'] for slot in availability['free_slots']])
                    has_required_duration = max_free_duration >= float(required_duration)
                
                if has_required_duration:
                    summary['partially_free'].append({
                        'employee_id': emp_data['employee_id'],
                        'employee_name': emp_data['employee_name'],
                        'department': emp_data['department'],
                        'free_slots': availability['free_slots'],
                        'occupied_slots': availability['occupied_slots']
                    })
            else:
                summary['completely_occupied'].append({
                    'employee_id': emp_data['employee_id'],
                    'employee_name': emp_data['employee_name'],
                    'department': emp_data['department'],
                    'occupied_slots': availability['occupied_slots']
                })
        
        summary['available_count'] = len(summary['completely_free']) + len(summary['partially_free'])
        summary['occupied_count'] = len(summary['completely_occupied'])
        
        return {
            'status': 'success',
            'data': summary,
            'message': f'Employee availability summary for {date}'
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Employee Availability Summary API Error')
        frappe.throw(_('An error occurred while generating availability summary'))

# Additional debugging function to help identify the correct field names
@frappe.whitelist()
def debug_work_allocation_structure(allocation_name):
    """
    Debug function to help identify the structure of Daily Work Allocation DocType
    """
    try:
        doc = frappe.get_doc('Daily Work Allocation', allocation_name)
        doc_dict = doc.as_dict()
        
        result = {
            'main_fields': {},
            'child_tables': {}
        }
        
        for key, value in doc_dict.items():
            if isinstance(value, list) and len(value) > 0:
                # This is likely a child table
                child_item = value[0]
                if hasattr(child_item, 'as_dict'):
                    result['child_tables'][key] = list(child_item.as_dict().keys())
                else:
                    result['child_tables'][key] = list(child_item.keys()) if isinstance(child_item, dict) else str(type(child_item))
            else:
                result['main_fields'][key] = str(type(value))
        
        return result
        
    except Exception as e:
        return {'error': str(e)}