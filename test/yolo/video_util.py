import cv2
import os

def extract_frames(video_path, output_dir, target_width, target_height):
    # 确保保存图片的文件夹存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开视频文件
    video_capture = cv2.VideoCapture(video_path)

    # 检查视频是否打开成功
    if not video_capture.isOpened():
        print("无法打开视频文件")
        return

    frame_count = 0
    success, frame = video_capture.read()
    #间隔帧
    save_step = 10

    while success:
        if not frame_count % save_step == 0:
            break
        # 调整帧的分辨率
        resized_frame = cv2.resize(frame, (target_width, target_height))

        # 保存帧为图片
        frame_filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, resized_frame)

        # 打印保存的帧信息
        print(f"保存 {frame_filename}")

        # 读取下一帧
        success, frame = video_capture.read()
        frame_count += 1

    # 释放视频文件
    video_capture.release()
    print("视频帧提取完成！")

# 示例：使用此函数提取帧
video_path = 'example_video.mp4'  # 视频文件路径
output_dir = 'output_frames'      # 保存帧的目录
target_width = 640                # 目标宽度
target_height = 640               # 目标高度

extract_frames(video_path, output_dir, target_width, target_height)

if __name__ == '__main__':
    video_path = 'example_video.mp4'
    output_dir = 'output_frames'
    target_width = 640
    target_height = 640
    extract_frames(video_path, output_dir, target_width, target_height)