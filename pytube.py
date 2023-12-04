import pytube


# 视频链接
video_url = "https://www.youtube.com/watch?v=F3pgQb3Gpw"

# 创建YouTube对象
youtube = YouTube(video_url)

# 获取视频的所有可用格式
video_formats = youtube.streams.filter(file_extension='mp4').all()

# 选择要下载的格式（这里选择第一个格式）
video = video_formats[0]

# 下载视频
video.download("/")




