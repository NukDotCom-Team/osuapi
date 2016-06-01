from .model import User, SoloScore, JsonList, OsuMode, Beatmap, Match
from . import endpoints
from .connectors import *
import warnings


class OsuApi:
    """osu! api client.

    Parameters
    ----------
    key
        The osu! api key used for authorization.
    connector : Optional[event loop].
        The osuapi connector used for making requests. The library comes with
        two implementations, :class:`AHConnector` for using aiohttp, and
        :class:`ReqConnector` for using requests."""

    def __init__(self, key, *, connector):
        if not hasattr(connector, "process_request"):
            # dirty backwards compatability
            try:
                import aiohttp
                if connector is aiohttp or isinstance(connector, aiohttp.ClientSession):
                    connector = AHConnector(connector)
                    warnings.warn("Connector should now be a connector class, not aiohttp or a ClientSession directly. See use osuapi.AHConnector", Warning)
            except ImportError:
                pass
            try:
                import requests
                if connector is requests or isinstance(connector, requests.Session):
                    connector = ReqConnector(connector)
                    warnings.warn("Connector should now be a connector class, not requests or a Session directly. See use osuapi.ReqConnector", Warning)
            except ImportError:
                pass

        self.connector = connector
        self.key = key

    def _make_req(self, endpoint, data, type_):
        return self.connector.process_request(endpoint, {k: v for k, v in data.items() if v is not None}, type_)

    @staticmethod
    def _username_type(username):
        if username is None:
            return None
        return "int" if isinstance(username, int) else "string"

    def get_user(self, username, *, mode=OsuMode.osu):
        """Get a user profile.


        Parameters
        ----------
        username : str or int
            A `str` representing the user's username, or an `int` representing the user's id.
        mode : :class:`OsuMode`
            The osu! game mode for which to look up. Defaults to osu!standard.
        """
        return self._make_req(endpoints.USER, dict(
            k=self.key,
            u=username,
            type=self._username_type(username),
            m=mode.value
            ), JsonList(User))

    def get_user_best(self, username, *, mode=OsuMode.osu, limit=50):
        """Get a user's best scores.

        Parameters
        ----------
        username : str or int
            A `str` representing the user's username, or an `int` representing the user's id.
        mode : :class:`OsuMode`
            The osu! game mode for which to look up. Defaults to osu!standard.
        limit
            The maximum number of results to return. Defaults to 50.
        """
        return self._make_req(endpoints.USER_BEST, dict(
            k=self.key,
            u=username,
            type=self._username_type(username),
            m=mode.value,
            limit=limit
            ), JsonList(SoloScore))

    def get_user_recent(self, username, *, mode=OsuMode.osu, limit=10):
        """Get a user's most recent scores.

        Parameters
        ----------
        username : str or int
            A `str` representing the user's username, or an `int` representing the user's id.
        mode : :class:`OsuMode`
            The osu! game mode for which to look up. Defaults to osu!standard.
        limit
            The maximum number of results to return. Defaults to 10, maximum 50.
        """
        return self._make_req(endpoints.USER_RECENT, dict(
            k=self.key,
            u=username,
            type=self._username_type(username),
            m=mode.value,
            limit=limit
            ), JsonList(Score))

    def get_scores(self, beatmap_id, *, username=None, mode=OsuMode.osu, mods=None, limit=50):
        """Get the top scores for a given beatmap.

        FIXME - not sure these params are correct.
        Parameters
        ----------
        beatmap_id
            Individual Beatmap ID to lookup.
        username : str or int
            A `str` representing the user's username, or an `int` representing the user's id.
            If specified, restricts returned scores to the specified user.
        mode : :class:`OsuMode`
            The osu! game mode for which to look up. Defaults to osu!standard.
        mods : :class:`OsuMod`
            If specified, restricts returned scores to the specified mods.
        limit
            Number of results to return. Defaults to 50, maximum FIXME.
        """
        return self._make_req(endpoints.SCORES, dict(
            k=self.key,
            b=beatmap_id,
            u=username,
            type=self._username_type(username),
            m=mode.value,
            mods=mods.value,
            limit=limit), JsonList(Score))

    def get_beatmaps(self, *, since=None, beatmapset_id=None, beatmap_id=None, username=None, mode=OsuMode.osu,
                     include_converted=False, beatmap_hash=None, limit=500):
        """Get beatmaps.

        Parameters
        ----------
        since : datetime
            If specified, restrict results to beatmaps *ranked* after this date.
        beatmapset_id
            If specified, restrict results to a specific beatmap set.
        beatmap_id
            If specified, restrict results to a specific beatmap.
        username : `str` or `int`
            A `str` representing the user's username, or an `int` representing the user's id.
            If specified, restrict results to a specific user.
        mode : :class:`OsuMode`
            The osu! game mode for which to look up. Defaults to osu!standard.
        include_converted : bool
            Whether or not to include autoconverts. Defaults to false.
        beatmap_hash
            If specified, restricts results to a specific beatmap hash.
        limit
            Number of results to return. Defaults to 500, maximum FIXME.
        """
        return self._make_req(endpoints.BEATMAPS, dict(
            k=self.key,
            s=beatmapset_id,
            b=beatmap_id,
            u=username,
            since="{:%Y-%m-%d %H:%M:%S}".format(since) if since is not None else None,
            type=self._username_type(username),
            m=mode.value,
            a=include_converted,
            h=beatmap_hash,
            limit=limit
            ), JsonList(Beatmap))

    def get_match(self, match_id):
        """Get a multiplayer match.

        match_id
            The ID of the match to retrieve. This is the ID that you see in a online multiplayer match summary.
            This does not correspond the in-game game ID."""
        return self._make_req(endpoints.MATCH, dict(
            k=self.key,
            mp=match_id), Match)
