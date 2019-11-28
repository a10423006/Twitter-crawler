# -*- coding: utf-8 -*-
import tweepy
import pandas as pd
from datetime import datetime
from key import host, account, password, database, consumer_key, consumer_secret, access_token, access_token_secret
import  pymysql
import re

db = pymysql.connect(host, account, password, database)
cursor = db.cursor()

# Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

create_time = []
user_name = []
link_tweet = []
tweet_content = []

# 帳號=@realDonaldTrump, extended模式才能抓full_text
status = api.user_timeline('realDonaldTrump', tweet_mode="extended")

# 最近20則
for i in range(0, len(status)):
    #日期轉換
    t = status[i]._json['created_at'].replace('+0000 ', '')
    t_format = datetime.strptime(t, "%a %b %d %H:%M:%S %Y")
    create_time.append(t_format)
    
    user_name.append(status[i]._json['user']['name'])
    link_tweet.append('https://twitter.com/realDonaldTrump/status/' + status[i]._json['id_str'])
    # 把多個空行轉成僅一個換行
    tweet_content.append("\n".join(re.split(r"\n+", status[i]._json['full_text'])))
    
twitter_table = pd.DataFrame({'Create Time': create_time, 
                              'User Name': user_name, 
                              'Tweet Content': tweet_content,
                              'Link': link_tweet})

#twitter_table.to_csv('Twitter.csv', index=False, header = False, mode='a')


for i in range(0, len(twitter_table)):
    sql = 'INSERT INTO etf_twitter(`Create Time`, `User Name`, `Tweet Content`, `Link`) VALUES("%s", "%s", "%s", "%s")' % \
            (twitter_table['Create Time'][i], twitter_table['User Name'][i], 
             twitter_table['Tweet Content'][i].replace('\n"',''), twitter_table['Link'][i])
            
    try:
        cursor.execute(sql)
        cursor.excute("alter table etf_twitter AUTO_INCREMENT=1;") #讓ID重新計算
        db.commit()
    except:
       db.rollback()

db.close()
