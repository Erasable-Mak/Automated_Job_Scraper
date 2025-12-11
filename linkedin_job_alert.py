import os
import time
import json
import random
import schedule
import time
import subprocess
from selenium.webdriver.common.by import By
from airtable import Airtable_Service
from slack_notification import notification
from scrapper_ud import WebScraper
# Initialize Airtable service
# Fetches the Airtable base ID from environment variables
db = Airtable_Service(os.getenv('BASE_ID'))


def login(web_driver: any) -> None:
    web_driver.open_url(url='https://www.linkedin.com/login')
    time.sleep(5)
    find_email=web_driver.find_element_by(find_by="id",what_to_find="username",multi=False)
    find_email.send_keys('userid/email/phone/number')
    time.sleep(5)
    find_password = web_driver.find_element_by(find_by="id", what_to_find="password", multi=False)
    find_password.send_keys('password')
    time.sleep(5)
    sign_btn=web_driver.find_element_by(find_by='class_name',what_to_find='btn__primary--large',multi=False)
    time.sleep(2)
    sign_btn.click()
    time.sleep(30)
    web_driver.get_cookies()
    time.sleep(10)
def login_using_cookies(web_driver:any)->None:
    web_driver.open_url(url='https://www.linkedin.com/login')
    time.sleep(5)
    with open("cookies.json", "r") as file:
        cookies = json.dumps(json.load(file))
    web_driver.load_cookies(cookies=cookies)
    try:
        web_driver.refresh_page()
    except:
        pass
    time.sleep(10)
def get_job(web_driver:any,url:str):
    web_driver.open_url(url=url)

    scroll_=web_driver.find_element_by(find_by='class_name',what_to_find="""IXuQZxiPSpCLmEHAeESZsstyPVZZafqCbcsE
          
          """)
    if scroll_ is None:
        scroll_ = web_driver.find_element_by(find_by='class_name', what_to_find="""JFejZbOQJSnTiDbFsNTjartqbrZdYyaQqPM
          
          """)

    for i in range(2):
        if scroll_:
            web_driver.scroll_by_height(scroll_)
            ramdom_time=random.randint(1,3)
            time.sleep(ramdom_time)
    jobs=web_driver.find_element_by(find_by='css_selector',what_to_find='li.occludable-update',multi=True)
    print("jobs",len(jobs))
    for job in jobs:
        print(job.text)
        try:
            all_al_job = db.get_all_data(os.getenv('TABLE_JOB_LINKEDIN'))
        except:
            continue
        random_number = random.uniform(2.5,4.0)
        time.sleep(random_number)
        try:
            job_id=job.get_attribute('data-occludable-job-id')
        except:
            continue
        # check_job = [cj for cj in all_al_job if cj['fields']['job id'] == str(job_id)]
        check_job = [cj for cj in all_al_job if cj['fields'].get('job id') == str(job_id)]
        try:
            job_title=job.find_element(By.CLASS_NAME,'artdeco-entity-lockup__title')
            company=job.find_element(By.CLASS_NAME,'artdeco-entity-lockup__subtitle')
            job_time=job.find_element(By.CLASS_NAME,'job-card-container__footer-item')
            if "Turing" in company.text:
                continue
            jon_href=job_title.find_element(By.TAG_NAME,'a')
            job_url = jon_href.get_attribute('href')
            if len(check_job) > 0:
                continue
            print(job_id)
            jt=job_title.text
            jt=jt.lower()
            if "intern" in jt:
                continue
            if "web" in jt or "backend" in jt or "python" in jt or "django" in jt or "mern" in jt or "react" in jt or "full" in jt or "javascript" in jt or "freel" in jt or "cloud" in jt or "dev" in jt:
                pass
            else:
                continue
            # Format the Slack notification message
            msg = [
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"***{job_title.text}***\n\n{company.text}\n\n{job_time.text}\n\n{job_url}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View",
                            "emoji": True
                        },
                        "value": job_url,
                        "url": job_url,
                        "action_id": "button-action"
                    }
                },
                {"type": "divider"},
            ]

            # Send the notification to Slack
            notification(channel_id="channel_id", message=msg)

            # Add the job record to Airtable
            result = db.add_record(os.getenv('TABLE_JOB_LINKEDIN'), data={
                "job id": str(job_id),
                "title": job_title.text,
                "url":job_url
            })
            print("Airtable add_record result:", result)

        except Exception as e:
            pass
            break
    # web_driver.close_driver()
def main():
    web_driver = WebScraper()
    web_driver.setup_driver()  # Set up the web driver
    # login(web_driver=web_driver) # comment this line if you have cookies saved
    login_using_cookies(web_driver=web_driver)
    while True:
        try:
            get_job(web_driver=web_driver,
                    url='https://www.linkedin.com/jobs/search/?&distance=25&f_AL=true&f_TPR=r86400&geoId=102713980&keywords=python&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=DD')
        except Exception as e:
            print("error aa gya hai ->",e)
            web_driver.close_driver()
            break
    main()


if __name__ == "__main__":
    # web_driver = WebScraper()
    # web_driver.setup_driver()  # Set up the web driver
    # login(web_driver=web_driver)
    #Schedule the script to run every 3 minutes

    try:
        main()
        schedule.every(2).minutes.do(main)
        while True:
            try:
                schedule.run_pending()
                time.sleep(2)  # Sleep for a second to prevent high CPU usage
            except Exception as e:
                print("error aa gya hai loop->",e)
    except Exception as e:
        print("error aa gya hai ->",e)

