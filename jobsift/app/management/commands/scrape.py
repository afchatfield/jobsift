from django.core.management.base import BaseCommand
from app.scrapers import Scraper, StatusAggregator, JobProfileCollecter
from app.models import JobBoard, JobProfile
from app.services import JobService
import asyncio
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        kwargs = {'normalise': True}

        job_profile = JobProfile.objects.get(id=3)
        collecter = JobProfileCollecter(job_profile)
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(collecter.get_jobs())
        collecter.save_jobs(results, **kwargs)
        # breakpoint()
