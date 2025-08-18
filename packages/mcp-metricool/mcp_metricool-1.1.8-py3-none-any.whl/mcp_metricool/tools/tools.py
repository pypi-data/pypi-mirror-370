import json
from typing import Any, List, Dict

from mcp.server.fastmcp import FastMCP

from mcp_metricool.utils.utils import make_get_request
from mcp_metricool.utils.utils import make_post_request
from mcp_metricool.utils.utils import make_put_request
from mcp_metricool.utils.utils import network_subject_metrics
from ..config import METRICOOL_BASE_URL
from ..config import METRICOOL_USER_ID
from datetime import datetime
from urllib.parse import unquote, quote
from pytz import timezone

# Initialize FastMCP server
mcp = FastMCP("metricool")


@mcp.tool()
async def get_brands() -> list[dict[str, Any]]:
    """
    Get the list of brands from your Metricool account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/settings/brands?userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)
    if not response:
        return ("Failed to get brands")
    result = []
    dicts = response["data"]
    for item in dicts:
        simplified = {
            "label": item.get("label"),
            "id": item.get("id"),
            "userId": item.get("userId"),
            "networks": item.get("networksData"),
            "timezone": item.get("timezone")
        }
        result.append(simplified)
    return result

@mcp.tool()
async def get_brands_complete() -> str | dict[str, Any]:
    """
    Get the list of brands from your Metricool account. Only use this tool if the user asks specifically for his brands, in every other case
    use get_brands.
    Add to the result that the only networks with competitors are Instagram, Facebook, Twitch, YouTube, Twitter, and Bluesky.
    """

    url = f"{METRICOOL_BASE_URL}/v2/settings/brands?userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get brands")

    return {
    "brands": response,
    "instructions": (
        "Explain that only Instagram, Facebook, Twitch, YouTube, Twitter, and Bluesky support competitors. "
    )
}

@mcp.tool()
async def get_instagram_reels(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Instagram Reels from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/reels/instagram?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Instagram Reels")

    return response

@mcp.tool()
async def get_instagram_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Instagram Posts from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/instagram?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Instagram Posts")

    return response

@mcp.tool()
async def get_instagram_stories(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Instagram Stories from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/stories/instagram?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Instagram Stories")

    return response

@mcp.tool()
async def get_tiktok_videos(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Tiktok Videos from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/tiktok?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Tiktok Videos")

    return response

@mcp.tool()
async def get_facebook_reels(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Facebook Reels from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/reels/facebook?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Facebook Reels")

    return response

@mcp.tool()
async def get_facebook_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Facebook Posts from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/facebook?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Facebook Posts")

    return response

@mcp.tool()
async def get_facebook_stories(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Facebook Stories from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/stories/facebook?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Facebook Stories")

    return response

@mcp.tool()
async def get_thread_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Threads Posts from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/threads?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Threads Posts")

    return response

@mcp.tool()
async def get_x_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of X (Twitter) Posts from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYYMMDD
     end date: End date of the period to get the data. The format is YYYYMMDD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/stats/twitter/posts?start={init_date}&end={end_date}&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get X Posts")

    return response

@mcp.tool()
async def get_bluesky_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Bluesky Posts from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/bluesky?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Bluesky Posts")

    return response

@mcp.tool()
async def get_linkedin_posts(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Linkedin Posts from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/linkedin?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Linkedin Posts")

    return response

@mcp.tool()
async def get_pinterest_pins(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Pinterest Pins from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/pinterest?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Pinterest Pins")

    return response

@mcp.tool()
async def get_youtube_videos(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Youtube Videos from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/posts/youtube?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Youtube Videos")

    return response

@mcp.tool()
async def get_twitch_videos(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Twitch Videos from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYYMMDD
     end date: End date of the period to get the data. The format is YYYYMMDD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/stats/twitch/videos?start={init_date}&end={end_date}&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Twitch Videos")

    return response

@mcp.tool()
async def get_facebookads_campaigns(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Facebook Ads Campaigns from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYYMMDD
     end date: End date of the period to get the data. The format is YYYYMMDD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/stats/facebookads/campaigns?start={init_date}&end={end_date}&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Facebook Ads Campaigns")

    return response

@mcp.tool()
async def get_googleads_campaigns(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Google Ads Campaigns from your Metricool account.

    Args:
     init date: Init date of the period to get the data. The format is YYYYMMDD
     end date: End date of the period to get the data. The format is YYYYMMDD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/stats/adwords/campaigns?start={init_date}&end={end_date}&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Google Ads Campaigns")

    return response

@mcp.tool()
async def get_tiktokads_campaigns(init_date: str, end_date: str, blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Tiktok Ads Campaigns from your Metricool brand account.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/campaigns/tiktokads?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get Tiktok Ads Campaigns")

    return response

@mcp.tool()
async def get_network_competitors(network: str, init_date: str, end_date: str, blog_id: int, limit: int, timezone: str) -> str | dict[str, Any]:
    """
    Get the list of your competitors from your Metricool brand account.
    Add interesting conclusions for my brand about my competitors.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     network: Network to retrieve the competitors. The format is "twitter", "facebook", "instagram", "youtube", "twitch" and "bluesky". Only these are accepted.
     blog id: Blog id of the Metricool brand account.
     limit: Limit of competitors. By default = 10
     timezone: Timezone of the post. The format is "Europe%2FMadrid".  Use the timezone of the user extracted from the get_brands tool.
    """

    url = f"{METRICOOL_BASE_URL}/v2/analytics/competitors/{network}?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&limit={limit}&timezone={timezone}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get competitors")

    return response

@mcp.tool()
async def get_network_competitors_posts(network: str, init_date: str, end_date: str, blog_id: int, limit: int, timezone: str) -> str | dict[str, Any]:
    """
    Get the list of posts from your competitors from your Metricool brand account.
    Add interesting conclusions for my brand about my competitors and analyze their posts.

    Args:
     init date: Init date of the period to get the data. The format is YYYY-MM-DD
     end date: End date of the period to get the data. The format is YYYY-MM-DD
     network: Network to retrieve the posts. The format is "twitter", "facebook", "instagram", "youtube", "twitch" and "bluesky". Only these are accepted.
     blog id: Blog id of the Metricool brand account.
     limit: Limit of posts of competitors. By default = 50
     timezone: Timezone of the post. The format is "Europe%2FMadrid".  Use the timezone of the user extracted from the get_brands tool.
    """
    if(network=="instagram"):
        url = f"{METRICOOL_BASE_URL}/v2/analytics/competitors/{network}/publications?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&limit={limit}&timezone={timezone}&integrationSource=MCP"
        response_pub = await make_get_request(url)
        url = f"{METRICOOL_BASE_URL}/v2/analytics/competitors/{network}/publications?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&limit={limit}&timezone={timezone}&integrationSource=MCP"
        response_reels = await make_get_request(url)
        response={"publications":response_pub, "reels":response_reels}
    else:
        url = f"{METRICOOL_BASE_URL}/v2/analytics/competitors/{network}/posts?from={init_date}T00%3A00%3A00&to={end_date}T23%3A59%3A59&blogId={blog_id}&userId={METRICOOL_USER_ID}&limit={limit}&timezone={timezone}&integrationSource=MCP"

        response = await make_get_request(url)

    if not response:
        return ("Failed to get competitors")

    return response

@mcp.tool()
async def get_pinterest_boards(blog_id: int) -> str | dict[str, Any]:
    """
    Get the list of Pinterest boards for a specific Metricool brand (blog_id).
    If the user doesn't provide a blog_id, ask for it.

    Args:
     blog_id: Blog id of the Metricool brand account.
    """
    url = f"{METRICOOL_BASE_URL}/v2/scheduler/boards/pinterest?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return "Failed to get pinterest boards"

    return response

@mcp.tool()
async def post_schedule_post(date:str, blog_id: int, info: json) -> str | dict[str, Any]:
    """
    Schedule a post to Metricool at a specific date and time.
    To be able to schedule the post, you need to maintain the structure.
    You can use the tool get_best_time_to_post to get the best time to post for a specific provider if the user doesn't specify the time to post.
    If the post include Instagram, is a must to have at least one image or video. Posts must include an image or a carousel, Reels must include a video, and Stories can include either an image or a video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Pinterest, is a must to have a image and the board where to publish the pin. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Youtube, is a must to have a video, select the audience (if it's video made for kids or not) and the title of the video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Tiktok, is a must to have at least one image or video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post is Facebook Reel, is a must to have a video. If is Facebook Story, image or video is needed. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post is Bluesky, make sure the text does not exceed 300 characters. If the content exceeds that limit, do not retry and return an error informing the user: "Error: The text exceeds the 300-character limit allowed on Bluesky. Please edit it."
    If the post is for X (formerly Twitter), make sure before posting that the text does not exceed 280 characters. You must NOT split the message into multiple tweets or threads, the message must be evaluated strictly against a 280-character limit. If the text exceeds 280 characters, do not retry and return only the following error message and stop processing:
    "Error: The text exceeds the 280-character limit allowed on X. Please edit it."
    The date can't be in the past.
    DO NOT modify the text if there's any error, just notify the user.

    Args:
     date: Date and time to publish the post. The format is YYYY-MM-DDT00:00:00
     blog id: Blog id of the Metricool brand account.
     info: Data of the post to be scheduled. Should be a json object with the following fields:
        autoPublish: True or False, default is True.
        descendants: list with the args of the other posts if it is a thread with the format [args of the second post, args of the third post,...  ], default is empty list if there is no thread.
        draft: True or False, default is False.
        firstCommentText: Text of the first comment of the post. Default ""
        hasNotReadNotes: True or False, default is False.
        media: default is empty list.
        mediaAltText: default is empty list.
        providers: always need at least one provider with the format [{"network":"<string>"}]. Use "twitter" for X posts.
        publicationDate: Date and timezone of the post. The format is {dateTime:"YYYY-MM-DDT00:00:00", timezone:"Europe/Madrid"}. Use the timezone of the user extracted from the get_brands tool.
        shortener: True or False, default is False.
        smartLinkData: default is {ids:[]}
        text: Text of the post.
        Always you need to add the networkData for the posts, as empty if you don't have more information. Only include the networkData for the networks you have in the providers list.
            The format is "twitterData": {"tags":[]}, Tags is used for tagging people on the images of the post, not hashtags.
                            "facebookData": {"type":"<string>", "title":"<string>", "boost":<double>, "boostPayer":"<string>", "boostBeneficiary":"<string>"},
                                Facebook type can be "POST", "REEL" or "STORY"
                                Facebook title is only available for Facebook videos (This is separate from the main text of the post).
                                Facebook boost, boostPayer, and boostBeneficiary are only included if they are promoted posts.
                            "instagramData": {"type": "<string>" (default = POST), "collaborators":[{username: "string", deleted: false}]], "showReelOnFeed": "<boolean>" (default = true), "boost":<double>, "boostPayer":"<string>", "boostBeneficiary":"<string>"},
                                Instagram type can be "POST", "REEL" or "STORY".
                                There could be more than one collaborator, following the same structure.
                            "linkedinData": {"documentTitle": "<string>", "publishImagesAsPDF": "<boolean>" (default = false), "previewIncluded": "<boolean>" (default = true), "type": "<string>" (default = post), "poll": {"question": "<string>", "options": [{"text": "<string>"}, {"text": "<string>"}], "settings": {"duration": "<string>"}}},
                                Linkedin type can be "post" or "poll".
                                If there is a documentTitle in Linkedin, publishImagesAsPDF must be true.
                                Linkedin poll duration can be "ONE_DAY", "THREE_DAYS", "SEVEN_DAYS " or "FOURTEEN_DAYS ".
                            "pinterestData": {"boardId":"<string>", "pinTitle":"<string>","pinLink":"<string>", "pinNewFormat":"<boolean>"},
                            "youtubeData": {"title": "<string>", "type": "<string>" (default = video), "privacy": "<string>" (default = public), "tags": [ "<string>", "<string>" ], "category": "<string>" (optional field), "madeForKids": "<boolean>"},
                                Youtube type can be "video" or "short" and privacy can be "public", "unlisted" or "private".
                                Youtube category can be FILM_ANIMATION, AUTOS_VEHICLES, MUSIC, PETS_ANIMALS, SPORTS, TRAVEL_EVENTS, GAMING, PEOPLE_BLOGS, COMEDY, ENTERTAINMENT, NEWS_POLITICS, HOWTO_STYLE, EDUCATION, SCIENCE_TECHNOLOGY, NONPROFITS_ACTIVISM.
                            "twitchData": {"autoPublish":"<boolean>", "tags":[]},
                            "tiktokData": {"disableComment": "<boolean>" (default = false), "disableDuet": "<boolean>" (default = false), "disableStitch": "<boolean>" (default = false), "privacyOption": "<string>" (default = "PUBLIC_TO_EVERYONE"), "commercialContentThirdParty": "<boolean>" (default = false), "commercialContentOwnBrand": "<boolean>" (default = false), "title": "<string>", "autoAddMusic": "<boolean>" (default = false), "photoCoverIndex": "<integer>" (default = 0)},
                                Tiktok privacyOption can be "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR" or "SELF_ONLY".
                            "blueskyData": {"postLanguages":["",""]},
                            "threadsData":{"allowedCountryCodes:["",""]}
        The other fields are optional, but you need to add the ones you have. If you don't have more information, you can ask the user about it and wait until you have the information.

    """

    for provider in info.get("providers", []):
        network = provider.get("network")
        text = info.get("text", "")

        if network == "twitter" and len(text) > 280:
            return "Error: The text exceeds the 280-character limit allowed on X. Please edit it and try again."
        if network == "bluesky" and len(text) > 300:
            return "Error: The text exceeds the 300-character limit allowed on Bluesky. Please edit it and try again."
    url = f"{METRICOOL_BASE_URL}/v2/scheduler/posts?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_post_request(url, data=json.dumps(info))

    if not response:
        return ("Failed to schedule the post")

    return response


@mcp.tool()
async def get_scheduled_posts(blog_id: int, start: str, end: str, timezone: str, extendedRange: bool) -> str | dict[str, Any]:
    """
    Get the list of scheduled posts for a specific Metricool brand (blog_id).
    Only retrieves posts that are scheduled (not yet published).
    If the user doesn't provide a blog_id, ask for it.

    Args:
     blog_id: Blog id of the Metricool brand account.
     start: Start date of the period to get the data. The format is YYYY-MM-DD
     end: End date of the period to get the data. The format is YYYY-MM-DD
     timezone: Timezone of the post. The format is "Europe%2FMadrid".  Use the timezone of the user extracted from the get_brands tool.
     extendedRange: When it's true, search date range is expanded one day after and one day before. Default value is false.
    """
    url = f"{METRICOOL_BASE_URL}/v2/scheduler/posts?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP&start={start}T00%3A00%3A00&end={end}T23%3A59%3A59&timezone={timezone}&extendedRange={extendedRange}"

    response = await make_get_request(url)

    if not response:
        return "Failed to get scheduled posts"

    return response

@mcp.tool()
async def get_best_time_to_post(start: str, end: str, blog_id: int, provider: str, timezone: str) -> str | dict[
    str, Any]:
    """
    Get the best time to post for a specific provider. The return is a list of hours and days with a value. The higher the value, the best time to post.
    Try to get the best for as maximum of 1 week. If you have day to publish but not hours, choose the start and end of this day.
    Args:
     start: Start date of the period to get the data. The format is YYYY-MM-DD
     end: End date of the period to get the data. The format is YYYY-MM-DD
     blog id: Blog id of the Metricool brand account.
     provider: Provider of the post. The format is "twitter", "facebook", "instagram", "linkedin", "youtube", "tiktok". Only these are accepted.
     timezone: Timezone of the post. The format is "Europe%2FMadrid".  Use the timezone of the user extracted from the get_brands tool.
    """

    days_of_week = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday"
    }

    url = f"{METRICOOL_BASE_URL}/v2/scheduler/besttimes/{provider}?start={start}T00%3A00%3A00&end={end}T23%3A59%3A59&timezone={timezone}&blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_get_request(url)

    if not response:
        return ("Failed to get the best time to post")

    #Introducir día de la semana
    for entry in response["data"]:
        day_number = entry.get("dayOfWeek")
        entry["dayOfWeekName"] = days_of_week.get(day_number, "Unknown")

    return response

@mcp.tool()
async def update_schedule_post(id: str, date:str, blog_id: int, info: json) -> str | dict[str, Any]:
    """
    Update a scheduled post in Metricool. You need the id of the post to update. Get it from the get_scheduled_posts tool previous on the conversation.
    Ask the user if they're sure they want to modify the post, including what will be changed, and require them to confirm.
    Do not retry if there is a problem.
    To update the post, ensure the full original content is included in the request, modifying only the new information while keeping the rest unchanged and maintaining the original structure.
    If the post include Instagram, is a must to have at least one image or video. Posts must include an image or a carousel, Reels must include a video, and Stories can include either an image or a video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Pinterest, is a must to have a image and the board where to publish the pin. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Youtube, is a must to have a video, select the audience (if it's video made for kids or not) and the title of the video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post include Tiktok, is a must to have at least one image or video. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post is Facebook Reel, is a must to have a video. If is Facebook Story, image or video is needed. If you don't have more information, you can ask the user about it and wait until you have the information.
    If the post is Bluesky, make sure the text does not exceed 300 characters. If the content exceeds that limit, do not retry and return an error informing the user: "Error: The text exceeds the 300-character limit allowed on Bluesky. Please edit it."
    If the post is for X (formerly Twitter), make sure before posting that the text does not exceed 280 characters. You must NOT split the message into multiple tweets or threads, the message must be evaluated strictly against a 280-character limit. If the text exceeds 280 characters, do not retry and return only the following error message and stop processing:

    The date can't be in the past.

    Args:
     date: Date and time to publish the post. The format is YYYY-MM-DDT00:00:00
     id: id of the post to update. Get it from the get_scheduled_posts tool previous on the conversation.
     blog id: Blog id of the Metricool brand account.
     info: Data of the post to be scheduled. Should be a json object with the following fields:
        id: id of the post to update. Get it from the get_scheduled_posts tool previous on the conversation. The format is "id":<integer>
        uuid: uuid of the post to update. Get it from the get_scheduled_posts tool previous on the conversation. The format is "uuid":"<string>"
        autoPublish: True or False, default is True.
        descendants: list with the args of the other posts if it is a thread with the format [args of the second post, args of the third post,...  ], default is empty list if there is no thread.
        draft: True or False, default is False.
        firstCommentText: Text of the first comment of the post. Default ""
        hasNotReadNotes: True or False, default is False.
        media: default is empty list.
        mediaAltText: default is empty list.
        providers: always need at least one provider with the format [{"network":"<string>"}]. Use "twitter" for X posts.
        publicationDate: Date and timezone of the post. The format is {dateTime:"2025-01-01T00:00:00", timezone:"Europe/Madrid"}
        shortener: True or False, default is False.
        smartLinkData: default is {ids:[]}
        text: Text of the post.
        Always you need to add the networkData for the posts, as empty if you don't have more information. Only include the networkData for the networks you have in the providers list.
            The format is "twitterData": {"tags":[]}, Tags is used for tagging people on the images of the post, not hashtags.
                            "facebookData": {"type":"<string>", "title":"<string>", "boost":<double>, "boostPayer":"<string>", "boostBeneficiary":"<string>"},
                                Facebook type can be "POST", "REEL" or "STORY"
                                Facebook title is only available for Facebook videos (This is separate from the main text of the post).
                                Facebook boost, boostPayer, and boostBeneficiary are only included if they are promoted posts.
                            "instagramData": {"type": "<string>" (default = POST), "collaborators":[{username: "string", deleted: false}]], "carouselTags":{"<number>":[{"username":"<string>","x":<double>,"y":<double>}]} (number is the index of the image within the carousel), "showReelOnFeed": "<boolean>" (default = true), "boost":<double>, "boostPayer":"<string>", "boostBeneficiary":"<string>"},
                                Instagram type can be "POST", "REEL" or "STORY".
                                There could be more than one collaborator, following the same structure.
                                The carouselTags is a dictionary with the number of the image in the carousel as key and a list of tags for that image.
                            "linkedinData": {"documentTitle": "<string>", "publishImagesAsPDF": "<boolean>" (default = false), "previewIncluded": "<boolean>" (default = true), "type": "<string>" (default = post), "poll": {"question": "<string>", "options": [{"text": "<string>"}, {"text": "<string>"}], "settings": {"duration": "<string>"}}},
                                Linkedin type can be "post" or "poll".
                                If there is a documentTitle in Linkedin, publishImagesAsPDF must be true.
                                Linkedin poll duration can be "ONE_DAY", "THREE_DAYS", "SEVEN_DAYS " or "FOURTEEN_DAYS ".
                            "pinterestData": {"boardId":"<string>", "pinTitle":"<string>","pinLink":"<string>", "pinNewFormat":"<boolean>"},
                            "youtubeData": {"title": "<string>", "type": "<string>" (default = video), "privacy": "<string>" (default = public), "tags": [ "<string>", "<string>" ], "category": "<string>" (optional field), "madeForKids": "<boolean>"},
                                Youtube type can be "video" or "short" and privacy can be "public", "unlisted" or "private".
                                Youtube category can be FILM_ANIMATION, AUTOS_VEHICLES, MUSIC, PETS_ANIMALS, SPORTS, TRAVEL_EVENTS, GAMING, PEOPLE_BLOGS, COMEDY, ENTERTAINMENT, NEWS_POLITICS, HOWTO_STYLE, EDUCATION, SCIENCE_TECHNOLOGY, NONPROFITS_ACTIVISM.
                            "twitchData": {"autoPublish":"<boolean>", "tags":[]},
                            "tiktokData": {"disableComment": "<boolean>" (default = false), "disableDuet": "<boolean>" (default = false), "disableStitch": "<boolean>" (default = false), "privacyOption": "<string>" (default = "PUBLIC_TO_EVERYONE"), "commercialContentThirdParty": "<boolean>" (default = false), "commercialContentOwnBrand": "<boolean>" (default = false), "title": "<string>", "autoAddMusic": "<boolean>" (default = false), "photoCoverIndex": "<integer>" (default = 0)},
                                Tiktok privacyOption can be "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR" or "SELF_ONLY".
                            "blueskyData": {"postLanguages":["",""]},
                            "threadsData":{"allowedCountryCodes:["",""]}
    """

    url = f"{METRICOOL_BASE_URL}/v2/scheduler/posts/{id}?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"

    response = await make_put_request(url, data=json.dumps(info))

    if not response:
        return ("Failed to update the post")

    return response



@mcp.tool()
async def get_metrics(network: str) -> str | dict[str, Any]:
    """
    Retrieve the available metrics for a specific network.
    Args:
        network: Specific network to get the available metrics.
    """
    if network not in network_subject_metrics:
        return f"Incorrect network '{network}'. The available networks are: {', '.join(network_subject_metrics.keys())}"
    else:
        metrics = {}
        subjects = list(network_subject_metrics[network].keys())
        for subj in subjects:
            metrics[subj] = network_subject_metrics[network][subj]
        return {"metrics": metrics,
                "instructions": "Stop the chat, show the metrics and let the user choose the metrics they want to analyze before going again to get_analytics, the user must choose before you continue."}


@mcp.tool()
async def get_analytics(blog_id: int, start: str, end: str, timezone: str, network: str, metric: [str]) -> str | dict[str, Any]:

    """
    Retrieve analytics data for a specific Metricool brand. If the user does not specify any metric you can use the
    get_metrics tool and let the user decide them.

    Args:
        - blog_id (int): ID of the Metricool brand account. Required.
        - start (str): Start date of the data period (format: YYYY-MM-DD). Required.
        - end (str): End date of the data period (format: YYYY-MM-DD). Required.
        - timezone (str): Timezone from the brand(e.g., Europe%2FMadrid). Required. If you don't have the timezone you can obtain it from the get_brands tool
        - network (str): Social network to analyze (e.g., facebook, instagram, linkedin, youtube, tiktok, etc.), it must be connected to the brand. Required.
        - metric ([str]): List of metrics, default is empty.
        If blog_id is missing, ask the user to provide it.
        If network is missing, ask the user to specify one.
        If network is not connected to the brand, ask the user to specify one of the connected ones.
"""

    if network not in network_subject_metrics:
        return f"Incorrect network '{network}'. The available networks are: {', '.join(network_subject_metrics.keys())}"
    if not metric:
        return "Please provide a list of metrics. You can use the 'get_metrics' tool to explore available metrics."

    results = {}


    subjects = list(network_subject_metrics[network].keys())
    start_formatted = format_datetime_with_timezone(start, "00:00:00", timezone)
    end_formatted = format_datetime_with_timezone(end, "23:59:59", timezone)
    start_aux = start.replace("-", "")
    end_aux = end.replace("-", "")
    for subj in subjects:
        metrics = metric if metric else network_subject_metrics[network][subj]
        for met in metrics:
            if met not in network_subject_metrics[network][subj]:
                continue
            if network == 'tiktok' and subj == 'videos':
                url = (
                f"{METRICOOL_BASE_URL}/v2/analytics/timelines"
                f"?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"
                f"&from={start_formatted}&to={end_formatted}"
                f"&timezone={timezone}&metric={met}&network={network}"
                )
            elif network == 'youtube' and subj == 'videos':
                url = (
                    f"{METRICOOL_BASE_URL}/v2/analytics/timelines"
                    f"?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"
                    f"&from={start_formatted}&to={end_formatted}"
                    f"&timezone={timezone}&metric={met}&network={network}&postsType=publishedInRange"
                )
            elif network == 'youtube' and subj == "account":
                url = (
                    f"https://app.metricool.com/api/stats/timeline/{met}?start={start_aux}&end={end_aux}&timezone={timezone}"
                    f"&userId={METRICOOL_USER_ID}&blogId={blog_id}&integrationSource=MCP"
                )
            elif network == "linkedin" and subj != "stories":
                url = (
                    f"{METRICOOL_BASE_URL}/v2/analytics/timelines"
                    f"?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"
                    f"&from={start_formatted}&to={end_formatted}"
                    f"&timezone={timezone}&metric={met}&metricType={subj}&network={network}"
                )
            elif network == "linkedin" and subj == "stories":
                url = (
                    f"https://app.metricool.com/api/stats/timeline/{met}"
                    f"?start={start_aux}&end={end_aux}&userId={METRICOOL_USER_ID}&blogId={blog_id}&integrationSource=MCP"
                )
            elif network == "webpage":
                url = (
                    f"https://app.metricool.com/api/stats/timeline/{met}"
                    f"?start={start_aux}&end={end_aux}&userId={METRICOOL_USER_ID}&blogId={blog_id}&timezone={timezone}&integrationSource=MCP"
                )
            elif network == "twitter":
                url = (
                    f"https://app.metricool.com/api/stats/timeline/{met}"
                    f"?start={start_aux}&end={end_aux}&userId={METRICOOL_USER_ID}&blogId={blog_id}&timezone={timezone}&integrationSource=MCP"
                )
            elif network == "twitch":
                url = (
                    f"https://app.metricool.com/api/stats/timeline/twitch{met}"
                    f"?start={start_aux}&end={end_aux}&userId={METRICOOL_USER_ID}&blogId={blog_id}&timezone={timezone}&integrationSource=MCP"
                )
            else:
                url = (
                f"{METRICOOL_BASE_URL}/v2/analytics/timelines"
                f"?blogId={blog_id}&userId={METRICOOL_USER_ID}&integrationSource=MCP"
                f"&from={start_formatted}&to={end_formatted}"
                f"&timezone={timezone}&metric={met}&subject={subj}&network={network}"
                )
            try:
                result = await make_get_request(url)
                if result:
                    results[f"{subj}:{met}"] = result
                else:
                    results[f"{subj}:{met}"] = "No data"
            except Exception as e:
                results[f"{subj}:{met}"] = f"Error: {str(e)}"

            for key, value in results.items():
                if isinstance(value, dict) and "data" in value:
                    for item in value["data"]:
                        if isinstance(item, dict) and "values" in item:
                            for v in item["values"]:
                                if "dateTime" in v:
                                    v["dateTime"] = convert_datetime_to_timezone(v["dateTime"], unquote(timezone))

    return results if results else "No valid data."

def format_datetime_with_timezone(date_str: str, hour: str, timezone_str: str) -> str:
    tz_clean = unquote(timezone_str)
    tz = timezone(tz_clean)
    dt = datetime.strptime(f"{date_str}T{hour}", "%Y-%m-%dT%H:%M:%S")
    final_dt = tz.localize(dt)
    return quote(final_dt.isoformat())

def convert_datetime_to_timezone(dt_str: str, target_tz_str: str) -> str:
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
        target_tz = timezone(target_tz_str)
        dt_converted = dt.astimezone(target_tz)
        return dt_converted.isoformat()
    except Exception as e:
        return dt_str

