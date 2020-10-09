import html
import json
import math
import os
import re
from urllib import parse

import pyprind

import settings
from Tools import requests_dora


def get_singer_list_page(area_id, page_ind):
    '''

    :param area_id: "{
                        "id":-100,
                        "name":"全部"
                    },
                    {
                        "id":200,
                        "name":"内地"
                    },
                    {
                        "id":2,
                        "name":"港台"
                    },
                    {
                        "id":5,
                        "name":"欧美"
                    },
                    {
                        "id":4,
                        "name":"日本"
                    },
                    {
                        "id":3,
                        "name":"韩国"
                    },
                    {
                        "id":6,
                        "name":"其他"
                    }"
    :param page_ind:
    :return:
    '''
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=857193777; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/portal/singer_list.html"
    }
    paramter = {
        "g_tk": "5381",
        "callback": "getUCGI9688380858412697",
        "jsonpCallback": "getUCGI9688380858412697",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
        "data": '{"comm":{"ct":24,"cv":10000},"singerList":{"module":"Music.SingerListServer","method":"get_singer_list","param":{"area":%d,"sex":-100,"genre":-100,"index":-100,"sin":%d,"cur_page":%d}}}' % (area_id, (page_ind - 1) * 80, page_ind)
    }

    html_text = requests_dora.try_best_2_get(url=url, params=paramter, headers=header).text
    se = re.search("getUCGI9688380858412697\((.*)\)", html_text)
    json_str = None
    if se:
        json_str = se.group(1)

    data = json.loads(json_str)["singerList"]["data"]
    singerlist = data["singerlist"]
    singer_num_total = data["total"]
    return singerlist, singer_num_total


def get_singer_list(area_id):
    singer_list_total = []
    singer_list, total = get_singer_list_page(area_id, 1)
    singer_list_total.extend(singer_list)

    page_max = int(math.ceil(total / 80))
    for i in pyprind.prog_bar(range(1, page_max)):
        page_ind = i + 1
        singer_list, total = get_singer_list_page(area_id, page_ind)
        singer_list_total.extend(singer_list)

    area_2_singers = {}
    for singer in singer_list_total:
        area = singer["country"]
        if area not in area_2_singers:
            area_2_singers[area] = [singer, ]
        else:
            area_2_singers[area].append(singer)

    return area_2_singers


def crawl_song_list_page(singer_mid, begin):
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "cookie": "RK=7dNm4/X + Yj; tvfe_boss_uuid=bf00ee54e9081ab4; pgv_pvi=8772238336; pac_uid=1_857193777; pgv_pvid=6457341280; o_cookie=857193777; ptcz=c761e59c8c8d6bd5198866d02a5cb7313af1af468006c455d6c2b5d26201d42e; pgv_si=s10759168; _qpsvr_localtk=0.08285763449905015; ptisp=ctc; luin=o0857193777; lskey=00010000228dd1371b945c68ecfd3b71d3071425024a7a8a2a23e3ffcb5b9904c9f7088d2ea8c01539ffed92; pt2gguin=o0857193777; uin=o0857193777; skey=@Kydi7w0EI; p_uin=o0857193777; p_skey=HjsE9sEjznJfXk*9KFEeW4VZr6i3*tlXZ2nuzEw8kCg_; pt4_token=c-p6sv3JEboA51cSQ3ABqxM8O80Jct3jYYkgy-aEQuE_; p_luin=o0857193777; p_lskey=000400008f9c296cd10c03a5173d22a184aad124d791568e90e4198beb8ad699a4d02fbfc059f71ab3d8758c; ts_last=y.qq.com/portal/playlist.html; ts_refer=ui.ptlogin2.qq.com/cgi-bin/login; ts_uid=3392060960",
        "referer": "https://y.qq.com/n/yqq/singer/{}.html".format(singer_mid)
    }

    paramter = {
        "g_tk": "5381",
        "jsonpCallback": "MusicJsonCallbacksinger_track",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
        "singermid": singer_mid,
        "order": "listen",
        "begin": begin,
        "num": "30",
        "songstatus": "1",
    }

    html_text = requests_dora.try_best_2_get(url=url, params=paramter, headers=header).text
    json_str = html_text.lstrip(" MusicJsonCallbacksinger_track(").rstrip(")").strip()
    data = json.loads(json_str)["data"]
    song_list = data["list"]
    total_num = data["total"]
    song_list_new = []
    for song in song_list:
        song = song["musicData"]
        song_new = {}
        song_new["albumid"] = song["albumid"]
        song_new["albummid"] = song["albummid"]
        song_new["albumname"] = song["albumname"]
        song_new["songid"] = song["songid"]
        song_new["songmid"] = song["songmid"]
        song_new["songname"] = song["songname"]
        song_list_new.append(song_new)
    return song_list_new, int(total_num)


