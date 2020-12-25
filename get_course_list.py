# cd C:\Users\fken2\Desktop\lu\opencourse_platform\course_info
# system
import os
import re
import csv
import json
import time
import argparse
from datetime import datetime

# package
import requests
import pyquery
import urllib.parse as UP
from fake_useragent import UserAgent
import codecs  # deal with parsing

from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# self defined .py
import proxy

URLS = {
    "ntu": "http://ocw.aca.ntu.edu.tw/ntu-ocw/ocw/coupage/1", # 最後一個數字是頁碼
    "ntust": "http://ocw.ntust.edu.tw/index.php/frontend/show/lessons",
    "ntnu": "http://ocw.lib.ntnu.edu.tw/course/index.php"
}

courseList = []
courseData = {}

def getResponse(name, url, user_agent):
    proxies = proxy.getListProxy()
    for i in proxies:
        print(i)
        response = requests.get(url, headers={
                                "user-agent": user_agent}, proxies={'https': f'https://{i["ip"]}:{i["port"]}'})
        if i is None:
            print("proxy is invalid")
            continue
        print("proxy is valid")
        time.sleep(1)
        break
    if response.status_code != 200:
        print(f"{name} page download: fail")
        return None
    print(f"{name} page download: done")
    time.sleep(1)
    return response

def getNtuOnePageCourseList(url, courseCounter, school):
    """
    爬取 NTU 課程列表
    """
    response = getResponse("course_list", url, UserAgent().random)
    if response is None:
        return print("getCourseList Fail")

    # get HTML elements by pyquery
    getElement = pyquery.PyQuery(response.text)

    courses = getElement("div.coursebox")

    for c in courses.items():
        courseCounter += 1
        print("Course No.", courseCounter, ": ")

        courseText = c("div.coursetext")

        # 英文標題有特殊 class
        courseTitle = courseText("div.coursetitle a").text()
        if courseTitle == '':
            courseTitle = courseText("div.eng-coursetitle a").text()

        listData = {
            "id": courseCounter,
            "title": courseTitle,
            "intro": courseText("div.introtext").text(),
            "teacher": courseText("div.teacher").text(),
            "img_link": c("div.coursepic a img").attr("src"),
            "link": courseText("a").attr("href"),
            "school": school
        }
        print(listData)

        courseList.append(listData)
        print("--------------------------------------------")
        # break

    return courseCounter

def getNtuLastPageNum(url):
    """
    取得最後一頁的頁碼
    """
    response = getResponse("course_list", url, UserAgent().random)

    if response is None:
        return print("getCourseList Fail")

    getElement = pyquery.PyQuery(response.text)

    return int(getElement("ul.pagecount li:last-child a").attr("href").split('/')[-1])

def getNtustCourseListHTML(url):
    """
    使用 selenium 模仿點擊網頁行為
    載入 AJAX 回傳結果後
    把 HTML 丟給 pyquery 擷取所需資訊
    """
    html_tmp = []

    options = Options()
    options.add_argument("--disable-infobars") # remove the warning msg bar
    options.add_argument("--kiosk") # fullscreen and disable right click
    driver = Chrome(chrome_options=options, executable_path='./chromedriver.exe')
    driver.get(url)

    while True:
        list_long = driver.find_element_by_css_selector("div#list_long")
        course_list = list_long.get_attribute('innerHTML')
        
        if len(html_tmp) == 0 or course_list != html_tmp[-1]: # 確保有走到最後一頁
            html_tmp.append(course_list)
        else:
            break

        driver.find_element_by_css_selector("a#pic_next").click()

        time.sleep(1)

    driver.close()
    driver.quit()
    
    return html_tmp

def getNtustCourseList(url, courseCounter, school):
    """
    爬取 NTUST 課程列表
    """
    print("\n=== Current target: ", url, "\n")

    pages = getNtustCourseListHTML(url) # 用 list 裝 每一頁 AJAX 抽換的 HTML

    # 讀取每個頁面的 HTML
    for p in pages:
        getElement = pyquery.PyQuery(p)

        # 讀取每堂課相關資訊
        for c in getElement("dd a").items():
            courseCounter += 1
            print("Course No.", courseCounter, ": ")

            courseText = c("ul")

            listData = {
                "id": courseCounter,
                "title": courseText("li:nth-child(1) span").text(),
                "intro": None,
                "teacher": courseText("li:nth-child(2) span").text(),
                "img_link": c("img").attr("src"),
                "link": c("a").attr("href"),
                "school": school
            }
            print(listData)

            courseList.append(listData)
            print("--------------------------------------------")

    return courseCounter

