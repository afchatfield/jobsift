from app.utils import JobCleaner

import os
from functools import wraps
from inspect import getfullargspec

# from bs4 import BeautifulSoup
import pandas as pd
import asyncio
from pyppeteer import launch
from app.services import JobService


class Scraper:
    def __init__(self):
        self.page = None
        
    # async def scrape_job_board(self, job_board_data, search_params):
    #     print(job_board_data)
    #     # load page
    #     browser = await launch(headless=False)
    #     page = await browser.newPage()
    #     await page.setViewport({ 'width': 2400, 'height': 1200})

    #     await page.goto(job_board_data['url'])

    #     # search navigation collation
    #     search_selectors = {item['selector_type']: item['css_selector'] 
    #         for item in job_board_data['job_board_search_selectors']
    #     }

    #     search_title = search_selectors['search_title']
    #     search_location = search_selectors['search_location']
    #     search_button = search_selectors['search_submit']
    #     next_page = search_selectors['next_page']

    #     # page navigation
    #     await page.waitForSelector(search_title)
    #     await page.waitForSelector(search_location)

    #     await page.type(search_title, 'Software Engineer')
    #     await page.type(search_location, 'UK')

    #     await page.click(search_button)

    #     await page.waitForNavigation()

    #     job_listings = await page.querySelectorAll(search_selectors['result_iterator'])
    #     job_results = []

    #     # selectors
    #     selectors = {item['field']: item['css_selector'] 
    #         for item in job_board_data['job_board_selectors']
    #     }

    #     for job in job_listings[:5]:
    #         job_details = {}
    #         for job_field, css_selector in selectors.items():
    #             print(job_field, css_selector)
    #             try:
    #                 element = await job.querySelector(css_selector)
    #                 print(element)
    #                 job_details[job_field] = await page.evaluate('(element) => element.textContent', element)
    #                 if element:
    #                     print(f'result: {job_details[job_field]}')
    #                 print(f"Success: {job_field}: {job_details[job_field]}")
    #             except ElementHandleError as e:
    #                 print(e)
    #         print("JOB")
    #         print(job_details)
    #         job_results.append(job_details)

    #     await browser.close()
    #     return job_results
    
    def _async_test(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            is_navigator = 'is_navigator' in getfullargspec(func).args
            try:
                result = await func(self, *args, **kwargs)
                if not is_navigator:
                    if 'selector' in getfullargspec(func).args and \
                        (not result or result is None or (isinstance(result, list) and len(result) == 0)):
                        return (None, {'status': 'failed', 'error_message': 'Selector not found'})
                return (result, {'status': 'active'})
            except Exception as e:
                return (None, {'status': 'failed', 'error_message': str(e)})
        return wrapper
    
    async def scrape_jobs(self):
        search_params = {
            'title': self.title,
            'location': self.location,
            'salary': self.salary,
            'description': self.description,
            'sector': self.sector
        }
        job_board_results = []
        for job_board in self.job_boards:
            job_board_data = job_board.get_job_board_data()
            job_results, data_status = await self.scrape_job_board(job_board_data, search_params)
            job_board_results[job_board.id] = {'results': job_results, 'status': data_status}
        return job_board_results
    
    async def scrape_job_board(self, job_board_data, search_params, **kwargs):
        # TODO: replace old scrape_job_boards function when finished
        job_results = []
        # data status refers to status of css selectors and url to check if theyre working
        # job board holds status of css selectors for the job board navigation
        # and jobs for each individual job scraped to be processed later for comprehensive statuses
        data_status = {
            'job_board': {},
            'jobs': []
        }
        # open browser
        browser = await self.open_browser()

        # open url
        _, data_status['job_board']['url'] = await self.get_url(job_board_data['url'])

        # navigation selectors collation
        search_selectors = {item['field']: item['css_selector'] 
            for item in job_board_data['job_board_search_selectors']
        }
        # navigate
        _, data_status['job_board']['search_title'] = await self.navigate(
            search_selectors['search_title'], text=search_params['title']
        )
        _, data_status['job_board']['search_location'] = await self.navigate(
            search_selectors['search_location'], text=search_params['location']
        )
        _, data_status['job_board']['search_submit'] = await self.navigate(search_selectors['search_submit'])

        await self.page.waitForNavigation()

        # get all results on page
        job_listings, data_status['job_board']['result_iterator'] = await self.wait_for_selector(
            selector=search_selectors['result_iterator'], all=True
        )

        # selectors
        selectors = {item['field']: item['css_selector'] 
            for item in job_board_data['job_board_selectors']
        }

        for job in job_listings[:5]:
            job_details, job_status = {}, {}
            for job_field, css_selector in selectors.items():
                result, job_status[job_field] = await self.wait_for_selector(css_selector, job_element=job)
                if result:
                    job_details[job_field] = result
            print("JOB")
            job_results.append(job_details)
            data_status['jobs'].append(job_status)

        await browser.close()
        return job_results, data_status

    async def open_browser(self, viewport={'width': 2000, 'height': 1400}):
        # Browser launch logic here
        browser = await launch(headless=False)
        self.page = await browser.newPage()
        await self.page.setViewport(viewport)
        return browser
    
    @_async_test
    async def get_url(self, url):
        await self.page.goto(url)
    
    @_async_test
    async def navigate(self, selector, text=None, is_navigator=True):
        await self.page.waitForSelector(selector)
        if text:
            await self.page.type(selector, text)
        else:
            await self.page.click(selector)
    
    @_async_test
    async def wait_for_selector(self, selector, job_element=None, all=False):
        if all:
            result = await self.page.querySelectorAll(selector)
        else:
            element = await job_element.querySelector(selector)
            if element is not None:
                result = await self.page.evaluate('(element) => element.textContent', element)
            else:
                result = None
        return result
    
    def clean_job_details(self, job, **kwargs):
        """ clean job details dictionary """
        cleaner = JobCleaner()
        cleaned_job = {}

        if 'title' not in job:
            # Log or raise an error here
            print(f"Error: Job with no title - {job}")
            return None
        
        # Clean title
        cleaned_job['title'] = job['title'].strip()

        # Iterate over the rest of the items and call the master clean function
        for key, value in job.items():
            if key != 'title':
                cleaned_job_detail = cleaner.clean(key, value, **kwargs)
                if isinstance(cleaned_job_detail, dict):
                    cleaned_job.update(cleaned_job_detail)
                else:
                    cleaned_job[key] = cleaned_job_detail

        return cleaned_job
    

class StatusAggregator:
    def __init__(self, status_df):
        self.job_board_selector_status = self.create_job_board_status(status_df)
        self.jobs_selector_status = self.create_job_selector_status(status_df)

    def create_job_board_status(self, df):
        job_board_status = [{'name': key, **value} for key, value in df['job_board'].items()]
        return pd.DataFrame(job_board_status)

    def create_job_selector_status(self, df):
        return pd.json_normalize(df['jobs'])
    
    def aggregate_jobs_selector_status(self):
        aggregated_status = pd.DataFrame(columns=['status'])

        status_columns = [column for column in self.jobs_selector_status.columns if column.endswith('status')]
        error_columns = [column for column in self.jobs_selector_status.columns if column.endswith('error_message')]

        for column in status_columns:
            base_column_name = column.replace('.status', '')

            # Check if there's a custom aggregation method for this column
            if hasattr(self, f'aggregate_{base_column_name}'):
                aggregated_status.loc[base_column_name, 'status'] = getattr(self, f'aggregate_{base_column_name}')()
            else:
                # Default aggregation method: if any are active, consider it active
                aggregated_status.loc[base_column_name, 'status'] = 'active' if (self.jobs_selector_status[column] == 'active').any() else 'failed'

            if aggregated_status.loc[base_column_name, 'status'] == 'failed':
                error_column = [col for col in error_columns if col.startswith(base_column_name)][0]
                if 'error_message' not in aggregated_status.columns:
                    aggregated_status['error_message'] = ''
                aggregated_status.loc[base_column_name, 'error_message'] = self.jobs_selector_status[self.jobs_selector_status[column] == 'failed'][error_column].iloc[0]
        
        if 'error_message' in aggregated_status.columns:
            aggregated_status['error_message'] = aggregated_status['error_message'].replace('', float('nan'))

        return aggregated_status
    
    def get_status(self):
        jobs_selector_status = self.aggregate_jobs_selector_status()
        job_board_selector_status = self.job_board_selector_status.set_index('name')

        comprehensive_status = pd.concat([job_board_selector_status, jobs_selector_status], ignore_index=False)

        return comprehensive_status
    
    def aggregate_average(self, series, threshold=90):
        # Calculate the percentage of 'active' responses
        active_percentage = (series == 'active').mean() * 100
        
        # If the percentage is over the threshold, return 'active'
        if active_percentage > threshold:
            return 'active'
        else:
            # Otherwise, return the most popular 'other' value
            other_values = series[series != 'active']
            return other_values.mode().iloc[0]
        
    def aggregate_location(self):
        return self.aggregate_average(self.jobs_selector_status['location.status'], threshold=25)
    
    def aggregate_title(self):
        return self.aggregate_average(self.jobs_selector_status['title.status'])
    
    def aggregate_company(self):
        return self.aggregate_average(self.jobs_selector_status['company.status'], threshold=50)
    

class JobProfileCollecter:
    def __init__(self, job_profile):
        self.job_profile = job_profile
        self.scraper = Scraper()
        self.job_boards = self.job_profile.job_boards.all()
        self.job_board_data = [job_board.get_job_board_data() for job_board in self.job_boards]

    async def get_jobs(self):
        search_params = {
            'title': self.job_profile.title,
            'location': self.job_profile.location,
            'salary': self.job_profile.salary,
            'description': self.job_profile.description,
            'sector': self.job_profile.sector
        }
        job_board_results = {}
        for job_board_data in self.job_board_data:
            job_results, data_status = await self.scraper.scrape_job_board(job_board_data, search_params)
            job_board_results[job_board_data['id']] = {'results': job_results, 'status': data_status}
        return job_board_results

    def save_jobs(self, results, **kwargs):
        for job_board_id, data in results.items():
            print(f"Job Board ID: {job_board_id}")
            cleaned_jobs = [self.scraper.clean_job_details(job, **kwargs) for job in data['results']]
            print(pd.DataFrame(cleaned_jobs))
            breakpoint()
            for job in cleaned_jobs:
                JobService.create_or_update_job(job_board_id, job, job_profile=self.job_profile.id)

            status = StatusAggregator(data['status'])
            status_df = status.get_status()
            print(status_df)
            JobService.create_or_update_selector_status(job_board_id, status_df)


if __name__ == "__main__":
    s = Scraper()
    jobs = asyncio.run(s.scrape_job_board(1, {}))
    print(jobs)