def get_lyric(song):
    songid = song["songid"]
    songmid = song["songmid"]
    url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg"
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "referer": "https://y.qq.com/n/yqq/song/{}.html".format(songmid)
    }
    paramters = {
        "nobase64": 1,
        "musicid": songid,
        "callback": "jsonp1",
        "g_tk": "1134533366",
        "jsonpCallback": "jsonp1",
        "loginUin": "0",
        "hostUin": "0",
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0"
    }
    html_text = requests_dora.try_best_2_get(url=url, params=paramters, headers=header).text
    res = json.loads(html_text.lstrip("jsonp1(").rstrip(")"))
    if "lyric" in res:
        lyric = res["lyric"]
        if "此歌曲为没有填词的纯音乐，请您欣赏" in lyric:
            return {}, []
        # decode
        lyric = html.unescape(lyric)
        lyric = html.unescape(lyric)
        lyric = parse.unquote(lyric)

        it = re.finditer(r"\[(\d+):(\d+.\d+)\](.+)", lyric)
        lyric_lines = []
        contributors_dict = {}
        for match in it:
            min = float(match.group(1))
            try:
                sec = float(match.group(2))
            except ValueError:
                sec = 0

            line = match.group(3)
            line = line.strip()
            if line == "":
                continue
            se_contributors = re.search("(.*?)[:：](.*)", line)
            if se_contributors:
                contributors_dict[se_contributors.group(1).strip()] = se_contributors.group(2).strip()
                continue
            lyric_lines.append({
                "time": min * 60 + sec,
                "line": line,
            })

        return contributors_dict, lyric_lines[1:]
    else:
        return {}, []


def crawl_song_list(singer):
    singer_mid = singer[settings.KEY_SINGER_MID]
    singer_name = singer[settings.KEY_SINGER_NAME]
    song_list_total = []
    song_list, total = crawl_song_list_page(singer_mid, 0)
    song_list_total.extend(song_list)

    p_ind_list = range(30, total, 30)
    bar1 = pyprind.ProgBar(len(p_ind_list), title="getting song list of {}...".format(singer_name))
    for i in p_ind_list:
        song_list, total = crawl_song_list_page(singer_mid, i)
        song_list_total.extend(song_list)
        bar1.update()

    bar2 = pyprind.ProgBar(len(song_list_total), title="getting the lyric for each song of {}...".format(singer_name))
    for song in song_list_total:
        contributors, lyric = get_lyric(song)
        song[settings.KEY_CONTRIBUTORS] = contributors
        song[settings.KEY_LYRIC] = lyric
        song[settings.KEY_SINGER_NAME] = singer_name
        bar2.update()
        print(song)

    return song_list_total


