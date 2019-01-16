# Akamai-Scraping
Akamaiのリアルタイム・インターネット・モニターのマップを取得し、GIFを作成するプログラム

Python3.6で作成
seleniumとbeautiful soupを使ってスクレイピングをしています。

マップのデータはHTMLで取得し、CSSを用いて出力しています。

なお、このプログラムはseleniumを使用するためGoogle ChromeとGoogle Chromeに対応したウェブドライバーが必要となります。
こちらから最新のウェブドライバーをダウンロードしてください。
https://sites.google.com/a/chromium.org/chromedriver/downloads

このプログラムを起動する際は以下のようにディレクトリに配置してください。本プログラムと同じ階層にmap.css,chromedriver.exeを配置しないと正常に動作しません。
Folder
 |-akamai_scraping.py
 |-map.css
 |-chromedriver.exe

実際のウェブサイトのURL：https://www.akamai.com/jp/ja/solutions/intelligent-platform/visualizing-akamai/real-time-web-monitor.jsp

https://user-images.githubusercontent.com/46716880/51262711-40b89a80-19f6-11e9-9fe6-4a5d77f726b7.png
