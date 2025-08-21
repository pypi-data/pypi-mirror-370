import time
import json
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from seleniumwire.utils import decode

def _download(url, **kwargs):
    data = _intercept_network_requests(url, **kwargs)
    traces = data['response']['chart']['figure']['data']
    dfs = _create_dataframes(traces)
    merged_df = pd.concat(dfs, axis=1, join='outer')
    return merged_df

def _create_dataframes(traces):
    dfs = []
    for trace in traces:
        # if 'customdata' in trace:
            name = trace['name']
            x = trace['x']
            y = trace['y']

            length = min(len(x), len(y))
            x = x[:length]
            y = y[:length]

            df = pd.DataFrame({ name: pd.to_numeric(y, errors='coerce') }, index=pd.to_datetime(pd.to_datetime(x, format='mixed').date))
            df = df[~df.index.duplicated(keep='first')]
            df.index.name = 'Date'
            dfs.append(df)

    return dfs

def _intercept_network_requests(url, check_interval=0.5, timeout=30):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Enable headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU for compatibility
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    start_time = time.time()
    request = None

    while time.time() - start_time < timeout:
        for req in driver.requests:
            if "_dash-update-component" in req.url and req.response:
                request = req
                break
        if request:
            break
        time.sleep(check_interval)

    if request:
        content_encoding = request.response.headers.get('Content-Encoding', '')
        body = decode(request.response.body, content_encoding)
        body = body.decode('utf-8', errors='ignore')
        driver.quit()
        return json.loads(body)
    else:
        driver.quit()
        raise TimeoutError(f"Could not find the request within {timeout} seconds. Try increasing the timeout!")
