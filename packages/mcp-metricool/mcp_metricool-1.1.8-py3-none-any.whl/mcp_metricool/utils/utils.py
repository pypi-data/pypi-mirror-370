import json
from typing import Any

import httpx

from ..config import METRICOOL_USER_TOKEN

network_subject_metrics = {
        "tiktok": {
            "videos": [
                "videos", "views", "comments", "shares", "interactions", "likes",
                "reach", "engagement", "impressionSources", "averageVideoViews"
            ],
            "account": [
                "video_views", "profile_views", "followers_count", "followers_delta_count",
                "likes", "comments", "shares"
            ]
        },
        "pinterest": {
            "pins": [
                "impression", "save", "pin_click", "outbound_click", "video_mrc_view",
                "video_avg_watch_time", "video_v50_watch_time", "quartile_95_percent_view", "pins"
            ],
            "account": [
                "followers", "following", "delta followers", "IMPRESSION", "ENGAGEMENT_RATE",
                "ENGAGEMENT", "PIN_CLICK", "OUTBOUND_CLICK", "SAVE"
            ],
            "posts": [
                "PINS"
            ]
        },
        "youtube": {
            "videos": [
                "views", "interactions", "likes", "dislikes", "comments", "shares"
            ],
            "account": [
                "yttotalSubscribers", "ytestimatedRevenue", "ytVideos", "ytsubscribersGained",
                "ytsubscribersLost"
            ]
        },
        "facebook": {
            "stories": [
                "storiesCount"
            ],
            "posts": [
                "count", "interactions", "engagement", "impressionsunique", "impressions",
                "clicks", "comments", "shares", "reactions"
            ],
            "reels": [
                "blue_reels_play_count", "post_impressions_unique", "post_video_likes_by_reaction_type",
                "post_video_social_actions", "engagement", "count"
            ],
            "account": [
                "page_posts_impressions", "page_actions_post_reactions_total", "postsCount", "postsInteractions",
                "likes", "pageFollows", "pageImpressions", "pageImpressions.M", "pageImpressions.F",
                "pageImpressions.U", "pageImpressions.13-17", "pageImpressions.18-24", "pageImpressions.25-34",
                "pageImpressions.35-44", "pageImpressions.45-54", "pageImpressions.55-64",
                "pageImpressions.65+", "pageViews"
            ]
        },
        "gmb": {
            "business": [
                "business_impressions_maps", "business_impressions_search", "business_impressions_total",
                "business_direction_requests", "call_clicks", "website_clicks", "clicks_total",
                "business_conversations", "business_bookings", "business_food_orders", "business_actions_total"
            ]
        },
        "instagram": {
            "account": [
                "email_contacts", "get_directions_clicks", "phone_call_clicks", "text_message_clicks",
                "clicks_total", "postsCount", "postsInteractions", "followers", "friends"
            ],
            "posts": [
                "count", "interactions", "engagement", "reach", "impressions", "likes",
                "comments", "saves", "shares"
            ],
            "reels": [
                "count", "comments", "likes", "saved", "shares", "engagement", "impressions",
                "reach", "interactions", "videoviews"
            ]
        },
        "linkedin": {
            "account": [
                "followers", "paidFollowers", "companyImpressions", "deltaFollowers"
            ],
            "posts": [
                "posts", "clicks", "likes", "comments", "shares", "engagement",
                "impressions", "interactions"
            ],
            "stories": [
                "inStoriesEngagement", "inStoriesInteractions", "inStoriesImpressions",
                "inStoriesCliks", "inStories"
            ]
        },
        "threads": {
            "posts": [
                "count", "views", "likes", "replies", "reposts", "engagement",
                "quotes", "interactions"
            ],
            "account": [
                "followers_count", "delta_followers"
            ]
        },
        "bluesky": {
            "posts": [
                "posts_count", "interactions", "likes", "replies", "reposts", "quotes"
            ],
            "account": [
                "followers_count", "follows_count", "count", "follow_event", "unfollow_event"
            ]
        },
        "webpage": {
            "account": [
                "PageViews", "SessionsCount", "Visitors", "DailyPosts", "DailyComments"
            ]
        },
        "twitter": {
            "account": [
                "twitterFollowers", "twFriends", "twTweets", "follows", "unfollows",
                "twEngagement", "twImpressions", "twInteractions", "twFavorites",
                "twRetweets", "twReplies", "twQuotes", "twProfileClicks",
                "twLinkClicks"
            ]
        },
        "twitch": {
            "account": [
                "TotalFollowers", "TotalSubscribers", "TotalVideos", "DeltaFollowers",
                "TotalTier1", "TotalTier2", "TotalTier3", "TotalGifts", "TotalViews",
                "TotalDuration"

            ]
        }
    }
async def make_get_request(url: str) -> dict[str, Any] | None:
    """Make a get request to the Metricool API with proper error handling."""
    headers = {
        "X-Mc-Auth": METRICOOL_USER_TOKEN,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_post_request(url: str, data: json) -> dict[str, Any] | None:
    """Make a post request to the Metricool API with proper error handling."""
    headers = {
        "X-Mc-Auth": METRICOOL_USER_TOKEN,
        "content-type": "application/json",
        "accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_put_request(url: str, data: json) -> dict[str, Any] | None:
    """Make a put request to the Metricool API with proper error handling."""
    headers = {
        "X-Mc-Auth": METRICOOL_USER_TOKEN,
        "content-type": "application/json",
        "accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, data=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_patch_request(url: str, data: json) -> int | None:
    """Make a patch request to the Metricool API with proper error handling."""
    headers = {
        "X-Mc-Auth": METRICOOL_USER_TOKEN,
        "content-type": "application/json",
        "accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, headers=headers, data=data, timeout=30.0)
            response.raise_for_status()
            return response.status_code
        except Exception:
            return None
