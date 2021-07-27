import os
from typing import List, Union, Tuple

import yandex_music as ym


LOGIN = os.getenv('username')
PASSWORD = os.getenv('password')


class YandexTrack:
    def __init__(self, track: Union[ym.Track, ym.TrackShort]):
        if isinstance(track, ym.TrackShort):
            self.__track = track.fetch_track()
        else:
            self.__track = track
        self.__id = self.__track.track_id

    @property
    def title(self) -> str:
        return self.__track.title

    @property
    def id(self):
        return self.__id

    @property
    def artists_list(self) -> List:
        artists = list()
        for artist in self.__track.artists:
            artists.append(YandexArtist(artist))
        return artists

    def __repr__(self):
        return self.title + ' by ' + ', '.join(list(map(str, self.artists_list)))

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

    def download_link(self) -> str:
        return self.__track.get_download_info()[0].get_direct_link()


class YandexPlaylist:
    def __init__(self, playlist: ym.Playlist):
        self.__playlist = playlist

    @property
    def title(self) -> str:
        return self.__playlist.title

    def __repr__(self):
        return self.title

    @property
    def track_count(self) -> int:
        return self.__playlist.track_count

    def get_playlist_tracks(self) -> List[YandexTrack]:
        tracklist = list()
        for track in self.__playlist.tracks:
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

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

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

    def get_tracks(self) -> List[YandexTrack]:
        all_tracks = list()
        page = 0
        tracks_on_page = True
        while tracks_on_page:
            if not self.__artist.get_tracks(page=page):
                tracks_on_page = False
            else:
                for track in self.__artist.get_tracks(page=page):
                    all_tracks.append(YandexTrack(track))
                page += 1
        return all_tracks


class YandexClient:
    def __init__(self, yandex_client: Union[ym.Client, Tuple[str, str]]):
        if isinstance(yandex_client, ym.Client):
            self.__client = yandex_client
        else:
            login, pwd = yandex_client
            self.__client = ym.Client.fromCredentials(login, pwd)
        if self.__client.account_status()['account']['login'] is None:
            self.is_anonymous = True
        else:
            self.is_anonymous = False
        self.subscription_status = False
        if not self.is_anonymous:
            self.subscription_status = self.__client.account_status()['plus'].has_plus

    def like_track(self, track: YandexTrack) -> bool:
        if not self.is_anonymous:
            return self.__client.users_likes_tracks_add(track.id)
        else:
            return False

    def dislike_track(self, track: YandexTrack) -> bool:
        if not self.is_anonymous:
            return self.__client.users_dislikes_tracks_add(track.id)
        else:
            return False

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
        print(self.__client.search(name))
        for result in self.__client.search(name).artists.results:
            if (full_compar and result.name == name) or not full_compar:
                artist_list.append(YandexArtist(result))
        return artist_list

    def search_track_by_title(self, title: str, full_compar: bool = False) -> List[YandexTrack]:
        track_list = list()
        for result in self.__client.search(title).tracks.results:
            if (full_compar and result.title == title) or not full_compar:
                track_list.append(YandexTrack(result))
        return track_list

    def track_by_id(self, track_id: str) -> YandexTrack:
        track = self.__client.tracks(track_id)[0]
        return YandexTrack(track)
