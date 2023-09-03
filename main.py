from multiprocessing.connection import wait
from weakref import proxy
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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

thread_counter = 0
counter_lock = multiprocessing.Lock()
def run():
    driver = create_drivers(1)
    driver_job(*driver)
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


def driver_job(driver):
    print(driver)
    global counter_lock
    global thread_counter
    with counter_lock:
        thread_counter += 1
        thread_num = thread_counter
        print(f"{thread_num} process is running...")
    url = "https://www.livescore.in/ru/"

    driver.implicitly_wait(20)
    driver.get(url)
    # time.sleep(2)
    driver.find_element(By.XPATH,"//div[contains(text(),'LIVE')]").click()
    # time.sleep(1)

    driver.execute_script('window.scrollTo({left:0,top:document.body.scrollHeight,behavior:"smooth"})')
    # time.sleep(2)
    matches = driver.find_elements(By.CLASS_NAME,"event__match--live")

    div = len(matches) // CONNECTIONS
    mod = len(matches) % CONNECTIONS
    start = (thread_num-1)*div
    end = start + div
    if thread_num <= mod:
        end+=1
    else:
        start+=mod

    for i in range(start, end):
        print(f"{thread_num} process running {i} match...")
        matches[i].click()
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        # duelParticipant = driver.find_element(By.CLASS_NAME,"duelParticipant")
        # print(duelParticipant.text)
        print("--------------------------------")
        odds = driver.find_element(By.CLASS_NAME,"oddsRow").find_elements(By.CLASS_NAME,"oddsValueInner")
        left,draw,right = odds if odds else (None,None,None)
        if left and draw and right:
            print(f"left - {left.text}\nright - {right.text}\ndraw - {draw.text}")
        print("--------------------------------")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.quit()
def main():
    res = None
    drivers = create_drivers(CONNECTIONS)
    try:
        with pool.ProcessPoolExecutor(max_workers=CONNECTIONS) as executer:
            for i in range(CONNECTIONS):
                executer.submit(run)

            # futures = [executer.submit(run, driver) for driver in drivers]

            # for future in pool.as_completed(futures):
            #     result = future.result()
            #     # Обработка результата
    except Exception as e:
        print("Произошла ошибка:", str(e))




if __name__ == "__main__":
    main()