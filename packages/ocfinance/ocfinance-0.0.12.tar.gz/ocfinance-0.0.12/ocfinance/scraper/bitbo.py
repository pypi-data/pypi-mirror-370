import re
import json
import time
import pandas as pd

from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By

from seleniumbase import SB
from selenium.common.exceptions import StaleElementReferenceException

def _download(url, **kwargs):
    content = _get_script_content(url, **kwargs)
    traces = _get_traces(content)

    dfs = []
    for trace in traces:
        name, x, y = _get_data(trace, content)

        df = pd.DataFrame({ name: pd.to_numeric(y, errors='coerce') }, index=pd.to_datetime(x))
        df.index.name = 'Date'
        dfs.append(df)

    merged_df = pd.concat(dfs, axis=1, join='outer')
    return merged_df

def _get_script_content(url, **kwargs):
    sbr_webdriver = kwargs.get('sbr_webdriver')
    if sbr_webdriver:
        return _get_script_content_brightdata(url, sbr_webdriver)
    else:
        return _get_script_content_seleniumbase(url)

def _get_script_content_brightdata(url, sbr_webdriver):
    sbr_connection = ChromiumRemoteConnection(sbr_webdriver, 'goog', 'chrome')
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        driver.get(url)

        # CAPTCHA handling: If you're expecting a CAPTCHA on the target page, use the following code snippet to check the status of Scraping Browser's automatic CAPTCHA solver
        print('Waiting captcha to solve...')
        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params': {'detectTimeout': 20000},
        })
        print('Captcha solve status:', solve_res['value']['status'])

        script_content = ""
        script_tags = driver.find_elements(By.TAG_NAME, 'script')
        for script_tag in script_tags:
            script_inner_html = script_tag.get_attribute("innerHTML")
            if script_inner_html and 'trace' in script_inner_html:
                script_content += script_inner_html
    
    return script_content

def _get_script_content_seleniumbase(url):
    script_content = ""
    with SB(uc=True) as sb:
        sb.uc_open_with_reconnect(url, 4)
        sb.uc_gui_click_captcha()

        attempts = 0
        while attempts < 3:
            try:
                script_tags = sb.find_elements("script")
                for script_tag in script_tags:
                    script_inner_html = script_tag.get_attribute("innerHTML")
                    if script_inner_html and 'trace' in script_inner_html:
                        script_content += script_inner_html
                break
            except StaleElementReferenceException:
                attempts += 1
                time.sleep(1)

    return script_content

def _get_traces(content):
    trace_pattern = r'var\s+trace\d+\s*=\s*(\{.*?\});'
    traces = re.findall(trace_pattern, content, re.DOTALL)
    return traces

def _get_data(trace, content):
    x_pattern = r'x:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,'
    y_pattern = r'y:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,'
    name_pattern = r"name:\s*'([^']*)'"
    var_pattern = r'var\s+({name})\s*=\s*([^;]*);'

    name = ""
    x, y = [], []

    x_match = re.search(x_pattern, trace)
    y_match = re.search(y_pattern, trace)

    if x_match and y_match:
        x_var_name = x_match.group(1)
        y_var_name = y_match.group(1)

        x_var_pattern = var_pattern.format(name=x_var_name)
        y_var_pattern = var_pattern.format(name=y_var_name)

        x = re.search(x_var_pattern, content)
        y = re.search(y_var_pattern, content)

        if x and y:
            x = json.loads(x.group(2))
            y = json.loads(y.group(2))

            length = min(len(x), len(y))
            x = x[:length]
            y = y[:length]

            name_match = re.search(name_pattern, trace)
            if name_match:
                name = name_match.group(1)
    
    return name, x, y
