import frappe
from frappe.model.document import Document
from datetime import datetime


class TimesheetEntry(Document):

    def validate(self):
        self._calc_duration()
        self._validate_times()

    def _calc_duration(self):
        if self.start_time and self.end_time:
            start = self._to_minutes(str(self.start_time))
            end   = self._to_minutes(str(self.end_time))
            diff  = end - start
            self.duration = round(diff / 60, 2) if diff > 0 else 0

    def _validate_times(self):
        if self.start_time and self.end_time:
            if self._to_minutes(str(self.end_time)) <= self._to_minutes(str(self.start_time)):
                frappe.throw("End Time must be after Start Time.")

    @staticmethod
    def _to_minutes(t):
        parts = t.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Draft"
