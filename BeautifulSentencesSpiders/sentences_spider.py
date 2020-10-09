from Tools import requests_dora
from bs4 import BeautifulSoup
import re
import json
import pyprind
import logging
import os
from multiprocessing import Pool
import default
import time
import random


def get_work_list_page(url, page_ind):
    res = requests_dora.try_best_2_get("{}?page={}".format(url, page_ind), headers=requests_dora.get_default_headers(), timeout = 30,
                                       get_proxies_fun=get_proxies)
    html_str = res.text
    soup = BeautifulSoup(html_str, "lxml")

    page_last = -1
    if page_ind == 0:
        page_list = soup.select("ul.pager li")
        page_last = page_list[-2].get_text() if len(page_list) != 0 else -1

    work_list = []
    div_list = soup.select("div.views-row")
    for div in div_list:
        a = div.select_one("div.views-field-tid a")
        if a is None:
            continue
        url = "https://www.juzimi.com{}".format(a["href"])

        a = div.select_one("a.xqallarticletilelink")
        if a is None:
            continue
        work = a.text
        if work == "":
            work = "unknown"
        work_list.append({
            "url": url,
            "work": work,
        })

    return work_list, int(page_last)


def get_work_list(url):
    work_list_total = []
    work_list, page_last = get_work_list_page(url, 0)
    work_list_total.extend(work_list)
    if page_last != -1:
        print("{} pages".format(page_last))
        for p in pyprind.prog_bar(range(1, page_last)):
            work_list, page_last = get_work_list_page(url, p)
            work_list_total.extend(work_list)

    return work_list_total


def get_sentences_page(url, page_ind):
    headers = requests_dora.get_default_headers()
    random.seed(time.time)
    headers["User-Agent"] = random.shuffle(default.USER_AGENTS)

    res = requests_dora.try_best_2_get("{}?page={}".format(url, page_ind), headers=headers, timeout=20, get_proxies_fun=get_proxies)
    html_str = res.text
    # html_str = re.sub("[\r]+", "", res.text)
    # html_str = re.sub("[(<br/>)]+", "", html_str)

    soup = BeautifulSoup(html_str, "lxml")

    page_last = -1
    if page_ind == 0:
        page_last = soup.select_one("li.pager-last a")
        page_last = int(page_last.get_text())if page_last else -1

    div_list = soup.select("div.view-content div.views-field-phpcode")
    sentence_list = []
    for div in div_list:
        sentence = div.select_one("a.xlistju").get_text()
        from_ = div.select_one("div.xqjulistwafo")

        author = ""
        work = ""
        if from_ is not None:
            author = from_.select_one("a[title*='作者']")

            author = author.get_text() if author else ""

            work = from_.select_one("a[title*='出自']")
            work = work.get_text() if work else ""

        like = div.select_one("a[title*='喜欢本句']")
        like = like.get_text() if like else ""
        se_like = re.search("喜欢\((\d+)\)", like)
        if se_like:
            like = int(se_like.group(1))
        else:
            like = 0

        sentence_list.append({
            "sentence": sentence,
            "work": work,
            "author": author,
            "like": like,
        })
    if len(sentence_list) == 0:
        logging.warning("the len of %s is 0, re-crawling..." % url)
        return get_sentences_page(url, page_ind)
    return sentence_list, page_last


def get_sentences_url(url):
    sentences_list_total = []
    sentences_list, page_last = get_sentences_page(url, 0)
    sentences_list_total.extend(sentences_list)
    if page_last != -1:
        print("{} pages".format(page_last))
        for p in pyprind.prog_bar(range(1, page_last)):
            sentences_list, page_last = get_sentences_page(url, p)
            sentences_list_total.extend(sentences_list)
    return sentences_list_total


def crawl_all_work_url():
    url_start = {
        "book": "https://www.juzimi.com/books",
        "film": "https://www.juzimi.com/allarticle/jingdiantaici",
        "fiction": "https://www.juzimi.com/allarticle/zhaichao",
        "prose": "https://www.juzimi.com/allarticle/sanwen",
        "anime": "https://www.juzimi.com/allarticle/dongmantaici",
        "drama": "https://www.juzimi.com/lianxujutaici",
        "ancient_prose": "https://www.juzimi.com/allarticle/guwen"
    }

    cat_done = []
    for root, dirs, files in os.walk("../Sources/sentences_yield"):
        for file_name in files:
            cat = re.search("(.*).json", file_name).group(1)
            cat_done.append(cat)

    for cat, url in url_start.items():
        if cat in cat_done:
            continue
        url_list = get_work_list(url)
        json.dump(url_list, open("../Sources/sentences_yield/{}.json".format(cat), "w", encoding="utf-8"))


def crawl_all_sentences(work_list_file_path):
    work_done = []
    for root, dirs, files in os.walk("D:\\sentences"):
        for file_name in files:
            work_name = re.search("(.*).json", file_name).group(1)
            work_done.append(work_name)

    count_unkown = 0

    work_list = json.load(open(work_list_file_path, "r", encoding="utf-8"))
    for work in work_list:
        url = work["url"]
        work_name = work["work"]
        work_name = re.sub("/", "_", work_name)

        if work_name in work_done:
            logging.warning("work: {} passed".format(work_name))
            continue

        logging.warning("crawling work: {}".format(work_name))
        sentence_list = get_sentences_url(url)
        if work_name == "unknown":
            work_name = "unknown_{}".format(count_unkown)
            count_unkown += 1

        json.dump(sentence_list, open("D:\\sentences\{}.json".format(work_name), "w", encoding="utf-8"))


def get_proxies():
    # proxy = "lum-customer-hl_95db9f83-zone-static:m6yzbkj85sou@zproxy.lum-superproxy.io:22225"
    res = requests_dora.try_best_2_get("http://api.ip.data5u.com/dynamic/get.html?order=53b3de376027aa3f699dc335d2bc0674&sep=3")
    proxy = res.text.strip()

    if not re.match("\d+\.\d+\.\d+\.\d+:\d+", proxy):
        logging.warning("the proxy expired...")
        raise Exception

    proxies = {
        "http": "http://{}".format(proxy),
        "https": "https://{}".format(proxy),
    }
    time.sleep(1)
    logging.warning("current proxy: {}".format(proxy))
    return proxies


if __name__ == "__main__":
    # crawl_all_work_url()
    job_list = [
        "../Sources/sentences_yield/book.json",
        "../Sources/sentences_yield/anime.json",
        "../Sources/sentences_yield/ancient_prose.json",
        "../Sources/sentences_yield/drama.json",
        "../Sources/sentences_yield/fiction.json",
        "../Sources/sentences_yield/film.json",
        "../Sources/sentences_yield/prose.json",
    ]
    for job in job_list:
        crawl_all_sentences(job)

    # sentences_list = get_sentences_url("https://www.juzimi.com/article/%E5%B9%B3%E5%87%A1%E7%9A%84%E4%B8%96%E7%95%8C") # 反爬虫
    # print(sentences_list)
    # print(len(sentences_list))