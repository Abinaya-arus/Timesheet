import frappe


def remove_timetrack_shortcut():
    """Remove TimeSheet shortcut from all workspaces."""
    workspaces = frappe.get_all('Workspace', pluck='name')
    for ws_name in workspaces:
        ws = frappe.get_doc('Workspace', ws_name)
        before = len(ws.shortcuts)
        ws.shortcuts = [s for s in ws.shortcuts if s.link_to != 'timetrack']
        if len(ws.shortcuts) < before:
            ws.save(ignore_permissions=True)
            print(f'Removed from {ws_name}')
    frappe.db.commit()
    print('Done.')


def add_timetrack_shortcut():
    """Add TimeSheet shortcut to the Home workspace for all users."""
    if not frappe.db.exists('Page', 'timetrack'):
        frappe.throw('TimeTrack page not found. Run bench migrate first.')

    workspace_name = 'Home'
    if not frappe.db.exists('Workspace', workspace_name):
        # Fallback: try first available public workspace
        workspace_name = frappe.db.get_value('Workspace', {'public': 1}, 'name')

    if not workspace_name:
        print('No public workspace found.')
        return

    ws = frappe.get_doc('Workspace', workspace_name)

    # Check if shortcut already exists
    for sc in ws.shortcuts:
        if sc.link_to == 'timetrack':
            print('Shortcut already exists.')
            return

    ws.append('shortcuts', {
        'label':   'TimeSheet',
        'type':    'Page',
        'link_to': 'timetrack',
        'icon':    'clock',
        'color':   'Blue',
    })
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print(f'TimeSheet shortcut added to "{workspace_name}" workspace.')
