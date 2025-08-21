import time
import json
from urllib.parse import urlparse
from selenium import webdriver
import pandas as pd

CRYPTOQUANT_URL = "https://cryptoquant.com/"

def _download(url, **kwargs):
    email = kwargs.get('email')
    password = kwargs.get('password')
    if not email or not password:
        raise TypeError("Email and/or password hasn't been passed")

    splits = urlparse(url).path.split('/')
    id = splits[-1]

    # Cryptoquant's own metrics
    if splits[1] == 'asset':
        raise NotImplementedError("Only third party metrics on cryptoquant have been implemented.")

    proxy = kwargs.get('proxy', None)
    driver = _get_driver(proxy=proxy)

    data = _get_json(driver, id, email, password)

    columns = data['data']['result']['columns']
    results = data['data']['result']['results']
    column_names = [col['name'] for col in columns]

    return _create_dataframe(results, column_names)

def _create_dataframe(results, column_names):
    df = pd.DataFrame(results, columns=column_names)
    
    date_column = None
    for col in df.columns:
        if col.lower() in ['day', 'date', 'datetime', 'transaction_day']:
            date_column = col
            break
    
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column])
        df.set_index(date_column, inplace=True)
        df.index.name = 'Date'
    else:
        print("Unable to find and parse the date column")
    
    return df

def _get_driver(proxy=None):
    chrome_options = webdriver.ChromeOptions()

    if proxy:
        driver = webdriver.Remote(proxy, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def _get_json(driver, id, email, password):
    driver.get(CRYPTOQUANT_URL)
    time.sleep(4)

    # Execute the login request
    script = f"""
        return fetch("https://api.cryptoquant.com/live/v1/sign-in", {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{
                "email": "{email}",
                "password": "{password}"
            }})
        }}).then(response => response.json());
    """
    response = driver.execute_script(script)

    if 'accessToken' in response:
        access_token = response['accessToken']

        data_url = f"https://api.cryptoquant.com/live/v1/analytics/{id}"
        
        result_script = f"""
            return fetch("{data_url}", {{
                method: 'GET',
                headers: {{
                    'Authorization': 'Bearer {access_token}',
                    'Accept': 'application/json'
                }}
            }}).then(response => response.json());
        """
        result = driver.execute_script(result_script)
    else:
        print(f"Error occurred: {response.get('error')}")
        driver.quit()
        return {}

    driver.quit()
    return result
