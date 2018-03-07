from json import JSONDecodeError

import requests as req
import tweepy as tw
import pandas as pd
import json
import os.path
from tweepy import TweepError

from props import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET, USER, FILE_PATH, JSON_TWITS, \
    PREDICT_FILE_URL, DOWNLOADED_FILE_NAME


def authenticate():
    auth = tw.OAuthHandler(consumer_key=CONSUMER_KEY,
                           consumer_secret=CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tw.API(auth, wait_on_rate_limit=True, parser=tw.parsers.JSONParser(), wait_on_rate_limit_notify=True)
    return api


class Storage:
    archive_df = None
    twitter_df = None
    recognition_df = None


class Command:
    def execute(self): pass


class LoadArchive(Command):
    @classmethod
    def load_data(cls, file_path, sep=','):
        try:
            df = pd.read_csv(file_path, sep=sep)
        except FileNotFoundError:
            print("File not found")
            df = None
        return df

    @classmethod
    def id_feature_to_str(cls, df):
        df[
            ["tweet_id",
             "in_reply_to_status_id",
             "in_reply_to_user_id",
             "retweeted_status_id",
             "retweeted_status_user_id"]
        ] = df[
            ["tweet_id",
             "in_reply_to_status_id",
             "in_reply_to_user_id",
             "retweeted_status_id",
             "retweeted_status_user_id"]
        ].astype(str)

    @classmethod
    def execute(cls):
        Storage.archive_df = cls.load_data(FILE_PATH)
        cls.id_feature_to_str(Storage.archive_df)


class GetTwitterData(Command):
    @classmethod
    def response_to_file(cls, file_name=JSON_TWITS, ids=None):
        if os.path.isfile(JSON_TWITS):
            return
        if ids is None:
            ids = Storage.archive_df.tweet_id
        api = authenticate()
        with open(file_name, 'a') as f:
            for iid in ids:
                try:
                    res = api.get_status(iid, tweet_mode='extended')
                    json.dump(res, f)
                    f.write('\n')
                except TweepError:
                    f.writelines(iid + " not result \n")

    @classmethod
    def file_to_df(cls, file_name=JSON_TWITS):
        lines = []
        with open(file_name, 'r', encoding='utf-8') as f:
            for l in f:
                try:
                    lines.append(json.loads(l, encoding='utf-8'))
                except JSONDecodeError:
                    print(l)
        return pd.DataFrame(lines).reset_index(level=0)

    @classmethod
    def execute(cls):
        cls.response_to_file()
        Storage.twitter_df = cls.file_to_df()


class Gather(Command):
    @classmethod
    def download_file(cls, file_url=PREDICT_FILE_URL):
        if os.path.isfile(DOWNLOADED_FILE_NAME):
            return
        res = req.get(file_url)
        with open(DOWNLOADED_FILE_NAME, "wb") as f:
            f.write(res.content)

    @classmethod
    def execute(cls):
        cls.download_file()
        Storage.recognition_df = LoadArchive.load_data(file_path=DOWNLOADED_FILE_NAME, sep='\t')


commands = [LoadArchive(), Gather(), GetTwitterData()]

for command in commands:
    command.execute()

