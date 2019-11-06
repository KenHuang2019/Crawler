# system
import os
import re
import json
import time
from datetime import datetime

# package
import requests
import pyquery
import urllib.parse as UP
from fake_useragent import UserAgent
import codecs  # deal with parsing

# self defined .py
import proxy

bookList = []
booksData = []


def set_header_user_agent():
    user_agent = UserAgent()
    return user_agent.random


def get(name, url, user_agent):
    proxies = proxy.getListProxy()
    for i in proxies:
        response = requests.get(url, headers={"user-agent": user_agent}, proxies={'https':f'https://{i["ip"]}:{i["port"]}'})
        if reader is None:
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


def getBookList(url):
    user_agent = set_header_user_agent()
    response = get("books", url, user_agent)
    if response is None:
        return print("getBooks Fail")

    # get HTML elements by pyquery
    getElement = pyquery.PyQuery(response.text)
    books = getElement("div.mod_a div.item")

    for book in books.items():
        name = book("h4 a")
        link = name("a").attr("href")
        bookPage = getBookPage(link)
        booksData.append(bookPage)
        listdata = {"bookName": name.text(), "link": link}
        bookList.append(listdata)
        time.sleep(1)
        # break

    return bookList


def getBookPage(url):
    user_agent = set_header_user_agent()
    res = UP.urlparse(url)
    code = os.path.basename(res.path)
    response = get("book", url, user_agent)
    if response is None:
        return print("getBookPage Fail")
    getElement = pyquery.PyQuery(response.text)

    # category (return a list)
    category = getElement("ul.type04_breadcrumb").text().split("\n")[1:]
    # image url
    imageUrl = getElement('img[itemprop="image"]').attr("src")
    imageUrl = f"{res.scheme}:{imageUrl}"
    # book info
    bookData = getElement("div.type02_p01_wrap")
    bookTextData = bookData("div.grid_10")  # get text data
    bookName = bookTextData("div.type02_p002 h1").text()
    bookInfo = bookTextData("div.type02_p003")
    bookAuthor = bookInfo("div.trace_box").next().text()
    publisher = bookTextData('span[itemprop="brand"]').text()
    publishDate = (
        bookTextData('span[itemprop="brand"]').parent().parent().next().text()[5:]
    )
    publishDate = datetime.strptime(
        publishDate, "%Y/%m/%d"
    ).date()  # convert to datetime object
    language = (
        bookTextData('span[itemprop="brand"]')
        .parent()
        .parent()
        .next()
        .next()
        .text()[3:]
    )
    price = getElement("em").eq(0).text()
    content = getElement('div[itemprop="description"]').text()

    return {
        "code": code,
        "category": category,
        "imageUrl": imageUrl,
        "name": bookName,
        "author": bookAuthor,
        "publisher": publisher,
        "publishDate": publishDate,
        "price": price,
        "language": language,
        "content": content,
    }

def getBooksData():
    if booksData != None:
        return booksData
    else:
        return None

if __name__ == "__getBookList__":
    # get all books
    getBookList()
if __name__ == "__getBookPage__":
    getBookPage()
if __name__ == "__getBooksData__":
    getBooksData()
