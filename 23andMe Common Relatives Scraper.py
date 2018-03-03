from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import csv


def pull_data_from_23andme_row(row_soup):
    common_relative_soup = row_soup.find('td')
    common_relative_id = common_relative_soup.find('a').get('href')[32:96]
    common_relative = common_relative_soup.find('strong').get_text().strip()

    your_pct_soup = common_relative_soup.find_next_sibling('td')
    your_pct = your_pct_soup.find('span', class_='hide-for-mobile').get_text()

    their_pct_soup = your_pct_soup.find_next_sibling('td')
    their_pct = their_pct_soup.find('span', class_='hide-for-mobile').get_text()

    return [common_relative_id, common_relative, your_pct, their_pct]


print('For this to work properly, the script needs to know how to log into your account')
email = input('Please enter your email address: ')
password = input('Please enter your password: ')

print('You said your email was {} and your password was {}'.format(email, password))
if input('Is this correct? (Y/n) ') != 'Y':
    print('Sorry, please re-run the script')
    exit()

print('Now, we need to know where your 23andMe DNA Relatives aggregate data is saved')
print('This csv should be unchanged from the download')
file_of_ids = input('Please enter the full path of your DNA Relatives aggregate data, WITHOUT quotation marks: ')

with open(file_of_ids) as f:
    link_reader = csv.reader(f, delimiter=',', quotechar='"')

    relative_ids = {row[8][59:]: row[0] for row in link_reader if row[0] != 'Display Name'}
    f.close()

print(relative_ids)

if input('File has {} unique IDs, continue? (Y/n) '.format(len(relative_ids))) != "Y":
    exit()

output_table = [['Relative ID', 'Relative Name', 'Common Relative ID', 'Common Relative Name', 'Your % w/ Common',
                 'Their % w/ common']]

base_url = r'https://you.23andme.com/url/tools:compare_match/?remote_id={}'

driver = webdriver.Firefox()
for relative_id in relative_ids:
    driver.get(base_url.format(relative_id))

    # Check if we need to sign in'
    if 'Sign in' in driver.title:
        email_input = driver.find_element_by_id('email')
        email_input.send_keys(email)
        password_input = driver.find_element_by_id('password')
        password_input.send_keys(password)
        password_input.submit()
    try:
        waitingtime = WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.CLASS_NAME, 'js-relatives-in-common-table')))
    except:  # Page didn't open in time/load our table, let's skip it
        print('Timed out while opening {}'.format(base_url.format(relative_id)))
        continue

    current_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

    relative_name = current_page_soup.find(class_= 'name')
    relative_name = relative_name.find('h1').text
    print('Pulling data for {}...'.format(relative_name))
    try:
        current_page = int(current_page_soup.find(class_= 'current-page').get_text().strip())
        # print(current_page)
        current_page_soup.find_previous_sibling()
        try:
            max_page = int(current_page_soup.find(class_= 'ellipses').find_next_sibling('span').get_text())
            print('{} pages of data to pull...'.format(max_page))
        except:
            print('Fewer than 5 pages, I hope this works!')
            max_page = 5
        # print(max_page)

        while current_page <= max_page:
            # print('Pulling page {}'.format(current_page))
            relatives_table = current_page_soup.find(class_= 'js-relatives-in-common-table')
            for row in relatives_table.find_all('tr'):
                if row.find('td') and row.has_attr('class') and 'loading-row' not in row.get('class'):
                    curr_common_relative = [relative_id, relative_name]
                    curr_common_relative.extend(pull_data_from_23andme_row(row))
                    output_table.append(curr_common_relative)
            else:
                # time to load the next page
                try:
                    driver.find_element_by_xpath("//span[contains(@class,'current-page')]/following-sibling::span").click()
                    waitingtime = WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.CLASS_NAME, 'js-relative-row')))
                    current_page_soup = BeautifulSoup(driver.page_source, 'html.parser')
                except:
                    current_page = max_page
                current_page = current_page + 1
    except:
        print('Error pulling data for {}, moving to next'.format(relative_name))
        output_table.append([relative_id, relative_name, '!ERROR!', '!ERROR!', '!ERROR!', '!ERROR!'])

# print(output_table)

with open("Common Relatives per Relative.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerows(row for row in output_table if row)
