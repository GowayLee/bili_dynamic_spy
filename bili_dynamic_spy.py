"""bili_dynamic_spy"""

import datetime
import json
import csv
import time
import requests

dynamic_type_dict = {
    "DYNAMIC_TYPE_NONE"	            :       "无效动态",
    "DYNAMIC_TYPE_FORWARD"	        :       "动态转发",	
    "DYNAMIC_TYPE_AV"	            :       "投稿视频",	
    "DYNAMIC_TYPE_PGC"	            :       "剧集（番剧、电影、纪录片）",
    "DYNAMIC_TYPE_COURSES"		    :       "TYPE_COURSES",
    "DYNAMIC_TYPE_WORD"	            :       "纯文字动态",
    "DYNAMIC_TYPE_DRAW"	            :       "带图动态",
    "DYNAMIC_TYPE_ARTICLE"	        :       "投稿专栏",
    "DYNAMIC_TYPE_MUSIC"	        :       "音乐",
    "DYNAMIC_TYPE_COMMON_SQUARE"	:       "装扮/剧集点评/普通分享",
    "DYNAMIC_TYPE_COMMON_VERTICAL"  :       "TYPE_COMMON_VERTICAL",  	
    "DYNAMIC_TYPE_LIVE"	            :       "直播间分享",
    "DYNAMIC_TYPE_MEDIALIST"	    :       "收藏夹",
    "DYNAMIC_TYPE_COURSES_SEASON"	:       "课程",
    "DYNAMIC_TYPE_COURSES_BATCH"	:       "TYPE_COURSES_BATCH",   	
    "DYNAMIC_TYPE_AD"		        :       "TYPE_AD",
    "DYNAMIC_TYPE_APPLET"		    :       "TYPE_APPLET",
    "DYNAMIC_TYPE_SUBSCRIPTION"	    :       "TYPE_SUBSCRIPTION",	
    "DYNAMIC_TYPE_LIVE_RCMD"	    :       "直播开播",
    "DYNAMIC_TYPE_BANNER"           :       "TYPE_BANNER",
    "DYNAMIC_TYPE_UGC_SEASON"	    :       "合集更新",
    "DYNAMIC_TYPE_SUBSCRIPTION_NEW" :       "TYPE_SUBSCRIPTION_NEW"
}

major_type_dict = {
    "ugc_season":	"合集信息",
    "article"	:	"专栏",
    "draw"		:   "带图动态",
    "archive"	:	"视频",
    "live_rcmd"	:	"直播状态",
    "common"	:	"一般类型",
    "pgc"		:   "剧集更新",
    "courses"	:	"课程",
    "music"		:   "音频更新",
    "opus"		:   "图文动态",
    "live"		:   "直播间",
    "none"		:   "动态失效"	
}

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
HEADERS = ["时间", "类型", "文本内容", "转发/投稿", "主体类型", "转发/投稿源标题"]
UID = config.get("tar_uid")
DEEPTH = config.get("crawl_deepth")

def main():
    """Main function"""
    baseurl = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    data = get_data(baseurl, UID, offset="")
    if data == "":
        print("获取数据失败")
        return
    savepath = ".\\saved\\" + get_name(data) + "的成分表.csv"
    with open(savepath, 'w', newline='', encoding='utf-8') as csv_file: # 创建csv文件, 并写入字段名
        writer = csv.writer(csv_file)
        writer.writerow(HEADERS)
    # 更新页面偏移数据
    has_more = data.get("data").get("has_more")
    cur_offset = data.get("data").get("offset")
    parse_data(data)
    save_csv_data(savepath, [])

    if has_more is True and DEEPTH > 0:
        for i in range(0, DEEPTH): # 第一次页面偏移时会重叠一条旧动态

            data = get_data(baseurl, UID, cur_offset)
            if data == "":
                print("获取数据失败")
                return
            has_more = data.get("data").get("has_more")
            cur_offset = data.get("data").get("offset")
            datapage = parse_data(data)

            if i == 1:
                datapage.pop(0) # 去除第一条重复的动态
            save_csv_data(savepath, datapage)
            if has_more is False:
                break
            time.sleep(0.2)

    return

def get_data(baseurl: str, uid: str, offset: str):
    """Parse response from bilibili api to json str"""
    respond = ask_url(baseurl, uid, offset)
    if respond != "":
        return json.loads(respond)
    return ""

