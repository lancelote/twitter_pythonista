from itertools import count

import pytest

from src.main import extract_tweet


class User(object):

    def __init__(self, name):
        self.screen_name = name


class Tweet(object):

    counter = count(0)

    def __init__(self, user, text='', users=None, urls=None):
        if users is None:
            users = []
        if urls is None:
            urls = []

        self.id = next(Tweet.counter)
        self.user = user
        self.text = text

        self.entities = {
            'user_mentions': [{'screen_name': name} for name in users],
            'urls': [{'expanded_url': url} for url in urls]
        }


@pytest.fixture
def full_tweet():
    user = User('user')
    tweet = Tweet(user, 'text', ['user1', 'user2'], ['url1', 'url2', 'url3'])
    return tweet


@pytest.fixture
def empty_tweet():
    user = User('user')
    return Tweet(user)


def test_extract_tweet_returns_correct_result_with_full_tweet(full_tweet):
    expected = ['user', 0, 'text', 'user1,user2', 'url1,url2,url3']
    assert extract_tweet(full_tweet) == expected


def test_extract_tweet_returns_correct_result_with_empty_tweet(empty_tweet):
    expected = ['user', 0, '', '', '']
