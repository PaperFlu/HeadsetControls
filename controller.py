import timeit
import sounddevice as sd
from media_controls import control_media_by_id

SAMPLE_RATE = 1000  # Sample rate for our input stream
BLOCK_SIZE = 10  # Number of samples before we trigger a processing callback
LONG_PRESS_DURATION_THRESHOLD = 0.8  # Number of seconds button should be held to register long press

CAPTURE_THRESHOLDS = [-0.4, 0.4]

BUTTON_A_THRESHOLDS = [-1, 1]
BUTTON_B_THRESHOLDS = [-1, 0.018]
BUTTON_C_THRESHOLDS = [-0.013, 0.012]
NORMAL_THRESHOLD = 0.008

RECOVER_DURATION_THRESHOLD = 0.15
RECOVER_DEVIATION_THRESHOLD = 0.005

LOG_FILE = open("log.txt", "a")
LOG_FILE.write("//\n")
LOG_FILE.flush()


class HeadsetButtonController:
    def process_frames(self, in_data, frames, time, status):
        if in_data[0][0] < CAPTURE_THRESHOLDS[0] or CAPTURE_THRESHOLDS[1] < in_data[0][0]:
            return

        diff_list = [(x[1] - x[0]) for x in in_data]

        max_diff = max(diff_list)
        min_diff = min(diff_list)
        max_abs_diff = max(abs(max_diff), abs(min_diff))
        deviation = max_diff - min_diff

        if self.is_pressing:
            press_duration = timeit.default_timer() - self.press_time

            is_long_press = press_duration >= LONG_PRESS_DURATION_THRESHOLD

            if max_abs_diff < NORMAL_THRESHOLD and deviation < RECOVER_DEVIATION_THRESHOLD:

                if self.recover_time == 0:
                    self.recover_time = timeit.default_timer()
                elif timeit.default_timer() - self.recover_time >= RECOVER_DURATION_THRESHOLD:
                    self.is_pressing = False
                    self.recover_time = 0

                    LOG_FILE.write("%f %f %f %f\n" % (self.largest_diff, self.smallest_diff, press_duration, deviation))
                    LOG_FILE.flush()

            else:
                self.recover_time = timeit.default_timer()

            if not self.is_fired:
                if not self.is_pressing or is_long_press:
                    self.is_fired = True

                    if BUTTON_C_THRESHOLDS[0] <= self.smallest_diff and self.largest_diff <= BUTTON_C_THRESHOLDS[1]:
                        control_media_by_id('C', is_long_press)
                    elif BUTTON_B_THRESHOLDS[0] <= self.smallest_diff and self.largest_diff <= BUTTON_B_THRESHOLDS[1]:
                        control_media_by_id('B', is_long_press)
                    elif BUTTON_A_THRESHOLDS[0] <= self.smallest_diff and self.largest_diff <= BUTTON_A_THRESHOLDS[1]:
                        control_media_by_id('A', is_long_press)

                else:
                    if self.largest_diff < max_diff:
                        self.largest_diff = max_diff
                    if self.smallest_diff > min_diff:
                        self.smallest_diff = min_diff

        else:
            if max_abs_diff > NORMAL_THRESHOLD:
                self.is_pressing = True
                self.is_fired = False
                self.largest_diff = max_diff
                self.smallest_diff = min_diff
                self.press_time = timeit.default_timer()

    def __init__(self):
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=2,
            callback=self.process_frames
        )
        self.stream.start()

        self.is_pressing = False
        self.is_fired = False
        self.largest_diff = 0
        self.smallest_diff = 0
        self.press_time = 0
        self.recover_time = 0
