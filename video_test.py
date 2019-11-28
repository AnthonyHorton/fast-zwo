import time
import numpy as np
from numpy_ringbuffer import RingBuffer
from asi import ASICamera


def frame_rate_test(camera, n=100):
    start_time = time.monotonic()
    camera.start_video_capture()
    image_array = RingBuffer(capacity=10, dtype=(np.uint16, 3672, 5496))
    for i in range(n):
        image = camera.get_video_data()
        #Start Brint's code
        if image is not None:
            #do stuff
            image_array.append(image)
            diff = image_array[0] - image
            
            
    end_time = time.monotonic()
    camera.stop_video_capture()
    fps = n / (end_time - start_time)
    msg = "Got {} frames in {} seconds ({} fps).".format(n, (end_time - start_time), fps)
    print(msg)
    return fps


if __name__ == '__main__':
    camera = ASICamera(library_path='/usr/local/lib/libASICamera2.so')
    frame_rate_test(camera, n=1000)