def crawl_songs(area_list, save_path):
    singer_id_done = []
    for root, dirs, files in os.walk(save_path):
        for file_name in files:
            singer_id = re.search("song_list_.*_(.*).json", file_name).group(1)
            singer_id_done.append(int(singer_id))

    area_2_singers = json.load(open("../Sources/qq_music_yield/area_2_singers.json", "r", encoding="utf-8"))

    for area in area_list:
        singer_list = area_2_singers[area]
        bar = pyprind.ProgBar(len(singer_list), title="process of crawling songs of singers of {}".format(area))
        for singer in pyprind.prog_bar(singer_list):
            singer_name = singer[settings.KEY_SINGER_NAME]
            singer_id = singer[settings.KEY_SINGER_ID]
            if singer_id in singer_id_done:
                continue
            song_list = crawl_song_list(singer)
            json.dump(song_list,
                      open("%s/song_list_%s_%s.json" % (save_path, singer_name, singer_id), "w", encoding="utf-8"))
            bar.update()

if __name__ == "__main__":
    # area_2_singers = get_singer_list(-100)
    # print(len(area_2_singers))
    # json.dump(area_2_singers, open("../Sources/area_2_singers.json", "w", encoding="utf-8"))

    # area_list = ["内地", "台湾", "香港", "新加坡"]
    # save_path = "D:\\dataset/qq_music_songs"
    # crawl_songs(area_list, save_path)

    lyric = '''D_IID=AC7C314D-15C6-352C-B0CE-83093C3D555C; D_UID=5F6D59DA-447C-3BFE-9A3C-B08C801EE849; D_ZID=3DAF0B68-5739-3BAA-B930-14C292159598; D_ZUID=77D70E71-A1FD-325C-B132-2DB01AFAE0B4; D_HID=6C845E4B-149F-3A6C-8325-2EC86A4808A4; D_SID=104.245.14.42:PNTZtxZoKxzwu3dMw0yCLGmYMckEJlzDIbVZ046ZtA4; cust_id=291d4037-cfec-4468-b9e0-a9f10c90e95c; refer_id=0000; city=San%20Jose; state=CA; lat=37.392395; lon=-121.962296; ipContinent=NA; _ga=GA1.2.1705640379.1547365676; _gid=GA1.2.1626407314.1547365676; calltrk_referrer=https%3A//www.manta.com/business; calltrk_landing=https%3A//www.manta.com/business; ftoggle-frontend-production=1546871818961zaaaSGdLDFaCPaDBdZAz1; __gads=ID=04e6411d6ebd7e5f:T=1547368009:S=ALNI_MaFGUEfFmYWkGWCuBs-E-x_Hc-txw; ipCountry=US; hasConsent=Y; ct_cookies_test=399a31619b32de717906c59d4998df8a; PHPSESSID=4995fvo2lbc534jnkohvru12b1; apbct_site_landing_ts=1547374547; ct_timestamp=1547374551; ct_checkjs=266276329; apbct_visible_fields=0; apbct_visible_fields_count=0; _ga=GA1.3.1705640379.1547365676; _gid=GA1.3.1626407314.1547365676; msbi=yes; contently_insights_user=ac1b2td713k6034e4e92; _bts=be9ce058-5c17-409c-adc1-86e60fec7d4a; _bti=%7B%22app_id%22%3A%22ed6e6b11168e3880f61e111016d10d9a%22%2C%22bsin%22%3A%22oDP%2BN55ELxxOGQLv5FmnKzyfZY0KYbJFsYRxii1MKZoFC6MCicGWsHhSAzZ0XIEwh02ACB6yYgRrrXZicxlbnQ%3D%3D%22%7D; crfgL0cSt0r=true; apbct_timestamp=1547375456; apbct_prev_referer=https%3A%2F%2Fwww.google.com%2F; apbct_page_hits=2; apbct_cookies_test=%7B%22cookies_names%22%3A%5B%22apbct_timestamp%22%2C%22apbct_prev_referer%22%2C%22apbct_site_landing_ts%22%2C%22apbct_page_hits%22%5D%2C%22check_value%22%3A%22e8c9ad4d44152d78c4ac14e178cd4835%22%7D; ct_ps_timestamp=1547375462; ct_timezone=8; mp_1c822e9904690975d2950bcbc115075a_mixpanel=%7B%22distinct_id%22%3A%20%2216846b5fa39234-05a8291779ca7d-b781636-144000-16846b5fa3a975%22%2C%22%24device_id%22%3A%20%2216846b5fa39234-05a8291779ca7d-b781636-144000-16846b5fa3a975%22%2C%22first_wp_page%22%3A%20%22The%20Academy%20-%20Manta%22%2C%22first_wp_contact%22%3A%20%22Sun%20Jan%2013%202019%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.manta.com%2Fc%2Fmb09480%2Frcn-imports-inc%22%2C%22%24initial_referring_domain%22%3A%20%22www.manta.com%22%2C%22%24search_engine%22%3A%20%22google%22%7D; mp_f6712b90922aca648f9e2307427ca86f_mixpanel=%7B%22distinct_id%22%3A%20%2216845c95c0e26b-0ca9bf0cc6e5b8-b781636-144000-16845c95c0f186%22%2C%22%24device_id%22%3A%20%2216845c95c0e26b-0ca9bf0cc6e5b8-b781636-144000-16845c95c0f186%22%2C%22offHours%22%3A%20true%2C%22treatment%22%3A%20%22no-test%22%2C%22altTreatment1%22%3A%20%22Postpone%20Merchant%20Scan%20control%22%2C%22altTreatment2%22%3A%20%22Claim%20Flow%20Reviews%22%2C%22altTreatment3%22%3A%20%22%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.manta.com%2Fbusiness%22%2C%22%24initial_referring_domain%22%3A%20%22www.manta.com%22%2C%22%24search_engine%22%3A%20%22google%22%7D; pageDepth=20; ct_pointer_data=%5B%5B0%2C424%2C61265%5D%2C%5B128%2C440%2C61361%5D%2C%5B198%2C446%2C61883%5D%2C%5B198%2C460%2C61974%5D%2C%5B208%2C473%2C62110%5D%2C%5B213%2C474%2C62258%5D%2C%5B220%2C474%2C62500%5D%2C%5B224%2C471%2C62560%5D%2C%5B231%2C467%2C62709%5D%2C%5B248%2C460%2C62860%5D%2C%5B261%2C458%2C63009%5D%2C%5B268%2C434%2C63324%5D%2C%5B268%2C449%2C63469%5D%2C%5B268%2C481%2C63609%5D%2C%5B264%2C488%2C63782%5D%2C%5B306%2C488%2C63911%5D%2C%5B341%2C453%2C64061%5D%2C%5B362%2C422%2C64226%5D%2C%5B364%2C420%2C64362%5D%2C%5B372%2C412%2C64603%5D%2C%5B368%2C421%2C64663%5D%2C%5B326%2C524%2C64813%5D%2C%5B359%2C543%2C65145%5D%2C%5B411%2C539%2C65312%5D%2C%5B409%2C528%2C65414%5D%2C%5B408%2C512%2C65613%5D%2C%5B408%2C508%2C65856%5D%2C%5B408%2C507%2C65872%5D%2C%5B408%2C504%2C66131%5D%2C%5B408%2C503%2C66180%5D%2C%5B408%2C502%2C66681%5D%2C%5B408%2C501%2C67063%5D%2C%5B409%2C500%2C67315%5D%2C%5B409%2C498%2C68455%5D%2C%5B411%2C496%2C68774%5D%2C%5B411%2C495%2C69091%5D%2C%5B412%2C492%2C69286%5D%2C%5B415%2C486%2C69316%5D%2C%5B428%2C435%2C69466%5D%2C%5B435%2C388%2C69617%5D%2C%5B440%2C385%2C69797%5D%2C%5B451%2C419%2C69916%5D%2C%5B454%2C473%2C70073%5D%2C%5B454%2C520%2C70217%5D%2C%5B454%2C533%2C70367%5D%2C%5B454%2C542%2C70517%5D%2C%5B546%2C537%2C70752%5D%5D; ct_fkp_timestamp=1547375578'''
    # lyric = html.unescape(lyric)
    # lyric = html.unescape(lyric)
    lyric = parse.unquote(lyric)
    print(lyric)

