import time

from asi import ASICamera


def frame_rate_test(camera, n=100):
    start_time = time.monotonic()
    camera.start_video_capture()
    for i in range(n):
        image = camera.get_video_data()
    end_time = time.monotonic()
    camera.stop_video_capture()
    fps = n / (end_time - start_time)
    msg = "Got {} frames in {} seconds ({} fps).".format(n, (end_time - start_time), fps)
    print(msg)
    return fps


if __name__ == '__main__':
    camera = ASICamera(library_path='/usr/local/lib/libASICamera2.so')
    print("Do nothing test:")
    frame_rate_test(camera, n=500)
