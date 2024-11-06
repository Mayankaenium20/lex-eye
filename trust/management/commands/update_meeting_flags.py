from django.core.management.base import BaseCommand
from django.utils import timezone
from trust.models import MeetingScheduler

class Command(BaseCommand):
    help = "Updates the `is_proceeding` flag for all existing meetings."

    def handle(self, *args, **kwargs):
        current_datetime = timezone.now()
        meetings = MeetingScheduler.objects.all()
        updated_count = 0
        for meeting in meetings:
            if meeting.meeting_time_date < current_datetime.date() or \
               (meeting.meeting_time_date == current_datetime.date() and meeting.meeting_time_to < current_datetime.time()):
                if not meeting.is_proceeding:
                    meeting.is_proceeding = True
                    meeting.save()
                    updated_count += 1
            elif meeting.is_proceeding:
                meeting.is_proceeding = False
                meeting.save()
                updated_count += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} meetings' flags."))