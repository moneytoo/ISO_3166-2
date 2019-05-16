from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path

from bs4 import BeautifulSoup
import csv
import json


def save(country_code):
    driver = webdriver.Chrome()
    url = "https://www.iso.org/obp/ui/#iso:code:3166:" + country_code
    driver.get(url)

    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "country-subdivisions"))
        )

    inner_html = driver.execute_script("return document.body.innerHTML")
    print(inner_html)

    Path('tmp/' + country_code).write_text(inner_html, encoding='utf-8')

    driver.quit()


def write_row(row, tag, writer, prepend_col=None):
    cols = row.find_all(tag)
    cols_text = []

    for col in cols:
        text = col.text

        if text.endswith('*'):
            text = text[:-1]

        if ' (see also ' in text:
            index = text.index(' (see also ')
            text = text[:index]

        cols_text.append(text)

    if cols_text:
        if prepend_col:
            cols_text = [prepend_col] + cols_text
        writer.writerow(cols_text)


def countries():
    # Top level JSON
    # https://www.iso.org/obp/ui/UIDL/?v-uiId=0

    country_codes = []
    uidl = Path('uidl.json').read_text(encoding='utf-8')
    data = json.loads(uidl)
    lst = data[0]['changes'][11][2][2]

    for item in lst:
        if isinstance(item, list):
            country_codes.append(item[4])

    return country_codes


def country_rows(country_code):
    html = Path('tmp/' + country_code).read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', attrs={'id': 'subdivision'})
    return table.find_all('tr')


def create_csv(country_code, write_header=True):
    rows = country_rows(country_code)

    if len(rows) > 1:
        with open('out/' + country_code + '.csv', 'w', newline='', encoding='utf-8-sig') as csv_out:
            csv_writer = csv.writer(csv_out)

            for row in rows:
                if write_header:
                    write_row(row, 'th', csv_writer, prepend_col='3166-1 Alpha-2 code')
                write_row(row, 'td', csv_writer, country_code)


def create_csv_all():
    with open('iso_3166-2.csv', 'w', newline='', encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out)
        header_written = False

        for country_code in countries():
            rows = country_rows(country_code)
            for row in rows:
                if not header_written:
                    write_row(row, 'th', csv_writer, prepend_col='3166-1 Alpha-2 code')
                write_row(row, 'td', csv_writer, country_code)
            header_written = True


# for country in countries():
#     create_csv(country, write_header=True)

create_csv_all()

