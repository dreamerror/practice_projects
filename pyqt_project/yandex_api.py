import os
from typing import List, Optional

import yandex_music as ym


LOGIN = os.getenv('username')
PASSWORD = os.getenv('password')

client = ym.Client.fromCredentials(LOGIN, PASSWORD)
anonymous_client = ym.Client()


class YandexTrack:
    def __init__(self, track: Optional[ym.Track, ym.TrackShort]):
        if isinstance(track, ym.TrackShort):
            self.__track = track.fetch_track()
        else:
            self.__track = track

    @property
    def title(self) -> str:
        return self.__track.title

    @property
    def duration(self) -> str:
        duration_ms = self.__track.duration_ms
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds -= minutes * 60
        s_seconds = str(seconds) if seconds > 10 else '0' + str(seconds)
        s_minutes = str(minutes) if minutes > 10 else '0' + str(minutes)
        return f'{s_minutes}:{s_seconds}'

    @property
    def duration_sec(self):
        return self.__track.duration_ms // 1000


class YandexPlaylist:
    def __init__(self, playlist: ym.Playlist):
        self.__playlist = playlist

    @property
    def title(self) -> str:
        return self.__playlist.title

    @property
    def track_count(self) -> int:
        return self.__playlist.track_count


def search_artist_by_name(ym_client: ym.Client, name: str, full_compar: bool = False) -> List[ym.Artist]:
    artist_list = list()

    for result in ym_client.search(name).artists.results:
        if (full_compar and result.name == name) or not full_compar:
            artist_list.append(result)

    return artist_list


def get_artist_albums(artist: ym.Artist) -> List[ym.ArtistAlbums]:
    all_albums = list()
    page = 0
    albums_on_page = True

    while albums_on_page:

        if not artist.get_albums(page=page):
            albums_on_page = False

        else:
            all_albums += artist.get_albums(page=page)
            page += 1

    return all_albums


def get_user_playlists(ym_client: ym.Client) -> List[ym.Playlist]:
    playlist_list = list()
    for playlist in ym_client.users_playlists_list():
        playlist_kind = playlist.kind
        playlist_list.append(ym_client.users_playlists(kind=playlist_kind))
    return playlist_list


def get_playlist_tracks(playlist: ym.Playlist) -> List[ym.Track]:
    tracks = list()

    for track in playlist.tracks:
        tracks.append(track.fetch_track())
    return tracks


# for track in client.users_likes_tracks():
#     track = track.fetch_track()
#     album = track['albums'][0].title
#     title = track['title']
#     artists = list()
#     for artist in track['artists']:
#         # pprint(artist.id)
#         pprint(client.search(artist.name).artists)
#         artists.append(artist.name)
#     artists_string = ', '.join(artists)
    # pprint(f'{title} from {album} by {artists_string}')

# client.users_likes_tracks()[3].fetch_track().download('nobody.mp3')

# for artist in search_artist_by_name(anonymous_client, 'Pyrokinesis', True):
#     for album in get_artist_albums(artist):
#         s = list()
#         for songer in album.artists:
#             s.append(songer.name)
#         print(f'{album.title}: {", ".join(s)}')

# for track in client.users_likes_tracks():
#     track = track.fetch_track()
#     s = list()
#     for songer in track.artists:
#         s.append(songer.name)
#     print(f'{track.title}: {", ".join(s)}: {normalize_duration(track.duration_ms)}')

with open('log.txt', 'w') as log:
    for playlist in get_user_playlists(client):
    # playlist = get_user_playlists(client)[0]
        log.write(playlist.title)
        tracks = list()
        for track in playlist.tracks:
            log.write('\n')
            log.write(f'\t\t{track.fetch_track().title}')
        log.write('\n\n\n\n')
