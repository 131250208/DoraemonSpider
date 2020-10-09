import re
import time
from bs4 import BeautifulSoup
import settings


def get_proxies_fr_gatherproxy(country, proxies, filer=None, uptime=None, page_ind=1):
    url = "http://www.gatherproxy.com/zh/proxylist/country/?c={}&Country={}&PageIdx={}".format(country, country, page_ind)
    if filer is not None:
        url += "&Filter={}".format(filer)
    if uptime is not None:
        url += "&Uptime={}".format(uptime)

    headers = requests_dora.get_default_headers()
    headers["Referer"] = "http://www.gatherproxy.com/zh/proxylist/country/?c=United%20States"
    headers["Host"] = "www.gatherproxy.com"
    headers["Origin"] = "http://www.gatherproxy.com"
    headers["Cookie"] = "_lang=zh-CN; _ga=GA1.2.131823174.1544890597; _gid=GA1.2.1869641062.1544890597; ASP.NET_SessionId=tezxx4qxdulohigvhwhhvepa; _gat=1"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    headers["Upgrade-Insecure-Requests"] = "1"

    res = requests_dora.try_best_2_post(url, headers=headers, proxies=proxies)

    if res is not None:
        soup = BeautifulSoup(res.text, "lxml")
        tr_list = soup.select("table#tblproxy tr")
        a_list = soup.select("div.pagenavi a")
        page_navi_max = a_list[-1].text

        data = {
            settings.KEY_PAGE_NAVI_MAX: int(page_navi_max)
        }
        proxy_list = []

        for tr in tr_list[2:]:

            td_list = tr.select("td")
            usability_split = td_list[6].text.split("/")
            usability = 1 - int(usability_split[1]) / int(usability_split[0])
            if uptime is not None and usability < uptime / 100:
                continue

            last_updated = td_list[0].text
            se_min = re.search("(\d+)m", last_updated)
            last_updated_min = int(se_min.group(1)) if se_min is not None else 0
            se_sec = re.search("(\d+)s", last_updated)
            last_updated_sec = int(se_sec.group(1)) if se_sec is not None else 0

            port = re.search("gp\.dep\('(.*?)'\)", td_list[2].text).group(1)
            port = int(port, 16)
            proxy_list.append({
                "ip": re.search("(\d+\.\d+\.\d+\.\d)", td_list[1].text).group(1),
                "port": str(port),
                "type": td_list[3].text,
                "last_updated": last_updated_min * 60 + last_updated_sec,
                "country": td_list[4].text,
                "usability": usability,
                "delay": re.search("(\d+)", td_list[7].text).group(1)
            })

        data[settings.KEY_PROXY_LIST] = proxy_list
        return data


def geolocate_proxy(proxy):
    url_lum = 'http://lumtest.com/myip.json'
    proxies = {
        "https": "https://{}".format(proxy),
        "http": "http://{}".format(proxy),
    }
    res = requests_dora.try_best_2_get(url_lum, max_times=0, timeout=30, proxies=proxies)
    if res is None:
        return

    print(res.text)
    return res

if __name__ == "__main__":
    from Tools import requests_dora
    # country = ['China', 'Indonesia', 'United%20States', 'Russia', 'Thailand', 'India', 'Taiwan', 'Japan', 'France', 'Iran', 'Bangladesh', 'Poland', 'Romania', 'Venezuela', 'Germany', 'Ukraine', 'Argentina', 'Mexico', 'Australia', 'Colombia']
    # for con in country:
    proxy = "127.0.0.1:1080"
    proxies = {
        "https": "https://{}".format(proxy),
        "http": "http://{}".format(proxy),
    }

    data = get_proxies_fr_gatherproxy("United States", proxies, settings.PROXIES_FILTER_NOT_TRANS, 1, 90)
    proxy_list = data[settings.KEY_PROXY_LIST]
    page_navi_max = data[settings.KEY_PAGE_NAVI_MAX]

    count_suc = 0
    ind = 0
    for pro in proxy_list:
        res = geolocate_proxy("{}:{}".format(pro["ip"], pro["port"]))
        ind += 1
        if res is not None and res.status_code == 200:
            count_suc += 1
        print("-----{}/{}-----".format(count_suc, ind))

    for i in range(page_navi_max):
        page_ind = i + 1
        if page_ind == 1:
            continue
        proxy_list = get_proxies_fr_gatherproxy("United States", proxies, settings.PROXIES_FILTER_NOT_TRANS, page_ind, 90)
        for proxy in proxy_list:
            res = geolocate_proxy("{}:{}".format(pro["ip"], pro["port"]))
            ind += 1
            if res is not None and res.status_code == 200:
                count_suc += 1
            print("-----{}/{}-----".format(count_suc, ind))
    # geolocate_proxy("67.133.86.33:57132")
