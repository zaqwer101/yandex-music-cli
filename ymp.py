#!/usr/bin/env python3
from yandex_music import Client
import subprocess
from config import TOKEN, PLAYER, PLAYER_ARGS, CACHE_DIR, SOCKET, PLAYER_SOCKET
import random
from enum import Enum
import threading
import time
import os
import signal
import socket


if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


class State(Enum):
    NONE        = 0
    PLAYING     = 1
    PAUSED      = 2
    NEXT_TRACK  = 3
    PREV_TRACK  = 4
    STOP        = 5
    PLAY_PAUSE  = 6


def tracks_load():
    client = Client(TOKEN).init()
    liked_list_api  = client.users_likes_tracks()
    tracks          = liked_list_api.tracks
    revision        = liked_list_api.revision
    random.shuffle(tracks)
    return tracks


CURRENT_STATE = State.PAUSED    
TRACKS = tracks_load()  # tracks list
PLAYER_PID = 0          # PID of player with current track


def play_track(track_name):
    global CURRENT_STATE
    global PLAYER_PID
    if CURRENT_STATE != State.PLAYING:
        CURRENT_STATE = State.PLAYING
        process = subprocess.Popen([PLAYER, track_name, "--input-ipc-server=/tmp/mpv.sock"])
        PLAYER_PID = process.pid
        process.communicate()
        if CURRENT_STATE != State.NEXT_TRACK:
            PLAYER_PID = 0
            CURRENT_STATE = State.NEXT_TRACK


def handler():
    global CURRENT_STATE
    global PLAYER_PID
    
    current_track = 0
    while current_track < len(TRACKS):
        while(True):
            if CURRENT_STATE == State.NEXT_TRACK:
                if PLAYER_PID != 0:
                    os.kill(PLAYER_PID, signal.SIGKILL)
                break

            elif CURRENT_STATE == State.PREV_TRACK:
                if PLAYER_PID != 0:
                    os.kill(PLAYER_PID, signal.SIGTERM)
                # if this track is already first, play it
                if current_track > 1:
                    current_track -= 2
                else:
                    current_track = 0
                break

            elif CURRENT_STATE == State.PLAY_PAUSE:
                if PLAYER_PID != 0:
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(PLAYER_SOCKET)
                    s.send(b'{"command": ["cycle", "pause"]}\n')
                    s.close()
                    CURRENT_STATE = State.PAUSED
                else:
                    CURRENT_STATE = State.NONE

            elif CURRENT_STATE == State.PAUSED:
                continue

            elif CURRENT_STATE == State.STOP:
                if PLAYER_PID != 0:
                    os.kill(PLAYER_PID, signal.SIGKILL)
                exit(0)

            if CURRENT_STATE == State.NONE: # no state at the moment
                break


            time.sleep(0.5)

        print(f"Current track: {current_track}")
        track_title    = TRACKS[current_track].fetchTrack().title
        track_artist   = ', '.join(TRACKS[current_track].fetchTrack().artists_name())

        # get rid of "/" in track name
        track_artist   = track_artist.replace("/", "\\")
        track_title    = track_title.replace("/", "\\")

        track_name = CACHE_DIR + track_artist + " - " + track_title + ".mp3"
        TRACKS[current_track].fetchTrack().download(track_name)

        playing_thread = threading.Thread(target=play_track, args=[track_name], daemon=True)
        playing_thread.start()

        current_track += 1


def socket_listener():
    global CURRENT_STATE
    __socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove(SOCKET)
    except OSError:
        pass
    __socket.bind(SOCKET)
    __socket.listen(10)
    while(True):
        conn, addr = __socket.accept()
        data = conn.recv(1024).decode().strip()
        print(data)
        if data == "NEXT_TRACK":
            CURRENT_STATE = State.NEXT_TRACK
        elif data == "PREV_TRACK":
            CURRENT_STATE = State.PREV_TRACK
        elif data == "STOP":
            CURRENT_STATE = State.STOP
        elif data == "PLAY_PAUSE":
            CURRENT_STATE = State.PLAY_PAUSE


socket_thread = threading.Thread(target=socket_listener, daemon=True)
socket_thread.start()

main_thread = threading.Thread(target=handler, daemon=False)
main_thread.start()