#推特自动转发抽奖机器人，前提要有推特开发者账号。原作者：zlexdl.eth

import tweepy
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random

engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/db?charset=utf8')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

consumer_key = ''
consumer_secret = ''

key = ''
secret = ''
##——————————这部分可以修改——————————————
keywords = 'Follow,Like,RT,Tag,Retweet,FOLLOW,LIKE,RETWEET,TAG,关注,转推,喜欢'  # 这个可以后续再补充
#转推内容
tweets = [
                '@petechang1113 @abc_noName1 @kevinLiuA1110 @tastydogclub @Adidasshow78 @mike1021031',
                '@Tony34108142 @waynechen2032 @Macnotmc1 @sodassdf @Ro0dZz @chou22389047 @stone20213 ',
                '@itivitimonster @Malachi007 @Ivanyichen @SawadyQ @jayfans15 @RoyLiu68727021 @havel_wu ']
##——————————这部分可以修改——————————————


auth = tweepy.OAuthHandler(consumer_key,
                           consumer_secret)
auth.set_access_token(key,
                      secret)

api = tweepy.API(auth)

#定义一个结构体
class TwitterBot(Base):
    __tablename__ = "twitter_bot"  # 数据库中保存的表名字
    id = Column(Integer, index=True, primary_key=True)
    tweet_id = Column(Integer, nullable=True)
    screen_name = Column(String(200), nullable=True)
    url = Column(String(300), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


while True:
    print("@@@@@@@@@@@@@@@@@@@@Start@@@@@@@@@@@@@@@@@@@@@@")
    print(datetime.utcnow())

    public_tweets = []

    try:
        # public_tweets = api.home_timeline(count=50, tweet_mode='extended')
        # public_tweets = api.user_timeline(screen_name='reinkerte31', count=3, tweet_mode='extended')
        public_tweets = api.list_timeline(list_id=1444116199432806401, count=100, tweet_mode='extended')

    except Exception as e:
        print(str(e))
        print("sleep 60s")
        time.sleep(60)
        continue

    for tweet in public_tweets:

        if session.query(TwitterBot).filter(TwitterBot.tweet_id == tweet.id).count() > 0:
            print(str(tweet.id) + "已存在。")  #之前已经操作过的推文就跳过
            continue

        print("id=" + str(tweet.id))
        print("created_at=" + str(tweet.created_at))

        p = tweet.full_text


        count = sum([1 if w in p and w else 0 for w in keywords.split(',')])
        if count > 1:
            print("---------------------Found 白名单推文")
            print(tweet.full_text)


            #推文中@的人都关注上
            user_mentions = tweet.entities['user_mentions']
            for friend in user_mentions:
                screen_names = friend['screen_name']

                friendships = api.lookup_friendships(screen_name=screen_names)

                if len(friendships) > 1:

                    if not friendships[1].is_following:
                        print("Following <" + screen_name + "> ")
                        api.create_friendship(screen_name=screen_name)

                        print("Follow <" + screen_name + "> success!")
                    else:
                        print("Already following <" + screen_name + "> !")

            #点爱心
            try:
                api.create_favorite(id=tweet.id_str)
            except Exception as e:
                print(str(e))



            message = random.choice(tweets)
            url = str("https://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id_str)
            print(url)
            re = api.update_status(message, attachment_url=url)
            print("转推结果：" + str(re.is_quote_status))
            #把本条推文添加在库里面
            twitterBot = TwitterBot(
                screen_name=tweet.user.screen_name,
                url=url,
                tweet_id=tweet.id)
            print(tweet.id)
            session.add(twitterBot)
            session.commit()
        #过5分钟再来搞下一条
            print("time.sleep(300) start time=" + str(datetime.utcnow()))
            time.sleep(300)
#整个循环结束了，过5分钟再重新来
    print("time.sleep(300) start time=" + str(datetime.utcnow()))
    time.sleep(300)
    print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")

