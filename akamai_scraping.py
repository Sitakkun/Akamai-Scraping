# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 11:54:53 2018

@author: 清水 匠
"""

#akamaiのトラフィックマップを頑張ってスクレイピングする！！
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Thread
from selenium.common.exceptions import UnexpectedAlertPresentException
from PIL import Image
import bs4, time, os, re, datetime, glob, requests, sys

"""global 変数"""
#保存するファイル名に使用
today = str(datetime.datetime.now()).replace(":","-")
#ループ用のフラグ 
cond = True
#seleniumのオプション変数
options = Options()
options.add_argument('--headless')
#trafficとattackのタイムスタンプを格納する変数
traffic_timestamp = ""
attack_timestamp = ""
#マップを成型するCSSにリンクさせるためのタグ
css_tag = "<head><meta charset=\"Shift_JIS\"><link rel=\"stylesheet\" type=\"text/css\" href=\"css_test.css\"></head>"
#解析する時間を指定する変数
scraping_time = 0
#解析した回数を記録する変数
count = 1
#画像をキャプチャした回数を記録する変数
traffic_captcha_count = 1
attack_captcha_count = 1


"""スクリーンショットを保存する関数"""
def captcha(filename): 
    global today
    global options
    global scraping_time
    global traffic_captcha_count
    global attack_captcha_count

    scraping_time_hour = str(scraping_time/3600)
    folder_name = today + '_' + scraping_time_hour + "hour"

    #ファイル名で攻撃かトラフィックかを判断し適切なフォルダへ保存する
    pattern = r".*traffic.*"
    if re.match(pattern,filename):
        captcha_filename = "./captcha/traffic/" + folder_name + "/" + filename.replace(".html",".png")
        #ファイル名を取得した回数の番号に置き換える（日をまたぐときにGIFの順序がおかしくなることを防ぐため）
        name, ext = os.path.splitext(filename)
        captcha_filename = captcha_filename.replace(name,str(traffic_captcha_count))
        traffic_captcha_count = traffic_captcha_count + 1
    else:
        captcha_filename = "./captcha/attack/" + folder_name + "/" + filename.replace(".html",".png")
        #ファイル名を取得した回数の番号に置き換える（日をまたぐときにGIFの順序がおかしくなることを防ぐため）
        name, ext = os.path.splitext(filename)
        captcha_filename = captcha_filename.replace(name,str(attack_captcha_count))
        attack_captcha_count = attack_captcha_count + 1

    #ブラウザに送るパスの作成
    abs_filename_url = "file:///"+os.path.abspath(filename)
    abs_filename_url = abs_filename_url.replace("\\","/")
    
    #print(abs_filename_url)
    captcha_driver = webdriver.Chrome(executable_path="./chromedriver.exe", chrome_options=options)
    captcha_driver.get(abs_filename_url)
    page_width = captcha_driver.execute_script('return document.body.scrollWidth')
    page_height = captcha_driver.execute_script('return document.body.scrollHeight')
    captcha_driver.set_window_size(page_width,page_height)
    time.sleep(2)
    captcha_driver.save_screenshot(captcha_filename)
    print("スクリーンショット保存")
    captcha_driver.close()

"""Akamaiから画像をダウンロードする関数"""
def akamai():
    global today
    global cond
    global options
    global traffic_timestamp
    global attack_timestamp
    global scraping_time

    scraping_time_hour = str(scraping_time/3600)
    folder_name = today + '_' + scraping_time_hour + 'hour'
    
    os.makedirs("captcha",exist_ok=True) #スクリーンショットを保存するフォルダ
    os.makedirs("captcha/attack",exist_ok=True)
    os.makedirs("captcha/traffic",exist_ok=True)


    os.makedirs("captcha/attack/" + folder_name,exist_ok=True)
    os.makedirs("captcha/traffic/" + folder_name,exist_ok=True)

    top_url = "https://www.akamai.com/jp/ja/"
    url = "https://www.akamai.com/jp/ja/solutions/intelligent-platform/visualizing-akamai/real-time-web-monitor.jsp"

    #AkamaiのWebページを表示する。
    #この際、Cookieを取得する。
    driver = webdriver.Chrome(executable_path="./chromedriver.exe", chrome_options=options)
    driver.get(top_url)
    driver.get_cookies()
    driver.get(url)
    driver.get_cookies()
    driver.refresh()
    time.sleep(10)
    
    print("トラフィック")
    try:     
        soup = bs4.BeautifulSoup(driver.page_source, "lxml")
        for svg in soup.find_all('div', class_='map_col'):
            svg.select('svg')
            #以下2行デバッグ用
            #print(svg)
            #print()

            #ページが更新されているかを確認するためのタイムスタンプの取得
            timestamp = soup.find_all('div', class_='timestamp')
            t_timestamp = timestamp[0].getText()

            #HTMLが正常に取得できているかを判断する。
            if t_timestamp == "":
                print("通知：ファイル取得エラー.HTMLソースを正しく取得できませんでした。")
                res = requests.get(driver.page_source)
                file = open("dump.html",'w')
                file.write(res)
                file.close()
            #正常にHTMLが取得されていた場合、タイムスタンプの値を比較してページが更新されているかを判断する。
            elif t_timestamp != traffic_timestamp:
                print("t_timestamp:"+t_timestamp)
                print("traffic_timestamp:"+traffic_timestamp)
                filename = str(datetime.datetime.now())+"_traffic.html"
                filename = filename.replace(':','-')
                print(filename)
                svg_html = css_tag + str(svg)
                file = open(filename,'w')
                file.write(svg_html)
                file.close()
                captcha(filename)
                os.remove(filename)
                traffic_timestamp = t_timestamp
            else:
                print("t_timestamp:"+t_timestamp)
                print("traffic_timestamp:"+traffic_timestamp)
                print("通知：trafficのマップは更新されていません。")
    
    except UnexpectedAlertPresentException:
        print("通知：seleniumエラー")

    print("攻撃")    
    try:
        #「攻撃」のデータを取得するためリンクをクリック
        link_elem = driver.find_element_by_id("attack_tab")
        link_elem.click()
        time.sleep(10)

        soup = bs4.BeautifulSoup(driver.page_source, "lxml")
        for svg in soup.find_all('div', class_='map_col'):
            svg.select('svg')
            #print(svg)
            #print()
            timestamp = soup.find_all('div', class_='timestamp')
            a_timestamp = timestamp[0].getText()
            if a_timestamp == "":
                print("通知：ファイル取得エラー.HTMLソースを正しく取得できませんでした。")
                res = requests.get(driver.page_source)
                file = open("dump.html",'w')
                file.write(res)
                file.close()
            elif a_timestamp != attack_timestamp:
                print("a_timestamp:"+a_timestamp)
                print("attack_timestamp:"+attack_timestamp)
                filename = str(datetime.datetime.now())+"_attack.html"
                filename = filename.replace(':','-')
                print(filename)
                svg_html = css_tag + str(svg)
                file = open(filename,'w')
                file.write(svg_html)
                file.close()
                captcha(filename)
                os.remove(filename)
                attack_timestamp = a_timestamp
            else:
                print("a_timestamp:"+a_timestamp)
                print("attack_timestamp:"+attack_timestamp)
                print("通知：attackのマップは更新されていません。")
        driver.close()
    except UnexpectedAlertPresentException:
        print("通知：seleniumエラー")


"""GIF画像に変換する関数"""
def gif_convert(today):
    global scraping_time

    scraping_time_hour = str(scraping_time/3600)
    folder_name = today + '_' + scraping_time_hour + "hour"

    print('GIFに変換する処理を開始します。')
    #各項目のPNGファイルのリストを作成するためのパス
    traffic_png_glob = './captcha/traffic/' + folder_name + '/*.png'
    attack_png_glob = './captcha/attack/' + folder_name + '/*.png'
    
    #保存する場所のパス
    traffic_gif_filename = './captcha/traffic/' + folder_name + '/' + folder_name + '_traffic.gif'
    attack_gif_filename = './captcha/attack/' + folder_name + '/' + folder_name + '_attack.gif'
    
    #整列したPNGファイルのリストを取得
    traffic_files = sorted(glob.glob(traffic_png_glob))
    attack_files = sorted(glob.glob(attack_png_glob))
    
    #PNGファイルを読み込む
    traffic_images = list(map(lambda file: Image.open(file), traffic_files))
    attack_images = list(map(lambda file: Image.open(file), attack_files))
    
    #GIF画像の作成
    traffic_images[0].save(traffic_gif_filename, save_all=True, append_images=traffic_images[1:], duration=250, loop=0)
    if os.path.isfile(traffic_gif_filename):
        print('trafficの画像をGIFに変換することに成功しました。')
    else:
        print('trafficの画像をGIFに変換することに失敗しました。')
        sys.exit("GIF convert Error")
    attack_images[0].save(attack_gif_filename, save_all=True, append_images=attack_images[1:], duration=250, loop=0)
    if os.path.isfile(attack_gif_filename):
         print('attackの画像をGIFに変換することに成功しました。')
    else:
        print('attackの画像をGIFに変換することに失敗しました。')
        sys.exit("GIF convert Error")

    #PNGの画像を削除
    for png in glob.glob(traffic_png_glob):
        if os.path.isfile(png):
            os.remove(png)

    for png in glob.glob(attack_png_glob):
        if os.path.isfile(png):
            os.remove(png)

"""時間監視用関数"""
def f():
    global cond
    global today
    global scraping_time

    #指定時間分待機
    time.sleep(scraping_time)
    print("指定時間たったため、Web監視を終了します")
    cond = False
    gif_convert(today)
    sys.exit('Succeeded.')
    


if __name__ == "__main__":
    print(datetime.datetime.now())
    print("Akamaiのウェブモニタリングのマップをダウンロードします。")  

    print("マップを解析する時間を指定してください。")
    scraping_time = float(input("単位（時間）："))
    scraping_time = round(scraping_time * 3600)


    #スレッドの開始  
    thread = Thread(target=f)
    thread.start()


    #指定時間経過するまで画像取得
    while cond:
        print(str(count) + "回目の取得 : ",end="")
        print(datetime.datetime.now())

        """
        if today != str(datetime.date.today()):
            #日付が変わったら画像取得終了
            print("日付が変わったため、Web監視を終了します")
            cond = False
            break
        """

        akamai()
       #2分間待機
        print("2分間待機.....")
        print()
        time.sleep(120)
        count += 1
    




