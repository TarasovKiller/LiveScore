from multiprocessing.connection import wait
from weakref import proxy
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
import json
import pickle
import re
import undetected_chromedriver as uc
from proxy_set import *
import threading
from bs4 import BeautifulSoup
import concurrent.futures as pool
import multiprocessing, time

CONNECTIONS = 3
PROCESS_NUMBER = 0

counter_lock = multiprocessing.Lock()
def run(process_num,urls):
    global PROCESS_NUMBER
    print(len(urls))
    PROCESS_NUMBER = process_num
    print(f"{process_num} is staring...")
    driver = create_drivers(1)[0]
    driver.implicitly_wait(10)

    div = len(urls) // CONNECTIONS
    mod = len(urls) % CONNECTIONS
    start = (process_num-1)*div
    end = start + div
    if process_num <= mod:
        end+=1
    else:
        start+=mod

    for i in range(start, end):
        url = urls[i]
        print(f"{process_num} is processing {i} match ({url})...")
        try:
            get_summary(driver,url)
        except Exception as e:
            print(e)


def create_drivers(n):
    drivers = []
    for i in range(n):
        service = Service(executable_path='./chromedriver.exe')
        options = webdriver.ChromeOptions()


        # proxy.add_to_capabilities(capabilities)


        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

        # driver = uc.Chrome(service=service,options=options)
        driver = get_chromedriver(use_proxy=True)
        drivers.append(driver)
    return drivers

def get_summary(driver,url):


    driver.get(url)
    time.sleep(2)

    print("--------------------------------")
    odds = driver.find_element(By.CLASS_NAME,"oddsRow").find_elements(By.CLASS_NAME,"oddsValueInner")
    left,draw,right = odds if odds else (None,None,None)
    if left and draw and right:
        print(f"left - {left.text}\nright - {right.text}\ndraw - {draw.text}")
    print("--------------------------------")


def get_urls():
    driver = create_drivers(1)[0]
    main_url = "https://www.livescore.in/ru/"

    driver.implicitly_wait(20)
    driver.get(main_url)
    time.sleep(2)
    try:
        matches = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "event__match"))
        )
    except Exception as e:
        print("Too long for finding matches")
        driver.quit()
    # driver.find_element(By.XPATH,"//div[contains(text(),'LIVE')]").click()
    time.sleep(2)

    # driver.execute_script('window.scrollTo({left:0,top:document.body.scrollHeight-100,behavior:"smooth"})')
    time.sleep(2)
    # matches = wait.until(EC.elements_to_be_clickable(By.CLASS_NAME,"event__match--live"))
    try:
        matches = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "event__match"))
        )
    except Exception as e:
        print("Too long for finding matches")
        driver.quit()


    matches = driver.find_elements(By.CLASS_NAME,"event__match")
    urls = ["https://www.livescore.in/ru/match/"+
            re.sub(r"g_\d_","",match.get_attribute("id"))+
            "/#/match-summary" for match in matches]
    return urls



def main():
    urls = get_urls()
    print(len)
    numbers = []
    try:
        with pool.ProcessPoolExecutor(max_workers=CONNECTIONS) as executer:
            wait_complete = []
            for i in range(CONNECTIONS):
                future = executer.submit(run, *(i+1,urls))
                wait_complete.append(future)
        for res in pool.as_completed(wait_complete):

            print(f':=> {res.result()}')

    except Exception as e:
        print("Произошла ошибка:", str(e))


if __name__ == "__main__":
    main()