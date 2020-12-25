# system
import json

# package
import requests
import pyquery
import codecs  # deal with parsing

def getListProxy():
    response = requests.get("https://free-proxy-list.net/")
    if response.status_code != 200:
        print("Proxy page download: failed")
        return
    print("Proxy page download: done")
    # with codecs.open("Proxy.html", "w", "utf-8-sig") as f:
    #         f.write(response.text)

    proxies = []

    d = pyquery.PyQuery(response.text)
    table = d("table#proxylisttable")
    trs = table("tbody > tr")
    for tr in trs.items():
        ip = tr("td:nth-child(1)").text()
        port = tr("td:nth-child(2)").text()
        # print(f"Proxy {ip}:{port}")
        proxies.append({"ip": ip, "port": int(port)})

        # test proxy is activate or not
        # try:
        #     resp = requests.get('https://www.google.com/', proxies={
        #         'https':f'https://{ip}:{port}'
        #     })
        #     print(resp.status_code)
        # except:
        #     pass

        # break
    # print(proxies)
    return proxies

if __name__ == "__main__":
    getListProxy()
    # print(getListProxy())
