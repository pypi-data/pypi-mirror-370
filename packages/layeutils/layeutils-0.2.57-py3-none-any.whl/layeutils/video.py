"""Example
import layeutils.video as util_video
_, channels = util_video.get_playlist_channels_from_m3u('tv_channels_6b1a1759896a_plus.m3u')

target_group_keywords = [
    "US|", "CA|", "UK|", "IE|", "TN|", 
    "NETFLIX DOCU", 
    "AMAZON DOCU", 
    "APPLE+ DOCU",
    "DISCOVERY+", 
    "EN - DOCUMENTARIES"
    ] 
remove_group_keywords = ["SPORT", "NBA", "WNBA", "ESPN", "NHL", "NFL", "FLO","MLB", "GOLF", "TENNIS", "FIFA"] 

filtered_channels = util_video.filter_channel_by_group_keywords(
    includes = target_group_keywords,
    excludes = remove_group_keywords,
    channels = channels,
)

util_video.write_to_m3u_file(filtered_channels,'result-playlist.m3u')

"""
from typing import List

from ipytv.channel import IPTVChannel
from ipytv.playlist import M3UPlaylist


def get_playlist_channels_from_m3u(m3u_path: str) -> tuple[M3UPlaylist, List[IPTVChannel]]:
    """使用ipytv库，从给定路径的m3u文件中获取playlist和所有channel列表

    Args:
        m3u_path (str): _description_

    Returns:
        _type_: _description_
    """
    from ipytv import playlist

    pl: M3UPlaylist = playlist.loadf(m3u_path)
    channels: List[IPTVChannel] = pl.get_channels()
    return pl, channels


def get_unique_group_list(channels: List[IPTVChannel]) -> List[str]:
    """使用ipytv库，从给定的channel列表中获取唯一的group列表

    Args:
        channels (List[IPTVChannel]): _description_

    Returns:
        List[str]: _description_
    """
    groups = []
    for channel in channels:
        if channel.attributes['group-title'] not in groups:
            groups.append(channel.attributes['group-title'])
    return groups


def filter_channel_by_group_keywords(
        includes: List[str],
        excludes: List[str],
        channels: List[IPTVChannel]) -> List[IPTVChannel]:
    """使用ipytv库，根据给定的关键词列表，逐一查询给定的channel对应的group-title属性，过滤出符合条件的频道列表

    Args:
        includes (List[str]): 包含的关键词列表, eg. 
            ["US|", "CA|", "UK|", "IE|", "TN|", 
            "NETFLIX DOCU", 
            "AMAZON DOCU", 
            "APPLE+ DOCU",
            "DISCOVERY+", 
            "EN - DOCUMENTARIES"] 
        excludes (List[str]): 排除的关键词列表, eg. ["SPORT", "NBA", "WNBA", "ESPN", "NHL", "NFL", "FLO","MLB", "GOLF", "TENNIS", "FIFA"] 
        channels (List[IPTVChannel]): 频道列表

    Returns:
        List[IPTVChannel]: 过滤后的频道列表
    """
    filtered_channels = []
    for channel in channels:
        group_title = channel.attributes['group-title']
        if any(keyword.lower() in group_title.lower() for keyword in includes) and \
           not any(keyword.lower() in group_title.lower() for keyword in excludes):
            filtered_channels.append(channel)
    return filtered_channels


def write_to_m3u_file(
        channels: List[IPTVChannel],
        output_path: str = 'playlist.m3u') -> None:
    """使用ipytv库，将给定的频道列表写入到m3u文件中

    Args:
        channels (List[IPTVChannel]): _description_
        output_path (str): default 'playlist.m3u'
    """
    result_pl = M3UPlaylist()
    result_pl.append_channels(channels)
    with open(output_path, 'w', encoding='utf-8') as out_file:
        content = result_pl.to_m3u_plus_playlist()
        out_file.write(content)
