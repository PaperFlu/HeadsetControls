import timeit
import sounddevice as sd
from media_controls import control_media_by_id

SAMPLE_RATE = 1000  # Sample rate for our input stream
BLOCK_SIZE = 10  # Number of samples before we trigger a processing callback
LONG_PRESS_SECONDS = 0.6  # Number of seconds button should be held to register long press

BUTTON_A_THRESHOLD = 1
BUTTON_B_THRESHOLD = 0.028
BUTTON_C_THRESHOLD = 0.02
NORMAL_THRESHOLD = 0.015

RECOVER_THRESHOLD = 0.0005
RECOVER_DEVIATION = 0.0005

LOG_FILE = open("log.txt", "a")
LOG_FILE.write("//\n")
LOG_FILE.flush()


class HeadsetButtonController:
    def process_frames(self, in_data, frames, time, status):
        diff_list = [x[1] - x[0] for x in in_data[:]]

        diff = max(diff_list[:])
        deviation = max(diff_list[:]) - min(diff_list[:])

        if self.is_pressing:
            diff_abs = abs(diff)
            press_duration = timeit.default_timer() - self.press_time

            is_long_press = press_duration >= LONG_PRESS_SECONDS
            is_recovered = diff_abs < RECOVER_THRESHOLD and deviation < RECOVER_DEVIATION

            if is_recovered:
                self.is_pressing = False

                LOG_FILE.write("%f %f %f\n" % (self.largest_diff, press_duration, deviation))
                LOG_FILE.flush()

            if not self.is_fired:
                if is_recovered or is_long_press:
                    self.is_fired = True

                    if self.largest_diff <= BUTTON_C_THRESHOLD:
                        control_media_by_id('C', is_long_press)
                    elif self.largest_diff <= BUTTON_B_THRESHOLD:
                        control_media_by_id('B', is_long_press)
                    elif self.largest_diff <= BUTTON_A_THRESHOLD:
                        control_media_by_id('A', is_long_press)

                elif self.largest_diff < diff:
                    self.largest_diff = diff

        else:
            if diff > NORMAL_THRESHOLD:
                self.is_pressing = True
                self.largest_diff = diff
                self.press_time = timeit.default_timer()
                self.is_fired = False

    def __init__(self):
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=2,
            callback=self.process_frames
        )
        self.stream.start()

        self.is_pressing = False
        self.largest_diff = 0
        self.press_time = 0
        self.is_fired = False
