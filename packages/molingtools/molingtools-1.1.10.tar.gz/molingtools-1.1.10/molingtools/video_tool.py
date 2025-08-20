try:
    from PIL import Image
    from moviepy.editor import VideoFileClip
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install moviepy pillow')
    
    
# 等比例抽帧
def vedioFrameIt(video_path, frame_num: int=None, is_return_frame = True):
    with VideoFileClip(video_path) as video:
        if frame_num: 
            # 计算抽帧的时间点
            for i in range(frame_num):
                ftime = video.duration * i / frame_num
                # 抽帧
                frame = video.get_frame(ftime)
                if is_return_frame:
                    # array
                    yield frame
                else:
                    yield Image.fromarray(frame)
        else:
            # 默认抽取所有帧
            for frame in video.iter_frames():
                yield frame 
        