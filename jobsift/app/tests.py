from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import JobBoard, Job, JobBoardSelector, JobBoardSearchSelector, SelectorStatus, JobProfile

class TestJobBoard(TestCase):
    def setUp(self):
        self.job_board = JobBoard.objects.create(name='Test Job Board', url='https://testjobboard.com')

    def test_job_board_creation(self):
        self.assertEqual(self.job_board.name, 'Test Job Board')
        self.assertEqual(self.job_board.url, 'https://testjobboard.com')

class TestJob(TestCase):
    def setUp(self):
        self.job_board = JobBoard.objects.create(name='Test Job Board', url='https://testjobboard.com')
        self.job = Job.objects.create(
            title='Test Job',
            description='This is a test job',
            company='Test Company',
            location='Test Location',
            job_type='full-time',
            # category='software-development',
            salary='100000',
            # experience=5,
            education='bachelor',
            skills='Python, Django, JavaScript',
            application_email='test@email.com',
            application_url='https://testjobapplication.com',
            deadline='2022-12-31',
            job_board=self.job_board
        )

    def test_job_creation(self):
        self.assertEqual(self.job.title, 'Test Job')
        self.assertEqual(self.job.description, 'This is a test job')
        self.assertEqual(self.job.company, 'Test Company')
        self.assertEqual(self.job.location, 'Test Location')
        self.assertEqual(self.job.job_type, 'full-time')
        # self.assertEqual(self.job.category, 'software-development')
        self.assertEqual(self.job.salary, '100000')
        # self.assertEqual(self.job.experience, 5)
        self.assertEqual(self.job.education, 'bachelor')
        self.assertEqual(self.job.skills, 'Python, Django, JavaScript')
        self.assertEqual(self.job.application_email, 'test@email.com')
        self.assertEqual(self.job.application_url, 'https://testjobapplication.com')
        self.assertEqual(self.job.deadline, '2022-12-31')
        self.assertEqual(self.job.job_board, self.job_board)


class TestJobBoardSelector(TestCase):
    def setUp(self):
        self.job_board = JobBoard.objects.create(name='Test Job Board')

    def test_create_job_board_selector(self):
        job_board_selector = JobBoardSelector.objects.create(
            job_board=self.job_board,
            job_field='title',
            css_selector='#job-title'
        )
        self.assertEqual(job_board_selector.job_board.name, 'Test Job Board')
        self.assertEqual(job_board_selector.job_field, 'title')
        self.assertEqual(job_board_selector.css_selector, '#job-title')

    def test_unique_together_constraint(self):
        JobBoardSelector.objects.create(
            job_board=self.job_board,
            job_field='title',
            css_selector='#job-title'
        )
        with self.assertRaises(IntegrityError):
            JobBoardSelector.objects.create(
                job_board=self.job_board,
                job_field='title',
                css_selector='#job-title'
            )

    def test_job_board_foreign_key(self):
        job_board_selector = JobBoardSelector.objects.create(
            job_board=self.job_board,
            job_field='title',
            css_selector='#job-title'
        )
        self.assertEqual(job_board_selector.job_board, self.job_board)
        self.assertEqual(job_board_selector.job_board.name, 'Test Job Board')

    def test_string_representation(self):
        job_board_selector = JobBoardSelector.objects.create(
            job_board=self.job_board,
            job_field='title',
            css_selector='#job-title'
        )
        self.assertEqual(str(job_board_selector), f'{self.job_board} - title')

    def test_empty_css_selector(self):
        selector = JobBoardSelector.objects.create(
                job_board=self.job_board,
                job_field="company",
                css_selector=""
            )
        with self.assertRaises(ValidationError):
            selector.full_clean()

class TestSearchNavigationSelectorModel(TestCase):
    def setUp(self):
        self.job_board = JobBoard.objects.create(name="Test Job Board")
        self.selector = JobBoardSearchSelector.objects.create(
            job_board=self.job_board,
            selector_type="search_title",
            css_selector="#title"
        )

    def test_search_navigation_selector_creation(self):
        self.assertEqual(self.selector.job_board, self.job_board)
        self.assertEqual(self.selector.selector_type, "search_title")
        self.assertEqual(self.selector.css_selector, "#title")

    def test_search_navigation_selector_str_representation(self):
        expected_str = f"{self.job_board.name} - search_title"
        self.assertEqual(str(self.selector), expected_str)

    def test_invalid_selector_type(self):
        selector = JobBoardSearchSelector.objects.create(
            job_board=self.job_board,
            selector_type="invalid_type",
            css_selector="#title"
        )
        with self.assertRaises(ValidationError):
            selector.full_clean()

    def test_empty_css_selector(self):
        selector = JobBoardSearchSelector.objects.create(
            job_board=self.job_board,
            selector_type="search_location",
            css_selector=""
        )
        with self.assertRaises(ValidationError):
            selector.full_clean()