def parse_data(data):
    """Parse info from json str"""
    datetime_instance = datetime.datetime
    datapage = []
    items = data.get("data").get("items")

    for item in items:
        data_row = [] # [动态时间, 动态类型, 动态文本, 转发/投稿, 转发/投稿源标题]
        text = ""
        ref_type = ""
        ref_major_type = ""
        ref_title = ""
        module = item.get("modules")

        pub_time = None
        author = module.get("module_author")
        if author is not None:
            pub_time = datetime_instance.fromtimestamp(module.get("module_author").get("pub_ts"))
        else:
            pub_time = "-"
        data_row.append(pub_time)

        pub_type = dynamic_type_dict.get(item.get("type"))
        data_row.append(pub_type)

        dynamic = module.get("module_dynamic")
        if dynamic is not None:
            desc = dynamic.get("desc")
            if desc is not None:
                text = desc.get("text")
            else:
                text = "-"
            data_row.append(text.replace("\n", " ")) # 去除换行符
            major = dynamic.get("major")
            orig = item.get("orig")
            if orig is None and major is None:
                ref_type = "-"
                ref_major_type = "-"
            elif major is not None: # 附有投稿/更新
                ref_type = "投稿/更新"

            elif orig is not None: # 附有转发, 记录转发的动态主体类型与主体标题
                ref_type = "转发"
                major = orig.get("modules").get("module_dynamic").get("major")

            try:    # 神奇问题, 不同情况下的请求, 返回的JSON有细微但是致命的区别, 导致无法正确解析
                major_type = major.get("type")
                if major_type is not None:
                    major_type_key = split_str(major_type)
                    ref_major_type = major_type_dict.get(major_type_key) # 动态主体类型

                    if major_type_key not in ('draw', 'live_rcmd', 'none'): # 非 带图动态、直播推荐、动态失效
                        major_type_value = major.get(major_type_key)
                        if major_type_value is not None:
                            ref_title = major_type_value.get("title")
                        else:
                            ref_title = "-"
                    else:
                        ref_title = "*无标题*"
                else:
                    ref_major_type = "-"
                    ref_title = "-"

                data_row.append(ref_type)
                data_row.append(ref_major_type)
                data_row.append(ref_title.replace('\n', ' '))
            except AttributeError as e:
                print(f"Error: {e}")
                data_row.append(ref_type)
                data_row.append("N/A")
                data_row.append("N/A")

        datapage.append(data_row)
        current_datetime = datetime_instance.now()
        print(f"{current_datetime}:" + "\033[32m[INFO]\033[0m" + " Successfully get the data of >>" + text)

    return datapage

def get_name(data):
    """Get the name of the user who posted the dynamic"""
    items = data.get("data").get("items")
    if len(items) > 0:
        return items[0].get("modules").get("module_author").get("name")
    return "不发动态的人"

def split_str(text):
    """Do slice and lowercase the string 'MAJOR_TYPE_LIVE_RCMD' -> 'live_rcmd'"""
    parts = text.split('_')
    if len(parts) > 2:
        effect_part = '_'.join(parts[2:])
        result = effect_part.lower()
        return result
    return ""

def ask_url(url: str, uid: str, offset: str):
    """Send HTTP request"""
    header = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-Encoding': 'gzip, deflate, br, zstd',
        'accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'origin': 'https://space.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    config_cookie = config.get("cookies")
    cookie = {
        "buvid3": config_cookie.get("buvid3"),
        "b_nut": config_cookie.get("b_nut"),
        "_uuid": config_cookie.get("_uuid"),
        # "buvid_fp": "b2b6560be780932f3c6455a3d03e3c41",
        "buvid4": config_cookie.get("buvid4"),
    }

    param = {
        'offset': offset,
        'host_mid': uid
    }

    response = requests.get(url, params=param, cookies=cookie, headers=header, timeout=8)
    if response.status_code == 200:
        return response.text
    print("鉴权失败! 请检查Cookie")
    return ''

def save_csv_data(savepath: str, datapage: list):
    """Save data of one page to savepath"""
    with open(savepath, 'a', newline='', encoding='utf-8') as csv_file: # 追加模式, 每一次刷新都进行追加
        writer = csv.writer(csv_file)
        for row in datapage:
            writer.writerow(row)

if __name__ == "__main__":
    main()
    print("爬取完毕！")
