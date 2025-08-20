#!/usr/bin/python3

from spotipy import Spotify
from deezspot.exceptions import InvalidLink
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
import os

class Spo:
    __error_codes = [404, 400]
    
    # Class-level API instance and credentials
    __api = None
    __client_id = None
    __client_secret = None
    __initialized = False

    @classmethod
    def __init__(cls, client_id, client_secret):
        """
        Initialize the Spotify API client.
        
        Args:
            client_id (str): Spotify API client ID.
            client_secret (str): Spotify API client secret.
        """
        if not client_id or not client_secret:
            raise ValueError("Spotify API credentials required. Provide client_id and client_secret.")
            
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Store the credentials and API instance
        cls.__client_id = client_id
        cls.__client_secret = client_secret
        cls.__api = Spotify(
            auth_manager=client_credentials_manager
        )
        cls.__initialized = True

    @classmethod
    def __check_initialized(cls):
        """Check if the class has been initialized with credentials"""
        if not cls.__initialized:
            raise ValueError("Spotify API not initialized. Call Spo.__init__(client_id, client_secret) first.")

    @classmethod
    def __get_api(cls, client_id=None, client_secret=None):
        """
        Get a Spotify API instance with the provided credentials or use stored credentials.
        
        Args:
            client_id (str, optional): Spotify API client ID
            client_secret (str, optional): Spotify API client secret
            
        Returns:
            A Spotify API instance
        """
        # If new credentials are provided, create a new API instance
        if client_id and client_secret:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            return Spotify(auth_manager=client_credentials_manager)
        
        # Otherwise, use the existing class-level API
        cls.__check_initialized()
        return cls.__api

    @classmethod
    def __lazy(cls, results, api=None):
        """Process paginated results and extend the initial page's items in-place."""
        api = api or cls.__api
        if not results or 'items' not in results:
            return results
        items_ref = results['items']

        while results.get('next'):
            results = api.next(results)
            if results and 'items' in results:
                items_ref.extend(results['items'])
            else:
                break

        return results

    @classmethod
    def __fetch_all_album_tracks(cls, album_id: str, api: Spotify) -> dict:
        """
        Fetch all tracks for an album using album_tracks pagination.
        Returns a dict shaped like Spotify's 'tracks' object with all items merged.
        """
        all_items = []
        limit = 50
        offset = 0
        first_page = None
        while True:
            page = api.album_tracks(album_id, limit=limit, offset=offset)
            if first_page is None:
                first_page = dict(page) if page is not None else None
            items = page.get('items', []) if page else []
            if not items:
                break
            all_items.extend(items)
            offset += len(items)
            if page.get('next') is None:
                break
        if first_page is None:
            return {'items': [], 'total': 0, 'limit': limit, 'offset': 0}
        # Build a consolidated tracks object
        total_val = first_page.get('total', len(all_items))
        return {
            'items': all_items,
            'total': total_val,
            'limit': limit,
            'offset': 0,
            'next': None,
            'previous': None
        }

    @classmethod
    def get_track(cls, ids, client_id=None, client_secret=None):
        """
        Get track information by ID.
        
        Args:
            ids (str): Spotify track ID
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Track information
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            track_json = api.track(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        return track_json

    @classmethod
    def get_tracks(cls, ids: list, market: str = None, client_id=None, client_secret=None):
        """
        Get information for multiple tracks by a list of IDs.
        Handles chunking by 50 IDs per request and merges results while preserving order.
        
        Args:
            ids (list): A list of Spotify track IDs.
            market (str, optional): An ISO 3166-1 alpha-2 country code.
            client_id (str, optional): Optional custom Spotify client ID.
            client_secret (str, optional): Optional custom Spotify client secret.
            
        Returns:
            dict: A dictionary containing a list of track information under key 'tracks'.
        """
        if not ids:
            return {'tracks': []}

        api = cls.__get_api(client_id, client_secret)
        all_tracks = []
        chunk_size = 50
        try:
            for i in range(0, len(ids), chunk_size):
                chunk = ids[i:i + chunk_size]
                resp = api.tracks(chunk, market=market) if market else api.tracks(chunk)
                # Spotify returns {'tracks': [...]} for each chunk
                chunk_tracks = resp.get('tracks', []) if resp else []
                all_tracks.extend(chunk_tracks)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                # Create a string of the first few IDs for the error message
                ids_preview = ', '.join(ids[:3]) + ('...' if len(ids) > 3 else '')
                raise InvalidLink(f"one or more IDs in the list: [{ids_preview}]")
            else:
                raise
        
        return {'tracks': all_tracks}

    @classmethod
    def get_album(cls, ids, client_id=None, client_secret=None):
        """
        Get album information by ID and include all tracks (paged if needed).
        
        Args:
            ids (str): Spotify album ID
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Album information with full 'tracks.items'
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            album_json = api.album(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)
            else:
                raise

        # Replace/ensure tracks contains all items via dedicated pagination endpoint
        try:
            full_tracks_obj = cls.__fetch_all_album_tracks(ids, api)
            if isinstance(album_json, dict):
                album_json['tracks'] = full_tracks_obj
        except Exception:
            # Fallback to lazy-paging over embedded 'tracks' if available
            try:
                tracks = album_json.get('tracks') if isinstance(album_json, dict) else None
                if tracks:
                    cls.__lazy(tracks, api)
            except Exception:
                pass

        return album_json

    @classmethod
    def get_playlist(cls, ids, client_id=None, client_secret=None):
        """
        Get playlist information by ID.
        
        Args:
            ids (str): Spotify playlist ID
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Playlist information
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            playlist_json = api.playlist(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        tracks = playlist_json['tracks']
        cls.__lazy(tracks, api)

        return playlist_json

    @classmethod
    def get_episode(cls, ids, client_id=None, client_secret=None):
        """
        Get episode information by ID.
        
        Args:
            ids (str): Spotify episode ID
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Episode information
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            episode_json = api.episode(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        return episode_json

    @classmethod
    def search(cls, query, search_type='track', limit=10, client_id=None, client_secret=None):
        """
        Search for tracks, albums, artists, or playlists.
        
        Args:
            query (str): Search query
            search_type (str, optional): Type of search ('track', 'album', 'artist', 'playlist')
            limit (int, optional): Maximum number of results to return
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Search results
        """
        api = cls.__get_api(client_id, client_secret)
        search = api.search(q=query, type=search_type, limit=limit)
        return search

    @classmethod
    def get_artist(cls, ids, client_id=None, client_secret=None):
        """
        Get artist information by ID.
        
        Args:
            ids (str): Spotify artist ID
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Artist information
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            artist_json = api.artist(ids)
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)

        return artist_json

    @classmethod
    def get_artist_discography(cls, ids, album_type='album,single,compilation,appears_on', limit=50, offset=0, client_id=None, client_secret=None):
        """
        Get artist information and discography by ID.
        
        Args:
            ids (str): Spotify artist ID
            album_type (str, optional): Types of albums to include
            limit (int, optional): Maximum number of results
            client_id (str, optional): Optional custom Spotify client ID
            client_secret (str, optional): Optional custom Spotify client secret
            
        Returns:
            dict: Artist discography
        """
        api = cls.__get_api(client_id, client_secret)
        try:
            # Request all types of releases by the artist.
            discography = api.artist_albums(
                ids,
                album_type=album_type,
                limit=limit,
                offset=offset
            )
        except SpotifyException as error:
            if error.http_status in cls.__error_codes:
                raise InvalidLink(ids)
            else:
                raise

        # Ensure that all pages of results are fetched.
        cls.__lazy(discography, api)
        return discography
