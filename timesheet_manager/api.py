import frappe
from frappe import _
from frappe.utils import today, nowdate


# ── Auth ──────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_current_user():
    user     = frappe.session.user
    roles    = frappe.get_roles(user)
    is_admin = bool({'HR Manager', 'System Manager'} & set(roles))
    full_name = frappe.db.get_value('User', user, 'full_name') or user
    employee  = _get_employee_for_user(user)
    return {
        'name':      user,
        'full_name': full_name,
        'is_admin':  is_admin,
        'employee':  employee,
        'roles':     roles,
    }


# ── Timesheet Entries ─────────────────────────────────────────────────────────

@frappe.whitelist()
def get_entries(date=None, employee=None):
    user     = frappe.session.user
    roles    = frappe.get_roles(user)
    is_admin = bool({'HR Manager', 'System Manager'} & set(roles))

    filters = {}
    if employee and is_admin:
        filters['employee'] = employee
    else:
        emp = _get_employee_for_user(user)
        if emp:
            filters['employee'] = emp

    if date:
        filters['date'] = date

    entries = frappe.get_all(
        'Timesheet Entry',
        filters=filters,
        fields=['name', 'date', 'project', 'activity_type', 'start_time',
                'end_time', 'duration', 'description', 'status', 'task_completed'],
        order_by='date desc, start_time asc',
    )
    return entries


@frappe.whitelist()
def create_entry(date, project, activity_type, start_time, end_time,
                 description='', task_completed=0):
    employee = _get_employee_for_user(frappe.session.user)
    if not employee:
        frappe.throw(_('No Employee record linked to your account.'))
    doc = frappe.get_doc({
        'doctype':       'Timesheet Entry',
        'employee':      employee,
        'date':          date,
        'project':       project,
        'activity_type': activity_type,
        'start_time':    start_time,
        'end_time':      end_time,
        'description':   description,
        'task_completed': task_completed,
        'status':        'Draft',
    })
    doc.insert()
    frappe.db.commit()
    return {'name': doc.name, 'status': doc.status, 'duration': doc.duration}


@frappe.whitelist()
def update_entry(name, **kwargs):
    doc = frappe.get_doc('Timesheet Entry', name)
    _check_ownership(doc)
    allowed = {'date', 'project', 'activity_type', 'start_time',
               'end_time', 'description', 'task_completed'}
    for k, v in kwargs.items():
        if k in allowed:
            setattr(doc, k, v)
    doc.save()
    frappe.db.commit()
    return {'name': doc.name, 'duration': doc.duration}


@frappe.whitelist()
def submit_entry(name):
    doc = frappe.get_doc('Timesheet Entry', name)
    _check_ownership(doc)
    doc.status = 'Submitted'
    doc.save()
    frappe.db.commit()
    return {'status': doc.status}


@frappe.whitelist()
def submit_day(date):
    emp = _get_employee_for_user(frappe.session.user)
    if not emp:
        frappe.throw(_('No Employee linked to your account.'))
    entries = frappe.get_all(
        'Timesheet Entry',
        filters={'employee': emp, 'date': date, 'status': 'Draft'},
        pluck='name',
    )
    for name in entries:
        doc = frappe.get_doc('Timesheet Entry', name)
        doc.status = 'Submitted'
        doc.save()
    frappe.db.commit()
    return {'submitted': len(entries)}


@frappe.whitelist()
def approve_day(date, employee):
    frappe.only_for(['HR Manager', 'System Manager'])
    entries = frappe.get_all(
        'Timesheet Entry',
        filters={'employee': employee, 'date': date, 'status': ['!=', 'Approved']},
        pluck='name',
    )
    for name in entries:
        doc = frappe.get_doc('Timesheet Entry', name)
        doc.status     = 'Approved'
        doc.approved_by = frappe.session.user
        doc.save()
    frappe.db.commit()
    _notify_employee_approval(employee, date, 'approved')
    return {'approved': len(entries)}


