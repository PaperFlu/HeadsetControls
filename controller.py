import timeit
import sounddevice as sd
from media_controls import control_media_by_id

SAMPLE_RATE = 1000  # Sample rate for our input stream
BLOCK_SIZE = 10  # Number of samples before we trigger a processing callback
LONG_PRESS_SECONDS = 0.6  # Number of seconds button should be held to register long press

BUTTON_A_THRESHOLD = 1
BUTTON_B_THRESHOLD = 0.025
BUTTON_C_THRESHOLD = 0.015
NORMAL_THRESHOLD = 0.01

RECOVER_THRESHOLD = 0.0005
RECOVER_DEVIATION = 0.001

LOG_FILE = open("log.txt", "a")
LOG_FILE.write("//\n")
LOG_FILE.flush()


class HeadsetButtonController:
    def process_frames(self, in_data, frames, time, status):
        mean1 = sum([x[0] for x in in_data[:]]) / len(in_data[:])
        mean2 = sum([x[1] for x in in_data[:]]) / len(in_data[:])

        diff_list = [x[0] - x[1] for x in in_data[:]]
        deviation = max(diff_list[:]) - min(diff_list[:])

        diff = mean2 - mean1

        if self.is_pressing:
            diff_abs = abs(diff)
            if diff_abs < RECOVER_THRESHOLD and deviation < RECOVER_DEVIATION:
                self.is_pressing = False

                if self.largest_diff <= BUTTON_C_THRESHOLD:
                    control_media_by_id('C')
                elif self.largest_diff <= BUTTON_B_THRESHOLD:
                    control_media_by_id('B')
                elif self.largest_diff <= BUTTON_A_THRESHOLD:
                    control_media_by_id('A')

                LOG_FILE.write("%f %f %f\n" % (self.largest_diff, timeit.default_timer() - self.press_time, deviation))
                LOG_FILE.flush()

            else:
                if self.largest_diff < diff:
                    self.largest_diff = diff

        else:
            if diff > NORMAL_THRESHOLD:
                self.is_pressing = True
                self.largest_diff = diff
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
        self.largest_diff = 0
        self.press_time = 0
