"""
Test tweeting about beer.

Doesn't test the most important rule: never tweet.
"""

from unittest.mock import patch

from django.test import TestCase
from celery import Task
from celery.exceptions import Retry

from beers.models import Beer
from beers.test.factories import BeerFactory, ManufacturerFactory
from taps.models import Tap
from taps.test.factories import TapFactory
from venues.test.factories import VenueFactory
from tap_list_providers.tasks import (
    tweet_about_beers, SINGLE_BEER_TEMPLATE, MULTI_BEER_INNER, MULTI_BEER_OUTER,
)


class TweetTestCase(TestCase):

    def setUp(self):
        self.venue = VenueFactory()
        self.api_key = '12345'
        self.api_secret = '23456'
        self.consumer_key = '32sdfasd'
        self.consumer_secret = 'sgbbdabd'

    def settings_context_manager(self):
        return self.settings(
            TWITTER_CONSUMER_KEY=self.consumer_key,
            TWITTER_CONSUMER_SECRET=self.consumer_secret,
            TWITTER_ACCESS_TOKEN_KEY=self.api_key,
            TWITTER_ACCESS_TOKEN_SECRET=self.api_secret,
        )

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_single_beer(self, mock_retry, mock_api):
        beer = BeerFactory()
        TapFactory(venue=self.venue, beer=beer)
        with self.settings_context_manager():
            tweet_about_beers([beer.id])
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdate.assert_called_once_with(
            SINGLE_BEER_TEMPLATE.format(
                beer.name,
                '@' + beer.manufacturer.twitter_handle,
                beer.style.name,
                self.venue.name,
            )
        )
        mock_api.return_value.PostUpdates.assert_not_called()

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_single_beer_no_twitter(self, mock_retry, mock_api):
        beer = BeerFactory()
        beer.manufacturer.twitter_handle = ''
        beer.manufacturer.save()
        TapFactory(venue=self.venue, beer=beer)
        with self.settings_context_manager():
            tweet_about_beers([beer.id])
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdate.assert_called_once_with(
            SINGLE_BEER_TEMPLATE.format(
                beer.name,
                beer.manufacturer.name,
                beer.style.name,
                self.venue.name,
            )
        )
        mock_api.return_value.PostUpdates.assert_not_called()

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_single_beer_venue_twitter(self, mock_retry, mock_api):
        beer = BeerFactory()
        self.venue.twitter_handle = 'gsdgsdgasvas'
        self.venue.save()
        TapFactory(venue=self.venue, beer=beer)
        with self.settings_context_manager():
            tweet_about_beers([beer.id])
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdate.assert_called_once_with(
            SINGLE_BEER_TEMPLATE.format(
                beer.name,
                '@' + beer.manufacturer.twitter_handle,
                beer.style.name,
                '@' + self.venue.twitter_handle,
            )
        )
        mock_api.return_value.PostUpdates.assert_not_called()

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_single_beer_already_tweeted(self, mock_retry, mock_api):
        beer = BeerFactory(tweeted_about=True)
        TapFactory(venue=self.venue, beer=beer)
        with self.settings_context_manager():
            tweet_about_beers([beer.id])
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdate.assert_not_called()
        mock_api.return_value.PostUpdates.assert_not_called()

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_single_beer_no_creds(self, mock_retry, mock_api):
        beer = BeerFactory()
        TapFactory(venue=self.venue, beer=beer)
        with self.settings(
            TWITTER_CONSUMER_KEY='',
            TWITTER_CONSUMER_SECRET='',
            TWITTER_ACCESS_TOKEN_KEY='',
            TWITTER_ACCESS_TOKEN_SECRET='',
        ):
            tweet_about_beers([beer.id])
        mock_retry.assert_not_called()
        mock_api.assert_not_called()

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_multi_beer(self, mock_retry, mock_api):
        mfg = ManufacturerFactory()
        beers = Beer.objects.bulk_create(
            BeerFactory.build(manufacturer=mfg, style=None) for dummy in range(10)
        )
        Tap.objects.bulk_create(
            TapFactory.build(venue=self.venue, beer=beer)
            for beer in beers
        )
        with self.settings_context_manager():
            tweet_about_beers([i.id for i in beers])
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdates.assert_called_once()
        mock_api.return_value.PostUpdate.assert_not_called()
        call_args = mock_api.return_value.PostUpdates.call_args
        self.assertEqual(call_args[1], {'continuation': '…', 'threaded': True})
        self.assertEqual(len(call_args[0]), 1)
        tweet = call_args[0][0]
        self.assertIn(
            MULTI_BEER_OUTER.format(len(beers), '').strip(),
            tweet,
        )
        lines = tweet.splitlines()
        self.assertEqual(len(lines), 1 + len(beers))
        for beer, line in zip(beers, lines[1:]):
            self.assertIn(MULTI_BEER_INNER.format(
                beer.name,
                '@' + beer.manufacturer.twitter_handle,
                'unknown',
                self.venue.name,
            ), line)

    @patch('tap_list_providers.tasks.ThreadedApi')
    @patch.object(Task, 'retry')
    def test_multi_beer_more_to_come(self, mock_retry, mock_api):
        mfg = ManufacturerFactory()
        beers = Beer.objects.bulk_create(
            BeerFactory.build(manufacturer=mfg, style=None) for dummy in range(20)
        )
        Tap.objects.bulk_create(
            TapFactory.build(venue=self.venue, beer=beer)
            for beer in beers
        )
        with self.settings_context_manager():
            tweet_about_beers([i.id for i in beers])
        beers = beers[:10]
        mock_retry.assert_not_called()
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )
        mock_api.return_value.PostUpdates.assert_called_once()
        mock_api.return_value.PostUpdate.assert_not_called()
        call_args = mock_api.return_value.PostUpdates.call_args
        self.assertEqual(call_args[1], {'continuation': '…', 'threaded': True})
        self.assertEqual(len(call_args[0]), 1)
        tweet = call_args[0][0]
        self.assertIn(
            MULTI_BEER_OUTER.format(len(beers), '(10 still to come!)').strip(),
            tweet,
        )
        lines = tweet.splitlines()
        self.assertEqual(len(lines), 1 + len(beers))
        for beer, line in zip(beers, lines[1:]):
            self.assertIn(MULTI_BEER_INNER.format(
                beer.name,
                '@' + beer.manufacturer.twitter_handle,
                'unknown',
                self.venue.name,
            ), line)

    @patch('tap_list_providers.tasks.ThreadedApi')
    def test_beer_not_found_yet(self, mock_api):
        beer_pks = [1234, 5678]
        with self.settings_context_manager():
            with self.assertRaises(Retry):
                tweet_about_beers(beer_pks)
        mock_api.assert_called_once_with(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.api_key,
            access_token_secret=self.api_secret,
        )