@frappe.whitelist()
def delete_entry(name):
    doc = frappe.get_doc('Timesheet Entry', name)
    if doc.status != 'Draft':
        frappe.throw(_('Only Draft entries can be deleted.'))
    _check_ownership(doc)
    frappe.delete_doc('Timesheet Entry', name)
    frappe.db.commit()
    return {'deleted': name}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_dashboard_stats(date=None, employee=None):
    if not date:
        date = today()
    user     = frappe.session.user
    roles    = frappe.get_roles(user)
    is_admin = bool({'HR Manager', 'System Manager'} & set(roles))

    if employee and is_admin:
        emp = employee
    else:
        emp = _get_employee_for_user(user)

    filters = {'date': date}
    if emp:
        filters['employee'] = emp

    entries    = frappe.get_all('Timesheet Entry', filters=filters,
                                fields=['duration', 'status', 'project'])
    total_h    = round(sum(e.duration or 0 for e in entries), 2)
    projects   = len({e.project for e in entries if e.project})
    return {
        'hours':    total_h,
        'projects': projects,
        'entries':  len(entries),
        'date':     date,
    }


# ── Analytics ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_analytics(period='daily', date=None):
    if not date:
        date = today()
    emp     = _get_employee_for_user(frappe.session.user)
    filters = {'employee': emp} if emp else {}

    if period == 'daily':
        filters['date'] = date
    elif period == 'weekly':
        filters['date'] = ['between', [_week_start(date), date]]
    elif period == 'monthly':
        filters['date'] = ['between', [_month_start(date), date]]

    entries = frappe.get_all(
        'Timesheet Entry', filters=filters,
        fields=['activity_type', 'project', 'duration', 'date', 'start_time', 'end_time'],
    )
    by_activity, by_project = {}, {}
    for e in entries:
        h = e.duration or 0
        by_activity[e.activity_type] = round(by_activity.get(e.activity_type, 0) + h, 2)
        by_project[e.project]        = round(by_project.get(e.project, 0) + h, 2)

    return {
        'by_activity': [{'label': k, 'hours': v} for k, v in by_activity.items()],
        'by_project':  [{'label': k, 'hours': v} for k, v in by_project.items()],
        'total':       round(sum(e.duration or 0 for e in entries), 2),
        'entries':     entries,
    }


# ── Admin ─────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_employees():
    frappe.only_for(['HR Manager', 'System Manager'])
    employees = frappe.get_all(
        'Employee',
        filters={'status': 'Active'},
        fields=['name', 'employee_name', 'department', 'user_id', 'image'],
    )
    result = []
    for emp in employees:
        initials = ''.join(w[0].upper() for w in (emp.employee_name or '').split()[:2])
        result.append({
            'id':         emp.name,
            'name':       emp.employee_name,
            'dept':       emp.department or '',
            'initials':   initials or emp.name[:2].upper(),
            'user_id':    emp.user_id,
        })
    return result


@frappe.whitelist()
def get_pending_approvals():
    frappe.only_for(['HR Manager', 'System Manager'])
    entries = frappe.get_all(
        'Timesheet Entry',
        filters={'status': 'Submitted'},
        fields=['name', 'employee', 'date', 'project', 'activity_type',
                'start_time', 'end_time', 'duration', 'description'],
        order_by='date asc',
    )
    # Group by employee → date
    grouped = {}
    for e in entries:
        emp_name = frappe.db.get_value('Employee', e.employee, 'employee_name') or e.employee
        dept     = frappe.db.get_value('Employee', e.employee, 'department') or ''
        key      = e.employee
        if key not in grouped:
            grouped[key] = {'employee_id': e.employee, 'employee_name': emp_name,
                            'dept': dept, 'days': {}}
        date_key = str(e.date)
        if date_key not in grouped[key]['days']:
            grouped[key]['days'][date_key] = []
        grouped[key]['days'][date_key].append(e)

    result = []
    for emp_id, emp_data in grouped.items():
        days = [
            {
                'date':       d,
                'status':     'Submitted',
                'entries':    entries_list,
                'total_hours': round(sum((en.duration or 0) for en in entries_list), 2),
            }
            for d, entries_list in sorted(emp_data['days'].items())
        ]
        initials = ''.join(w[0].upper() for w in emp_data['employee_name'].split()[:2])
        result.append({
            'employee_id':   emp_id,
            'name':          emp_data['employee_name'],
            'dept':          emp_data['dept'],
            'initials':      initials,
            'pending_days':  len(days),
            'days':          days,
        })
    return result


# ── Notifications ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_notifications():
    emp = _get_employee_for_user(frappe.session.user)
    if not emp:
        return []
    recent = frappe.get_all(
        'Timesheet Entry',
        filters={'employee': emp, 'status': ['in', ['Approved', 'Rejected']]},
        fields=['name', 'date', 'project', 'status', 'rejection_reason', 'modified'],
        order_by='modified desc',
        limit=20,
    )
    notifs = []
    for e in recent:
        notifs.append({
            'id':    e.name,
            'type':  e.status.lower(),
            'title': f'Timesheet {e.status}',
            'body':  (f'Reason: {e.rejection_reason}' if e.status == 'Rejected'
                      else f'Your {e.date} timesheet ({e.project}) was approved'),
            'time':  str(e.modified),
            'unread': True,
        })
    return notifs


