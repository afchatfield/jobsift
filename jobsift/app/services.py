from django.db import transaction
from .models import Job, JobBoard, JobBoardSelector, JobBoardSearchSelector, SelectorStatus

class JobService:
    @staticmethod
    def create_or_update_job(job_board_id, job_data, job_profile=None):
        try:
            job_board = JobBoard.objects.get(id=job_board_id)
        except JobBoard.DoesNotExist:
            raise ValueError(f"Job board with id {job_board_id} does not exist")

        with transaction.atomic():
            try:
                job, created = Job.objects.get_or_create(
                    job_board=job_board,
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary=job_data['salary'],
                    job_profile=job_profile,
                    defaults=job_data
                )
            except KeyError:
                job, created = Job.objects.get_or_create(
                    job_board=job_board,
                    title=job_data['title'],
                    company=job_data['company'],
                    job_profile=job_profile,
                    defaults=job_data
                )

        return job
    
    @staticmethod
    def create_or_update_selector_status(job_board_id, status_df):
        try:
            job_board = JobBoard.objects.get(id=job_board_id)
        except JobBoard.DoesNotExist:
            raise ValueError(f"Job board with id {job_board_id} does not exist")
        
        search_selectors = [selector[0] for selector in JobBoardSearchSelector.SELECTOR_TYPES]

        with transaction.atomic():
            for index, row in status_df.iterrows():
                if index == 'url':
                    continue
                # Check if the selector is a search selector or a regular selector
                if index in search_selectors:
                    selector_model = JobBoardSearchSelector
                    selector_kwargs = {'selector_type': index}
                else:
                    selector_model = JobBoardSelector
                    selector_kwargs = {'job_field': index}

                # Get the selector object
                selector = selector_model.objects.get(job_board=job_board, **selector_kwargs)

                # Create or update the SelectorStatus object
                selector.status.update_or_create(
                    defaults=row.to_dict()
                )
