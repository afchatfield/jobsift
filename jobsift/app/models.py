from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

# Create your models here.

class JobBoard(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()

    def get_job_board_data(self):
        job_board_selectors = self.selectors.all()
        job_board_search_selectors = self.search_selectors.all()
        data = {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'job_board_selectors': [
                {
                    'field': selector.job_field,
                    'css_selector': selector.css_selector,
                    'status': selector.status.first().status if selector.status.exists() else None,
                    'error_message': selector.status.first().error_message if selector.status.exists() else None,
                } for selector in job_board_selectors
            ],
            'job_board_search_selectors': [
                {
                    'field': selector.selector_type,
                    'css_selector': selector.css_selector,
                    'status': selector.status.first().status if selector.status.exists() else None,
                    'error_message': selector.status.first().error_message if selector.status.exists() else None,
                } for selector in job_board_search_selectors
            ],
            'status': self.get_status(),
        }
        return data
    
    def get_status(self):
        job_board_selectors = self.selectors.all()
        job_board_search_selectors = self.search_selectors.all()

        # Initialize the overall status to 'Active'
        overall_status = 'active'

        # Check the status of the search selectors
        important_search_selectors = ['search_title', 'search_location', 'search_submit', 'result_iterator']
        for selector in job_board_search_selectors:
            current_status = selector.status.first()
            if current_status:
                if selector.selector_type in important_search_selectors and current_status.status != 'active':
                    overall_status = current_status.status or 'failed'
                    break
            elif selector.selector_type in important_search_selectors:
                overall_status = 'inactive'

        # If the search selectors are all active, check the status of the regular selectors
        if overall_status == 'active':
            title_selector = [selector for selector in job_board_selectors if selector.job_field == 'title']
            if title_selector:  # If title selector exists
                title_status = title_selector[0].status.first() 
                if title_status and title_status.status != 'active':
                    overall_status = title_status.status
            else:
                overall_status = 'inactive'

        if overall_status == 'active':
            inactive_selectors = [selector for selector in job_board_selectors if selector.job_field != 'title' and 
                                (not selector.status.exists() or selector.status.first().status != 'active')]
            if inactive_selectors:
                overall_status = 'partially_active'

        return overall_status

    def __str__(self):
        return self.name
    


class JobProfile(models.Model):
    job_boards = models.ManyToManyField(JobBoard, related_name='job_profiles')
    status = models.CharField(max_length=20, default='inactive', choices=[('active', 'Active'), ('inactive', 'Inactive')])
    quota = models.IntegerField(default=50)  # adjust the default quota as needed
    title = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sector = models.CharField(max_length=255, blank=True)
    # Add more fields as needed, or consider using a separate model for job template fields
    colour = models.CharField(max_length=7, default='#FFFFFF')  # store color as a hex code

    def __str__(self):
        return f"{self.title} - Profile"
    
    def clean(self):
        if not self.colour.startswith('#') or len(self.colour) != 7:
            raise ValidationError({'colour': 'Invalid hex colour value'})

        if self.quota < 0:
            raise ValidationError({'quota': 'Quota cannot be negative'})
        

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)

    JOB_TYPE_CHOICES = (
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('unspecified', 'Unspecified')
    )
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='unspecified')

    WORKING_MODEL_CHOICES = (
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('on-site', 'On Site'),
        ('unspecified', 'Unspecified'),
    )
    working_model = models.CharField(max_length=25, choices=WORKING_MODEL_CHOICES, default='unspecified')

    # Job Details
    salary = models.CharField(max_length=50, blank=True)
    normalised_salary = models.IntegerField(blank=True, null=True)
    benefits = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    experience = models.TextField(blank=True, null=True)
    hours = models.CharField(max_length=50, blank=True)

    company_website = models.URLField(blank=True)

    EDUCATION_CHOICES = (
        ('high-school', 'High School'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    )
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    
    # Application and Deadline
    application_email = models.EmailField(blank=True)
    application_url = models.URLField(blank=True)
    deadline = models.DateField(blank=True, null=True)
    
    # Timestamps
    # job posting date published
    created_at = models.DateTimeField(blank=True, null=True)
    # job posting scraped
    pulled_at = models.DateTimeField(auto_now=True)

    # Foreign Key to JobBoard
    job_board = models.ForeignKey(JobBoard, on_delete=models.CASCADE)

    # Foreign Key to JobProfile
    job_profile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('title', 'company', 'location', 'salary')


class SelectorStatus(models.Model):
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True, default='')

    # Generic foreign key to link to either JobBoardSearchSelector or JobBoardSelector
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    selector = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.selector} - status"

    def clean(self):
        if self.content_type.model not in ['jobboardsearchselector', 'jobboardselector']:
            raise ValidationError('Selector must be either a JobBoardSearchSelector or JobBoardSelector')
        
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class JobBoardSelector(models.Model):
    job_board = models.ForeignKey(JobBoard, on_delete=models.CASCADE, related_name='selectors')

    job_field = models.CharField(max_length=255) 
    css_selector = models.TextField(blank=False)

    # status relation
    status = GenericRelation(SelectorStatus)

    class Meta:
        unique_together = ('job_board', 'job_field')

    def __str__(self):
        return f'{self.job_board} - {self.job_field}'
    

class JobBoardSearchSelector(models.Model):
    SELECTOR_TYPES = (
        ("search_title", "Search Title Input"),
        ("search_location", "Search Location Input"),
        ("search_submit", "Search Submit Button"),
        ("next_page", "Next Page Button"),
        ("result_iterator", "Result Iterator")
    )

    job_board = models.ForeignKey(JobBoard, on_delete=models.CASCADE, related_name="search_selectors")
    selector_type = models.CharField(max_length=100, choices=SELECTOR_TYPES)
    css_selector = models.TextField(blank=False)

    status = GenericRelation(SelectorStatus)

    def clean(self):
        if not self.css_selector.strip():
            raise ValidationError("CSS selector cannot be blank")
        
    class Meta:
        unique_together = ('job_board', 'selector_type')

    def __str__(self):
        return f"{self.job_board} - {self.selector_type}"