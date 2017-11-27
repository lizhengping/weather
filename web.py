#coding = utf-8
import urllib
import re
import urllib.request
import time
import os
import imageResize
from PIL import Image,ImageDraw,ImageFont
import json



def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    html = html.decode('utf-8')
    print(html)
    return html

def wenzi(im,state):

    font = ImageFont.truetype('Songti.ttc', 30)
    draw = ImageDraw.Draw(im)
    day = time.strftime(u"%Y年%m月%d日", time.localtime(time.time()))

    ########配文字################

    text = u'兴隆站天气' + day + u'\n凌晨 ' + state[0] + u'\n930 ' + state[1]+ u'\n当天 ' + state[2]+ u'\n次日 ' + state[3]
    # text = u'你好\n你好'
    print(text)
    draw.text((20, 20), text, font=font, fill='#000000')
    text1 = u'凌晨云量'
    draw.text((20,220), text1, font=font, fill='#000000')
    text2 = u'当前云量'
    draw.text((20, 820), text2, font=font, fill='#000000')
    text3 = u'晴天钟预报'
    draw.text((20, 1420), text3, font=font, fill='#000000')
    text4 = u'天气预报'
    draw.text((20, 1820), text4, font=font, fill='#000000')

    return  im

def Yuntu(arr):
    global dayNow
    global state
    toImage = Image.new('RGBA', (900, 4400))
    for i in range(4):
        fromImge = Image.open(arr[i])
        loc = (50,(i * 600+270))
        if i==3:
            loc = (50,1870)
        print(loc)
        toImage.paste(fromImge, loc)

    toImage=wenzi(toImage,state)

    toImage.save("./"+dayNow+'/weatheReport.png')

def mkdir(path):
    # 引入模块
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print("创建文件夹"+path)


def download(_url, name):  # 下载函数
    if (_url == None):  # 地址若为None则跳过
        pass
    result = urllib.request.urlopen(_url)  # 打开链接
    # print result.getcode()
    if (result.getcode() != 200):  # 如果链接不正常，则跳过这个链接
        pass
    else:
        data = result.read()  # 否则开始下载到本地
        with open(name, "wb") as code:
            code.write(data)
            code.close()


def GetNowTime():
    d=time.strftime("%Y_%m_%d",time.localtime(time.time()))
    t= time.strftime("%H_%M_%S",time.localtime(time.time()))
    return d,t

def find_midnightUrl(imglist):
    midnightUrl=''
    for i in imglist:
        if (midnightUrl=='')and(i[0].find('/00_0') != -1):
            midnightUrl =i[0]
    return midnightUrl

def get_all_and_get_midnightUrl(imglist):
    print(imglist)
    midnight = 0
    for n in range (len(imglist)):
        time = re.findall(r"\d\d_\d\d_\d\d", imglist[n][0])
        day = re.findall(r"\d\d\d\d/\d\d/\d\d", imglist[n][0])
        day[0]=day[0].replace("/","_")
        mkdir(day[0])

        if (midnight==0) and (time[0][:5]=='00_0'):
            midnight=n
            print('yuntu1 is :',time[0])

        download(imglist[n][0],"./"+day[0]+"/"+time[0]+".jpg")
        print(time[0])
    midnightUrl = imglist[midnight][0]
    return midnightUrl


def getImg(html):
    midnight=0
    d, t = GetNowTime()
    mkdir(d)
    ########晴天钟图################
    weather_clock_url = "http://202.127.24.18/v4/bin/astro.php?lon=117.275&lat=40.26&lang=zh-CN&ac=0&unit=metric&tzshift=0"
    weather_clock="./" + str(d)+"/"+str(t) + "_weather_clock.jpg"
    download(weather_clock_url, weather_clock)

    ########天气预报图################
    weather_forecast_url = "http://202.127.24.18/v4/bin/two.php?lon=117.275&lat=40.26&lang=zh-CN&ac=0&unit=metric&output=internal&tzshift=0"
    weather_forecast="./" + str(d) + "/" + str(t) + "_weather_ forecast.jpg"
    download(weather_forecast_url, weather_forecast)

    pattern = "(http:[^\s]*?(jpg|png|PNG|JPG))"
    imglist = re.findall(pattern, html)

    ########打开这个会把全部全天相机图下载，返回值可以忽略################
    #midnightUrl=get_all_and_get_midnightUrl(imglist)

    midnightUrl = find_midnightUrl(imglist)
    print(midnightUrl)

    nowUrl = imglist[0][0]
    urls=[midnightUrl,nowUrl,weather_clock_url,weather_forecast_url]

    weatherReport(urls)
    print(urls)

def weatherReport(urls):
    global state
    arr=[]
    for i in range(len(urls)):
        download(urls[i], "./"+dayNow+'/'+str(i)+".jpg")
        a=imageResize.Graphics("./"+dayNow+'/'+str(i))
        if i<2:
            a.fixed_size(768, 512)
        if i==2:
            a.fixed_size(768, 312)
        if i==3:
            a.fixed_size(768, 1200)
        arr.append("./"+dayNow+'/'+str(i)+'_1.jpg')
        #arr=
    Yuntu(arr)

def get_state(version=1):
    global state

    ########晴天钟json数据################
    ApiUrl = "http://202.127.24.18/v4/bin/astro.php?lon=117.275&lat=40.26&ac=0&lang=en&unit=metric&output=json&tzshift=0"

    html = urllib.request.urlopen(ApiUrl)
    data = html.read().decode("utf-8")
    ss = json.loads(data)
    print (ss)
    data = ss['dataseries']
    print (data)

    # cloudcover=[0 for x in range(len(data))]
    cloudcover = {}
    cloudcover_state = [0,0,0,0]

    for i in data:
        cloudcover[i['timepoint']] = i['cloudcover']
    print (cloudcover)

    ########早上运行################
    if version == 1:
        cloudcover_morning = (cloudcover[6] + cloudcover[9]) / 2
        cloudcover_today = (cloudcover[21] + cloudcover[24]) / 2
        cloudcover_tomorrow = (cloudcover[45] + cloudcover[48]) / 2
        cloudcover_state = [0, cloudcover_morning, cloudcover_today, cloudcover_tomorrow]
        for i in range(3):
            if cloudcover_state[i + 1] > 0:
                state[i + 1] = u"优"
            if cloudcover_state[i + 1] > 5:
                state[i + 1] = u"良"
            if cloudcover_state[i + 1] > 7:
                state[i + 1] = u"差"

    ########前一天晚上运行，得到凌晨状况，默认优################
    if version == 2:
        cloudcover_yesterday = (cloudcover[27] + cloudcover[30]) / 2
        if cloudcover_state[0] > 0:
            state[0] = u"优"
        if cloudcover_state[0] > 4:
            state[0] = u"良"
        if cloudcover_state[0] > 7:
            state[0] = u"差"
        pass
    print (state)


if __name__ == '__main__' :

    global state
    global dayNow
    dayNow = time.strftime(u"%Y_%m_%d", time.localtime(time.time()))
    state = [u'优', u'优', u'优', u'优']
    get_state()

    ########天文台全天相机################
    html = getHtml("http://www.xinglong-naoc.org/weather/")
    getImg(html)






