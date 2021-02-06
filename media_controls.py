import win32api

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1


def control_media_by_id(button_id, is_long_press):
    target_vk = {
        'A': [
            VK_MEDIA_PLAY_PAUSE,
            VK_MEDIA_NEXT_TRACK
        ],
        'B': [
            VK_VOLUME_UP,
            VK_VOLUME_UP
        ],
        'C': [
            VK_VOLUME_DOWN,
            VK_VOLUME_DOWN
        ]
    }[button_id][int(is_long_press)]

    win32api.keybd_event(target_vk, 0, 0, 0)


def toggle_play():
    win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