@frappe.whitelist()
def mark_notification_read(name):
    return {'ok': True}


# ── Projects ──────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_projects():
    projects = frappe.get_all(
        'Timesheet Project',
        fields=['name', 'project_name'],
        order_by='project_name asc',
    ) if frappe.db.table_exists('tabTimesheet Project') else []

    if projects:
        return [p.project_name for p in projects]

    # Fall back to distinct project values already logged in timesheets
    raw = frappe.db.sql(
        "SELECT DISTINCT project FROM `tabTimesheet Entry` WHERE project IS NOT NULL AND project != '' ORDER BY project",
        as_dict=True,
    )
    return [r.project for r in raw]


@frappe.whitelist()
def add_project(name):
    frappe.only_for(['HR Manager', 'System Manager'])
    if frappe.db.table_exists('tabTimesheet Project'):
        if not frappe.db.exists('Timesheet Project', {'project_name': name}):
            doc = frappe.get_doc({'doctype': 'Timesheet Project', 'project_name': name})
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
    return {'name': name}


@frappe.whitelist()
def delete_project(name):
    frappe.only_for(['HR Manager', 'System Manager'])
    if frappe.db.table_exists('tabTimesheet Project'):
        existing = frappe.db.get_value('Timesheet Project', {'project_name': name}, 'name')
        if existing:
            frappe.delete_doc('Timesheet Project', existing, ignore_permissions=True)
            frappe.db.commit()
    return {'deleted': name}


@frappe.whitelist()
def rename_project(old_name, new_name):
    frappe.only_for(['HR Manager', 'System Manager'])
    if frappe.db.table_exists('tabTimesheet Project'):
        existing = frappe.db.get_value('Timesheet Project', {'project_name': old_name}, 'name')
        if existing:
            doc = frappe.get_doc('Timesheet Project', existing)
            doc.project_name = new_name
            doc.save(ignore_permissions=True)
            frappe.db.commit()
    return {'old': old_name, 'new': new_name}


@frappe.whitelist()
def get_project_hours():
    frappe.only_for(['HR Manager', 'System Manager'])
    rows = frappe.db.sql("""
        SELECT te.project, e.employee_name, e.department, SUM(te.duration) as hours
        FROM `tabTimesheet Entry` te
        JOIN `tabEmployee` e ON te.employee = e.name
        WHERE te.status IN ('Submitted', 'Approved')
          AND te.project IS NOT NULL AND te.project != ''
        GROUP BY te.project, te.employee
        ORDER BY te.project, hours DESC
    """, as_dict=True)

    grouped = {}
    for r in rows:
        if r.project not in grouped:
            grouped[r.project] = {'name': r.project, 'total': 0, 'employees': []}
        grouped[r.project]['employees'].append({
            'name':  r.employee_name,
            'dept':  r.department or '',
            'hours': round(float(r.hours or 0), 2),
        })
        grouped[r.project]['total'] = round(
            grouped[r.project]['total'] + float(r.hours or 0), 2)

    return list(grouped.values())


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_employee_for_user(user):
    return frappe.db.get_value('Employee', {'user_id': user}, 'name')


def _check_ownership(doc):
    emp = _get_employee_for_user(frappe.session.user)
    roles = frappe.get_roles(frappe.session.user)
    if doc.employee != emp and not bool({'HR Manager', 'System Manager'} & set(roles)):
        frappe.throw(_('Not permitted.'), frappe.PermissionError)


def _notify_employee_approval(employee, date, action):
    user_id = frappe.db.get_value('Employee', employee, 'user_id')
    if user_id:
        frappe.sendmail(
            recipients=[user_id],
            subject=f'Timesheet {action.capitalize()} — {date}',
            message=f'Your timesheet for {date} has been {action}.',
        )


def _week_start(date_str):
    from datetime import datetime, timedelta
    d = datetime.strptime(date_str, '%Y-%m-%d')
    return (d - timedelta(days=d.weekday())).strftime('%Y-%m-%d')


def _month_start(date_str):
    return date_str[:7] + '-01'
