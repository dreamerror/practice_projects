import os
from typing import List, Optional, Union

import yandex_music as ym


LOGIN = os.getenv('username')
PASSWORD = os.getenv('password')

client = ym.Client.fromCredentials(LOGIN, PASSWORD)
anonymous_client = ym.Client()

# print(anonymous_client.account_status()['plus'].has_plus)
# exit()


class YandexTrack:
    def __init__(self, track: Union[ym.Track, ym.TrackShort]):
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

    def get_playlist_tracks(self) -> List[YandexTrack]:
        tracklist = list()
        for track in self.__playlist:
            track = YandexTrack(track)
            tracklist.append(track)
        return tracklist


class YandexAlbum:
    def __init__(self, album: ym.Album):
        self.__album = album

    @property
    def title(self):
        return self.__album.title

    def __repr__(self):
        return self.title

    def get_tracks(self) -> List[YandexTrack]:
        all_tracks = list()
        for volume in self.__album.volumes:
            for track in volume:
                all_tracks.append(YandexTrack(track))
        return all_tracks


class YandexArtist:
    def __init__(self, artist: ym.Artist):
        self.__artist = artist

    @property
    def name(self):
        return self.__artist.name

    def get_albums(self) -> List[YandexAlbum]:
        all_albums = list()
        page = 0
        albums_on_page = True

        while albums_on_page:

            if not self.__artist.get_albums(page=page):
                albums_on_page = False

            else:
                for album in self.__artist.get_albums(page=page):
                    all_albums.append(YandexAlbum(album))
                page += 1

        return all_albums


class YandexClient:
    def __init__(self, yandex_client: ym.Client):
        self.__client = yandex_client
        if self.__client.account_status()['account']['login'] is None:
            self.is_anonymous = True
        else:
            self.is_anonymous = False
        self.subscription_status = False
        if not self.is_anonymous:
            self.subscription_status = self.__client.account_status()['plus'].has_plus

    def get_playlists(self) -> Union[None, List[YandexPlaylist]]:
        if self.is_anonymous:
            return None
        else:
            playlists_list = list()
            for playlist in self.__client.users_playlists_list():
                playlist_kind = playlist.kind
                playlists_list.append(YandexPlaylist(self.__client.users_playlists(kind=playlist_kind)))
            return playlists_list

    def search_artist_by_name(self, name: str, full_compar: bool = False) -> List[YandexArtist]:
        artist_list = list()
        for result in self.__client.search(name).artists.results:
            if (full_compar and result.name == name) or not full_compar:
                artist_list.append(YandexArtist(result))
        return artist_list
