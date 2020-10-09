# -*- coding:utf-8 -*-

# 这个类用来爬取链接里所有的论文标题、作者、所属会议等信息

import requests
from bs4 import BeautifulSoup
import re
import xlsxwriter
import random
from PapersCrawler import settings
from PapersCrawler import papers_db_connector
import logging
import time
import json
from PapersCrawler import log
import pyprind

class PaperCrawler2:

    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    ]

    def __init__(self):
        self.log = log.Logger('paper_crawler.log', logging.DEBUG, logging.DEBUG)

    def get_headers(self):
        time_current = time.time()
        random.seed(time_current)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'dblp-view=y; dblp-search-mode=c',
            'Host': 'dblp.uni-trier.de',
            'Referer': 'http://dblp.uni-trier.de/db/conf/ccs/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(self.USER_AGENTS),
        }
        return headers

    # 获取一个会议或者期刊里的所有年份的链接
    def get_issues(self, url, start_year=-1):
        '''
        get conference or journal urls of every issue for every year
        :param url: url of target conference or journal
        :return: link objects including published year, , url
        '''
        while True:
            try:
                res = requests.get(url, headers=self.get_headers(), timeout=20)
                break
            except Exception as e:
                self.log.error("%s Exc..., try again after 10s" % url)
                self.log.error(e)
                time.sleep(10)

        if res.status_code != 200:
            self.log.error("failed crawling {}, status: {}".format(url, res.status_code))
            raise Exception

        soup = BeautifulSoup(res.text, "lxml")
        links = []

        div = soup.find("div", id="breadcrumbs")
        if div is None:
            self.log.war("%s 找不到breadcrumbs" % url)
            return []
        # 先从导航判断是会议还是期刊
        if div.find_all("span", itemprop="name")[-1].text == "Journals": # 期刊
            journal_hl = soup.find("header", class_="headline noline").find("h1").text

            for li in soup.select("div#main > ul > li"):
                try:
                    a_list = li.select("a")
                    if a_list is None or len(a_list) == 0: continue

                    volume = li.text
                    m = re.match(r".*([0-9]{4}).*", li.text)
                    year = m.group(1)

                    for a in a_list:
                        if int(year) >= start_year:
                            link = {"year": year, "published_in": journal_hl + ", " + volume, "url": a["href"]}
                            links.append(link)

                except Exception as e:
                    print("%s get_issues error..." % url)
                    print(e)

        else: # 会议的爬取逻辑
            for ul in soup.select("div#main > ul.publ-list"):
                h = ul.find_previous("header")
                published_in = h.text

                for li in ul.find_all("li", class_ = "editor"):
                    a = li.find("div", class_="data").find("a", text=re.compile("contents"))
                    year = li.select("div.data > span[itemprop='datePublished']")[0].text

                    if int(year) >= start_year and a:
                        link = {"year": year, "published_in": published_in, "url": a["href"]} # published_in: which issue
                        links.append(link)

        return links

    # 获取一个链接里所有的paper 的 title, authors 等信息
    def get_papers(self, url): # e.g. http://dblp.uni-trier.de/db/conf/ccs/ccs2017.html

        while True:
            try:
                res = requests.get(url, headers=self.get_headers(), timeout=20)
                break
            except Exception as e:
                self.log.error("%s Exc..., try again after 10s" % url)
                self.log.error(e)
                time.sleep(10)
        if res.status_code != 200:
            self.log.error("failed crawling {}, status: {}".format(url, res.status_code))
            raise Exception

        bs = BeautifulSoup(res.text, "lxml")
        list_heads = bs.find_all("header")
        papers = []

        # 先从导航判断是会议还是期刊的链接，来决定li的class
        class_li = "article" # 期刊里是用article来选择
        if bs.find("div", id="breadcrumbs").find_all("span", itemprop="name")[1].text != "Journals":  # 期刊
            class_li = "inproceedings"

        if len(list_heads) <= 1: # 如果是没有分类标题的情况（只有总标题
            ul = bs.find("ul", class_="publ-list")
            if ul is None:
                self.log.war("%s has no publ-list" % url)
                return []

            for li in ul.find_all("li", class_= class_li):
                div_data = li.find("div", class_="data")
                list_spans_authors = div_data.find_all("span", itemprop = "author")
                list_authors = [x.text for x in list_spans_authors]

                title = div_data.find("span", class_ = "title").text
                paper = {"category": u"未分类", "authors": list_authors, "title": title}
                papers.append(paper)

        # 有标题的情况
        for ul in bs.select("div#main > ul.publ-list"):
            category = ul.find_previous("header").text # 找到前面最近的一个标题
            for li in ul.find_all("li", class_= class_li):
                div_data = li.find("div", class_="data")
                list_spans_authors = div_data.find_all("span", itemprop = "author")
                list_authors = [x.text for x in list_spans_authors]

                title = div_data.find("span", class_ = "title").text
                paper = {"category": category, "authors": list_authors, "title": title}
                papers.append(paper)

        return papers

    def ouput_rows(self, url_conf_jour, c_j, c_j_name, level, cat, keyWords = None, start_year=-1): # e.g. http://dblp.uni-trier.de/db/conf/ccs/ # 是期刊还是会议，名称， 等级
        '''
        get all papers and its relevant info
        :param url_conf_jour:
        :param c_j: conference or journal
        :param c_j_name: name of the conference or journal
        :param level: CCF recommendation level
        :param cat: domain
        :param keyWords: kw for filtering
        :return: a list of paper object
        '''
        links = self.get_issues(url_conf_jour, start_year=start_year)
        rows = []
        for l in links:
            year = l["year"]
            published_in = l["published_in"]
            published_in = re.sub("[\n\r]", "", published_in)
            url = l["url"]
            papers = self.get_papers(url)
            print("pages: {}".format(len(papers)))
            for p in pyprind.prog_bar(papers):
                category = p["category"]
                authors = ",".join(p["authors"])
                title = p["title"]

                # print("crawling: %s, %s, %s, %s, %s" % (title, authors, category, year, published_in))
                print("crawling %s: %d" % (url_conf_jour, len(rows)))

                if keyWords is not None: # 如果有指定过滤的关键词的话
                    for kw in keyWords:
                        if kw.lower() in title.lower():
                            rows.append({"title": title, "authors": authors, "category": category, "year": year,
                                         "published_in": published_in, "conf_journal": c_j, "name": c_j_name, "level": level, "cat": cat})
                            break
                else:
                    rows.append({"title": title, "authors": authors, "category": category, "year": year,
                                 "published_in": published_in, "conf_journal": c_j, "name": c_j_name, "level": level, "cat": cat})
        return rows

    # 将一个rows写进一个excel文件里的一张sheet
    def write_sheet(self, wb, sheet_name, rows):
        sheet = wb.add_worksheet(sheet_name)
        format1 = wb.add_format()
        format1.set_text_wrap()

        sheet.set_column("A:A", 80)
        sheet.set_column("B:B", 40)
        sheet.set_column("C:C", 25)

        sheet.set_column("D:D", 8)

        sheet.set_column("E:E", 35)

        sheet.set_column("F:F", 25)
        sheet.set_column("G:G", 25)
        sheet.set_column("H:H", 25)
        sheet.set_column("I:I", 50)

        sheet.write(0, 0, u'标题')
        sheet.write(0, 1, u'作者')
        sheet.write(0, 2, u'分类')
        sheet.write(0, 3, u'年份')
        sheet.write(0, 4, u'发表在')
        sheet.write(0, 5, u'期刊或会议')
        sheet.write(0, 6, u'名称')
        sheet.write(0, 7, u'等级')
        sheet.write(0, 8, u'所属')

        for ind, row in enumerate(rows):
            sheet.write(ind + 1, 0, row["title"], format1)
            sheet.write(ind + 1, 1, row["authors"], format1)
            sheet.write(ind + 1, 2, row["category"], format1)
            sheet.write(ind + 1, 3, row["year"], format1)
            sheet.write(ind + 1, 4, row["publish_in"], format1)
            sheet.write(ind + 1, 5, row["conf_journal"], format1)
            sheet.write(ind + 1, 6, row["name"], format1)
            sheet.write(ind + 1, 7, row["level"], format1)
            sheet.write(ind + 1, 8, row["cat"], format1)

    # 将多个链接爬取的内容存进excel文件
    def output_file(self, kw_list, list_url_dict, sv_path):
        wb = xlsxwriter.Workbook(sv_path)

        for u in list_url_dict:
            url= u["url"]
            match_ob = re.match("http://dblp.uni-trier.de/db/(.*)/(.*)/.*", url)
            c_j = match_ob.group(1)
            c_j_name = match_ob.group(2)
            level = u["level"]
            cat = u["cat"]

            rows = self.ouput_rows(url, c_j, c_j_name, level, cat, keyWords=kw_list)
            if len(rows) != 0:
                print("url %s output: %d" % (url, len(rows)))
                sheet_name = c_j_name
                self.write_sheet(wb, sheet_name, rows)
        wb.close()

    def save_rows(self, rows):
        db = papers_db_connector.PapersDB()

        r_len = len(rows)
        if r_len != 0:
            count_suc = 0
            for ind, row in enumerate(rows):

                res, msg = db.insert_paper(row)

                if res:
                    count_suc += 1
                    print("共%d 条结果， 插入row[%d] 完毕\n %s 插入结果: %s" % (r_len, ind, row["title"], msg))
                else:
                    self.log.war("共%d 条结果， 插入row[%d] 完毕\n %s 插入结果: %s" % (r_len, ind, row["title"], msg))

                if (ind + 1) == r_len:
                    self.log.info("共%d 条结果处理完毕, 成功插入： %d, 失败： %d" % (r_len, count_suc, r_len - count_suc))

        db.close()

    def save_json(self, list_cj, filename, start_year):
        rows_total = [] # for results
        cjname_over = [] # for info

        bar = pyprind.ProgBar(len(list_cj), title="crawling conf and jour urls in the list...")
        for ind, u in enumerate(list_cj):
            url = u["url"]
            match_ob = re.match("http://dblp.uni-trier.de/db/(.*?)/([^/]*)/?.*", url)
            c_j = match_ob.group(1)
            c_j_name = match_ob.group(2)
            level = u["level"]
            cat = u["cat"]

            rows = self.ouput_rows(url, c_j, c_j_name, level, cat, start_year=start_year)

            if len(rows) != 0:
                rows_total.extend(rows)
                cjname_over.append({"name": c_j_name, "num": len(rows)}) # for info

            self.log.info("pro: {}/{} ...".format(ind + 1, len(list_cj)))
            if (ind + 1) % 50 == 0 or (ind + 1) == len(list_cj):
                file = open("../Sources/papers_yield/%s_%d.json" % (filename, ind + 1), "w")
                json.dump(rows_total, file)

                self.log.info("%s has written %d rows to json successfully!" % (cjname_over, len(rows_total)))

                rows_total.clear()
                cjname_over.clear()

            bar.update()


if __name__ == "__main__":
    pc2 = PaperCrawler2()
    pc2.save_json(settings.URL_LIST, "papers", 2017)

    # for i in range(12):
    #     num = (i + 1) * 50
    #     if i == 11:
    #         num = 580
    #     filename = "papers_%d.json" % num
    #
    #     rows = json.load(open("./%s" % filename, "r"))
    #     pc2.save_rows(rows)
    #
    #     pc2.log.info("%s over!" % filename)


