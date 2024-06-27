import re
from datetime import datetime, timedelta
from currency_converter import CurrencyConverter
from dateparser import parse

TARGET_CURRENCY = "GBP"

class JobCleaner:
    def __init__(self):
        self.cleaning_functions = {
            'title': self.clean_text,
            'company': self.clean_text,
            'location': self.clean_text,
            'description': self.clean_text,
            'created_at': self.clean_date,
            'salary': self.clean_salary,
        }

    def clean(self, key, value, **kwargs):
        cleaning_function = self.cleaning_functions.get(key)
        if cleaning_function:
            return cleaning_function(value, **kwargs)
        else:
            return value
        
    def clean_text(self, s, **kwargs):
        # Remove leading and trailing whitespace
        s = s.strip()
        
        # Replace multiple whitespace characters with a single space
        s = re.sub(r'\s+', ' ', s)
        
        # Remove escape characters
        s = re.sub(r'[\n\r\t\f\v]', '', s)
        
        # Remove ..., more and ... (whitespace) more from the end
        s = re.sub(r'([\.]{3}|…)?(\s*more)?$', '', s)

        return s
    
    def clean_salary(self, salary_str, normalised=True, **kwargs):
        # Remove commas and 'per' from the string for simpler processing
        salary_str = salary_str.replace(',', '').replace('per', '')

        # Regular expression pattern to match salaries
        pattern = r'(\D)(\d+)([kK]?) *(?:- *(\D)(\d+)([kK]?))?'
        
        # Extract matches
        match = re.search(pattern, salary_str)
        
        if match:
            currency1, min_salary, k1, currency2, max_salary, k2 = match.groups()
            
            # If 'k' or 'K' is present, multiply the salary by 1000
            if k1:
                min_salary = int(min_salary) * 1000
            else:
                min_salary = int(min_salary)
                
            if max_salary:
                if k2:
                    max_salary = int(max_salary) * 1000
                else:
                    max_salary = int(max_salary)
            else:
                max_salary = min_salary

        # Map currency symbols to their abbreviations
            currencies = {
                '$': 'USD',
                '£': 'GBP',
                '€': 'EUR'
            }
            
            currency = currencies.get(currency1 or currency2, '')
            
            # Construct the output string
            result = f'{currency1 or currency2}{min_salary}'
            if max_salary != min_salary:
                result += f'-{max_salary}'
            result += f' {currency}'
            
            # Regular expression pattern to match timescale
            pattern = r'(?: *(?:per|\/) *(hour|hr|month|mth|year|yr|annum|an))'
            
            # Extract matches
            match = re.search(pattern, salary_str)
            
            if match:
                time = match.group(1)
                result += f' per {time}'
            else:
                time = "year"

            if normalised:
                normalised_salary = self.normalise_salary(min_salary, currency, time)
                return {
                    'salary': result,
                    'normalised_salary': normalised_salary
                }
            
            return result
        else:
            return None
        
    def normalise_salary(self, salary, currency, time):
        # Create a CurrencyRates object
        c = CurrencyConverter()

        # Convert the salary to the target currency
        if currency != TARGET_CURRENCY:
            salary = c.convert(salary, currency, TARGET_CURRENCY)

        # Convert the salary to per annum
        if time == 'hour' or time == 'hr':
            salary *= 2080  # Assuming 40 hours/week and 52 weeks/year
        elif time == 'month' or time == 'mth':
            salary *= 12

        return salary
    
    def clean_date(self, value, **kwargs):
        # Remove extra words and convert to lowercase
        time_str = value.replace('Posted', '').replace('Created', '').replace('Active', '').strip().lower()

        # Check if 'today' is in the string
        if 'today' in time_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M')

        # Replace '+' with 'ago'
        time_str = time_str.replace('+', 'ago')

        # Check if 'more than' or 'over' is in the string
        if 'more than' in time_str or 'over' in time_str:
            time_str = time_str.replace('more than', '').replace('over', '').strip()
            # Parse the time
            dt = parse(time_str)
            if dt is not None:
                # Add one day to the parsed time because 'more than' or 'over' implies a minimum bound
                return (dt + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')

        # If none of the above conditions are met, try to parse the time directly
        dt = parse(time_str)
        if dt is not None:
            return dt.strftime('%Y-%m-%d %H:%M')
        
        # if adding future functionlity for date parsing as a date to clean date (03/04/2024)
        #  use parse('18-12-15 06:00', settings={'DATE_ORDER': 'DMY'})

        # If all else fails, return None
        return None

def convert_currency(value, currency, target_currency):
    if currency == target_currency:
        return value
    c = CurrencyConverter()
    return c.convert(value, currency, target_currency)