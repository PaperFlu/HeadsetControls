import win32api

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF


def control_media_by_id(button_id):
    target_vk = {
        'A': VK_MEDIA_PLAY_PAUSE,
        'B': VK_VOLUME_UP,
        'C': VK_VOLUME_DOWN
    }[button_id]

    win32api.keybd_event(target_vk, 0, 0, 0)


def toggle_play():
    win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
