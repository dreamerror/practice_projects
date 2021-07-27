import os
from typing import List, Optional

import yandex_music as ym


LOGIN = os.getenv('username')
PASSWORD = os.getenv('password')

client = ym.Client.fromCredentials(LOGIN, PASSWORD)


def search_artist_by_name(ym_client: ym.Client, name: str) -> List[ym.Artist]:
    artist_list = list()

    for result in ym_client.search(name).artists.results:
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


def normalize_duration(duration_ms: int) -> str:
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds -= minutes * 60
    s_seconds = str(seconds) if seconds > 10 else '0' + str(seconds)
    s_minutes = str(minutes) if minutes > 10 else '0' + str(minutes)
    return f'{s_minutes}:{s_seconds}'


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

# for artist in search_artist_by_name(client, 'Pyrokinesis'):
#     for album in get_artist_albums(artist):
#         s = list()
#         for songer in album.artists:
#             s.append(songer.name)
#         print(f'{album.title}: {", ".join(s)}')

for track in client.users_likes_tracks():
    track = track.fetch_track()
    s = list()
    for songer in track.artists:
        s.append(songer.name)
    print(f'{track.title}: {", ".join(s)}: {normalize_duration(track.duration_ms)}')