class TestSelectorStatusModel(TestCase):
    def setUp(self):
        self.job_board = JobBoard.objects.create(name="Test Job Board")

        self.selector = JobBoardSelector.objects.create(
            job_board=self.job_board,
            job_field='title',
            css_selector='#job-title'
        )
        self.selector_status = SelectorStatus.objects.create(
            status='inactive',
            selector=self.selector
        )

        self.search_selector = JobBoardSearchSelector.objects.create(
            job_board=self.job_board,
            selector_type="search_title",
            css_selector="#title"
        )
        self.search_selector_status = SelectorStatus.objects.create(
            status='active',
            selector=self.search_selector
        )

    def test_create(self):
        self.assertEqual(self.selector_status.status, 'inactive')
        self.assertEqual(self.selector_status.selector, self.selector)
        self.assertEqual(self.selector_status.selector.job_board, self.selector.job_board)
        self.assertEqual(self.selector_status.selector.job_board, self.job_board)

        self.assertEqual(self.search_selector_status.status, 'active')
        self.assertEqual(self.search_selector_status.selector, self.search_selector)
        self.assertEqual(self.search_selector_status.selector.job_board, self.search_selector.job_board)
        self.assertEqual(self.search_selector_status.selector.job_board, self.job_board)

    def test_status_selector_str_representation(self):
        expected_str = f"{self.selector} - status"
        self.assertEqual(str(self.selector_status), expected_str)
        expected_str = f"{self.search_selector} - status"
        self.assertEqual(str(self.search_selector_status), expected_str)

    def test_job_board_status(self):
        job_board_selector = self.job_board.selectors.all()[0]
        job_board_selector_status = job_board_selector.status.all()[0]
        self.assertEqual(job_board_selector_status, self.selector_status)

        job_board_search_selector = self.job_board.search_selectors.all()[0]
        job_board_search_selector_status = job_board_search_selector.status.all()[0]
        self.assertEqual(job_board_search_selector_status, self.search_selector_status)

    def test_selector_status_error_message(self):
        status = SelectorStatus.objects.create(
            status='failed',
            selector=self.selector,
            error_message='This is an error message'
        )
        self.assertEqual(status.error_message, 'This is an error message')

    def test_invalid_selector_type(self):
        with self.assertRaises(ValidationError):
            selector_status = SelectorStatus(
                status='working',
                selector=self.job_board  # invalid selector type
            )
            selector_status.clean()


class TestJobProfileModel(TestCase):
    def setUp(self):
        self.job_board1 = JobBoard.objects.create(name='Job Board 1')
        self.job_board2 = JobBoard.objects.create(name='Job Board 2')

    def test_many_to_many_relationship(self):
        job_profile = JobProfile.objects.create(title='Test Job Profile')
        job_profile.job_boards.add(self.job_board1)
        job_profile.job_boards.add(self.job_board2)
        self.assertEqual(job_profile.job_boards.count(), 2)
        self.assertIn(job_profile, self.job_board1.job_profiles.all())
        self.assertIn(job_profile, self.job_board2.job_profiles.all())

    def test_colour_field_validation(self):
        job_profile = JobProfile.objects.create(title='Test Job Profile')
        job_profile.colour = 'not a hex value'
        with self.assertRaises(ValidationError):
            job_profile.full_clean()

    def test_quota_cannot_be_negative(self):
        job_profile = JobProfile.objects.create(title='Test Job Profile')
        job_profile.quota = -1
        with self.assertRaises(ValidationError):
            job_profile.full_clean()

    def test_quota_can_be_zero(self):
        job_profile = JobProfile.objects.create(title='Test Job Profile')
        job_profile.quota = 0
        job_profile.full_clean()  # should not raise an error