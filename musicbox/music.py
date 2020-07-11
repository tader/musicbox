#!/usr/bin/env python

from sonos.api import control
from sonos.config import active_group_store, active_household_store
from sonos.decorators import output_option, format_result, login_required, auto_refresh_token

import soco

from .config import Config


class Music():
    def __init__(self):
        self.config = Config()
        self.group_id = active_group_store.get_active_group()
        self.playing_id = None
        self.playing_type = None
        self.playing_shuffle = False
        self.paused = False

        self._zones_cached = None
        self._zones = []

    def zones(self):
        selected = self.config.get("zones", [])
        if self._zones_cached != selected:
            if len(selected) == 0:
                zones = list(soco.discover())
            else:
                zones = [
                    zone
                    for zone in soco.discover()
                    if zone.get_speaker_info()["serial_number"] in selected
                ]
            self._zones = zones
            self._zones_cached = selected
        return self._zones

    def group(self):
        coordinator, *members = self.zones()

        #if not coordinator.is_coordinator:
        #    coordinator.unjoin()

        for member in members:
            if member not in coordinator.group.members:
                member.join(coordinator)

        self.set_group(coordinator.group.uid)

        return coordinator.group

    def coordinator(self):
        return self.group().coordinator

    def clear_queue(self):
        self.coordinator().clear_queue()

    def volume(self):
        for zone in self.zones():
            if zone.volume >= 20 or zone.volume <=3:
                zone.volume = 13

            if zone.mute:
                zone.mute = False

    def play(self, card):
        if card.content_type and card.content_id:
            self.volume()

            if self.playing_id != card.content_id or self.playing_type != card.content_type or self.playing_shuffle != card.shuffle:
                if card.content_type == "sonos.playlist":
                    self.clear_queue()
                    self.play_playlist(card.content_id, shuffle=card.shuffle)
                elif card.content_type == "sonos.favorite":
                    self.clear_queue()
                    self.play_favorite(card.content_id, shuffle=card.shuffle)
                else:
                    raise Exception(f"Unknown content type {card.content_type} for card {card.id}")

                self.playing_type = card.content_type
                self.playing_id = card.content_id
                self.playing_shuffle = card.shuffle

                self.paused = False
            else:
                if self.paused:
                    control.play(self.group_id)
                    self.paused = False

    def pause(self, card):
        if not self.paused:
            control.pause(self.group_id)
            self.paused = True


    @login_required
    @auto_refresh_token(control.client)
    def favorites(self):
        household_id = active_household_store.get_active_household()
        response = control.client.get(control._url(f'/households/{household_id}/favorites'))
        result = control._json(response)
        return result['items']

    @login_required
    @auto_refresh_token(control.client)
    def playlists(self):
        household_id = active_household_store.get_active_household()
        response = control.client.get(control._url(f'/households/{household_id}/playlists'))
        result = control._json(response)
        return result['playlists']

    @login_required
    @auto_refresh_token(control.client)
    def playlist(self, playlist_id):
        household_id = active_household_store.get_active_household()
        response = control.client.post(control._url(f'/households/{household_id}/playlists/getPlaylist'), json={"playlistId": int(playlist_id)})
        result = control._json(response)
        return result

    @login_required
    @auto_refresh_token(control.client)
    def play_favorite(self, favorite_id, shuffle=False, repeat=False):
        response = control.client.post(
                control._url(f'/groups/{self.group_id}/favorites'),
                json={
                    "favoriteId": int(favorite_id),
                    "playOnCompletion": True,
                    "playModes": {
                        "shuffle": shuffle,
                        "repeat": repeat,
                    },
                },
        )
        result = control._json(response)
        return result

    @login_required
    @auto_refresh_token(control.client)
    def play_playlist(self, playlist_id, shuffle=False, repeat=False):
        response = control.client.post(
                control._url(f'/groups/{self.group_id}/playlists'),
                json={
                    "playlistId": int(playlist_id),
                    "playOnCompletion": True,
                    "playModes": {
                        "shuffle": shuffle,
                        "repeat": repeat,
                    },
                },
        )
        result = control._json(response)
        return result

    @login_required
    @auto_refresh_token(control.client)
    def set_group(self, group_id):
        if self.group_id != group_id:
            active_group_store.save_active_group(group_id)
            self.group_id = group_id