def getNtnuOnePageCourseList(url, courseCounter, school):
    response = getResponse("course_categories_list", url, UserAgent().random)
    if response is None:
        return print("getCourseList Fail")

    # get HTML elements by pyquery
    getElement = pyquery.PyQuery(response.text)
    
    for courseBox in getElement('div.coursebox').items():
        courseCounter += 1
        print("Course No.", courseCounter, ": ")

        # 利用圖示多寡 ( 多一個 anchor ) 判斷該堂課是否需要密碼
        if courseBox('div.name a').size() > 2: 
            print("This course need password, skip this.")
            courseCounter -= 1
            continue

        title_anchor = courseBox('div.name a:last-child')

        title = title_anchor.text()

        # 確認是否有教師名稱
        if '/' in title:
            title_seg = title.split('/')
            title = title_seg[0]
            teacher = title_seg[1]
        else:
            teacher = None 

        listData = {
            "id": courseCounter,
            "title": title,
            "intro": None,
            "teacher": teacher,
            "img_link": None,
            "link": title_anchor.attr("href"),
            "school": school
        }
        print(listData)

        courseList.append(listData)
        print("--------------------------------------------")

    return courseCounter

def getNtnuCourseList(url, courseCounter, school):
    """
    爬取 NTNU 課程列表
    """
    response = getResponse("course_categories_list", url, UserAgent().random)
    if response is None:
        return print("getCourseList Fail")

    # get HTML elements by pyquery
    getElement = pyquery.PyQuery(response.text)
    counter = 0

    for category in getElement("table.categorylist").items():
        counter += 1
        category_url = category('a').attr("href")
        print("\n=== Current target: ", category_url, "\n")
        courseCounter = getNtnuOnePageCourseList(category_url, courseCounter, school)
        time.sleep(1)

    return courseCounter

def list2csv(courseList, fileName):
    """
    將蒐集來的課程列表資訊寫成 csv
    """
    keys = courseList[0].keys()
    with open('./csv/'+fileName + '.csv', 'w', newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        # dict_writer.writeheader()
        dict_writer.writerows(courseList)

def argIncorrect():
    """
    arg pass 輸入值錯誤回報
    """
    print("Incorrect args, please check -s arg value (should be one of these: 'ntu', 'ntust', 'ntnu')")

def getNtuCourseList(url, courseCounter, school):
    """
    取得所有 NTU 課程列表
    """
    for n in range(getNtuLastPageNum(url)):
        tmp_url = url[:-1] + str(n+1)
        print("\n=== Current target: ", tmp_url, "\n")
        courseCounter = getNtuOnePageCourseList(tmp_url, courseCounter, school)
        time.sleep(2)
    
    return courseCounter

def writeCsv(courseList, school):
    """
    docstring
    """
    # 確認是否有撈到課程列表
    if len(courseList) > 0:
        list2csv(courseList, school + "_course_list")
    else:
        print('courseList incorrect')

def main():
    """
    取得各校開放式課程連結
    1. 課程名稱、描述、教師名稱、縮圖
    2. 每堂課的各單元影片連結
    """
    # 設定 arg pass 讓使用者決定是否要繪圖
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", required=False, default=None)
    args = parser.parse_args()
    school = args.school.lower()

    courseCounter = 0

    if school in URLS: 
        url = URLS[school]

        print("=== School: ", school, "\n")

        if school == 'ntu':
            getNtuCourseList(url, courseCounter, school)
        if school == 'ntust':
            getNtustCourseList(url, courseCounter, school)
        if school == 'ntnu':
            getNtnuCourseList(url, courseCounter, school)
        
        writeCsv(courseList, school)

    elif school == 'all':
        
        # 每個學校都做一次爬取，這樣id才能符合DB需求
        for s in URLS:
            url = URLS[s]
            if s == 'ntu':
                courseCounter = getNtuCourseList(url, courseCounter, s)
            if s == 'ntust':
                courseCounter = getNtustCourseList(url, courseCounter, s)
            if s == 'ntnu':
                courseCounter = getNtnuCourseList(url, courseCounter, s)

        writeCsv(courseList, school)
    else:
        argIncorrect()

if __name__ == "__main__":
    main()
