import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from enum import Enum
import time

class Method(Enum):
    DIFFERENCE = "difference"
    SSIM = "ssim"
    HISTOGRAM = "histogram"
    MOTION_VECTOR = "motion_vector"  # 新增运动矢量方法

class MotionAnalyzer:
    """运动矢量分析器"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置分析器状态"""
        self.prev_mvs = None
        self.motion_history = []

    def extract_motion_vectors(self, video_path: str, frame_idx: int) -> Dict:
        """
        从压缩视频流中提取运动矢量信息

        Args:
            video_path: 视频文件路径
            frame_idx: 帧序号

        Returns:
            包含运动矢量信息的字典
        """
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        # 设置解码器参数以访问运动矢量
        cap.set(cv2.CAP_PROP_CODEC_PARAMS, cv2.VIDEOWRITER_PROP_QUALITY | cv2.CODEC_FLAG_EXTRACT_MVS)

        ret, _ = cap.read()
        if not ret:
            cap.release()
            return {}

        # 获取运动矢量信息
        mvs = {
            'vectors': cap.get(cv2.CAP_PROP_MOTION_VECTORS),
            'mb_type': cap.get(cv2.CAP_PROP_MB_TYPE),
            'mb_size': cap.get(cv2.CAP_PROP_MB_SIZE)
        }

        cap.release()
        return mvs

    def compute_motion_magnitude(self, mvs: Dict) -> float:
        """
        计算运动矢量的幅度

        Args:
            mvs: 运动矢量信息

        Returns:
            运动幅度得分
        """
        if not mvs or 'vectors' not in mvs:
            return 0.0

        vectors = mvs['vectors']
        if len(vectors) == 0:
            return 0.0

        # 计算运动矢量的平均幅度
        magnitudes = np.sqrt(vectors[:, 2]**2 + vectors[:, 3]**2)  # x和y方向的位移
        mean_magnitude = np.mean(magnitudes)

        # 计算运动矢量的方向一致性
        angles = np.arctan2(vectors[:, 3], vectors[:, 2])
        angle_std = np.std(angles)

        # 综合考虑幅度和方向一致性
        motion_score = mean_magnitude * (1 + angle_std)

        return motion_score

    def analyze_motion_change(self, current_mvs: Dict, threshold: float) -> bool:
        """
        分析运动变化是否足够显著

        Args:
            current_mvs: 当前帧的运动矢量
            threshold: 判断阈值

        Returns:
            是否检测到显著的运动变化
        """
        current_magnitude = self.compute_motion_magnitude(current_mvs)

        if self.prev_mvs is None:
            self.prev_mvs = current_mvs
            return True

        prev_magnitude = self.compute_motion_magnitude(self.prev_mvs)

        # 计算运动变化率
        if prev_magnitude > 0:
            change_ratio = abs(current_magnitude - prev_magnitude) / prev_magnitude
        else:
            change_ratio = current_magnitude

        self.prev_mvs = current_mvs
        self.motion_history.append(current_magnitude)

        # 保持历史记录在合理范围内
        if len(self.motion_history) > 30:
            self.motion_history.pop(0)

        # 使用自适应阈值
        if len(self.motion_history) > 5:
            mean_motion = np.mean(self.motion_history)
            std_motion = np.std(self.motion_history)
            adaptive_threshold = threshold * (1 + std_motion / mean_motion if mean_motion > 0 else 1)
        else:
            adaptive_threshold = threshold

        return change_ratio > adaptive_threshold

class AdvancedKeyframeExtractor:
    def __init__(self):
        self.reset()
        self.motion_analyzer = MotionAnalyzer()

    def reset(self):
        """重置提取器状态"""
        self.prev_frame = None
        self.prev_hist = None
        self.keyframes = []
        self.frame_indices = []
        self.motion_analyzer.reset()

    # ... (保持原有的其他方法不变)

    def is_keyframe(self,
                    current_frame: np.ndarray,
                    method: Method,
                    threshold: float,
                    video_path: Optional[str] = None,
                    frame_idx: Optional[int] = None) -> bool:
        """
        判断是否为关键帧

        Args:
            current_frame: 当前帧
            method: 使用的方法
            threshold: 阈值
            video_path: 视频文件路径(运动矢量方法需要)
            frame_idx: 帧序号(运动矢量方法需要)

        Returns:
            是否为关键帧
        """
        if self.prev_frame is None:
            return True

        if method == Method.MOTION_VECTOR:
            if video_path is None or frame_idx is None:
                return False
            current_mvs = self.motion_analyzer.extract_motion_vectors(video_path, frame_idx)
            return self.motion_analyzer.analyze_motion_change(current_mvs, threshold)

        elif method == Method.DIFFERENCE:
            diff = self.compute_difference(current_frame, self.prev_frame)
            return diff > threshold

        elif method == Method.SSIM:
            similarity = self.compute_ssim(current_frame, self.prev_frame)
            return similarity < threshold

        elif method == Method.HISTOGRAM:
            similarity = self.compute_histogram_similarity(current_frame, self.prev_frame)
            return similarity < threshold

        return False

    def extract_keyframes(self,
                          video_path: str,
                          method: Method = Method.DIFFERENCE,
                          threshold: float = 30.0,
                          sampling_rate: int = 5,
                          scale_factor: float = 0.5,
                          target_size: Optional[Tuple[int, int]] = None,
                          max_frames: Optional[int] = None,
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None
                          ) -> Tuple[List[np.ndarray], List[int]]:
        """
        提取关键帧

        Args:
            video_path: 视频文件路径
            method: 使用的方法
            threshold: 阈值
                - difference: 30.0
                - ssim: 0.7
                - histogram: 0.8
                - motion_vector: 0.4 (运动变化率阈值)
            sampling_rate: 采样率 (每N帧处理一帧)
            scale_factor: 降采样比例
            target_size: 目标大小
            max_frames: 最大处理帧数
            start_time: 开始时间(秒)
            end_time: 结束时间(秒)

        Returns:
            keyframes: 关键帧列表
            frame_indices: 关键帧对应的原始帧序号
        """
        self.reset()
        cap = cv2.VideoCapture(video_path)

        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        duration = total_frames / fps

        print(f"\n开始处理视频:")
        print(f"方法: {method.value}")
        print(f"总帧数: {total_frames}")
        print(f"FPS: {fps}")
        print(f"时长: {duration:.2f}秒")

        # 处理时间范围
        if start_time is not None:
            start_frame = int(start_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        else:
            start_frame = 0

        if end_time is not None:
            end_frame = int(end_time * fps)
        else:
            end_frame = total_frames

        if max_frames:
            end_frame = min(end_frame, start_frame + max_frames)

        frame_count = start_frame
        processed_count = 0
        start_time = time.time()

        while frame_count < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            # 跳帧采样
            if (frame_count - start_frame) % sampling_rate != 0:
                frame_count += 1
                continue

            # 降采样
            small_frame = self.downsample_frame(frame, scale_factor, target_size)

            # 判断是否为关键帧
            if method == Method.MOTION_VECTOR:
                is_key = self.is_keyframe(small_frame, method, threshold,
                                          video_path=video_path,
                                          frame_idx=frame_count)
            else:
                if method == Method.DIFFERENCE:
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                    is_key = self.is_keyframe(gray, method, threshold)
                    if is_key:
                        self.prev_frame = gray
                else:
                    is_key = self.is_keyframe(small_frame, method, threshold)
                    if is_key:
                        self.prev_frame = small_frame

            if is_key:
                self.keyframes.append(frame)  # 保存原始分辨率帧
                self.frame_indices.append(frame_count)

            processed_count += 1
            frame_count += 1

            # ... (其余代码保持不变)

        return self.keyframes, self.frame_indices

# 使用示例
if __name__ == "__main__":
    extractor = AdvancedKeyframeExtractor()

    # 使用运动矢量方法提取关键帧
    keyframes, indices = extractor.extract_keyframes(
        video_path="video.mp4",
        method=Method.MOTION_VECTOR,
        threshold=0.4,  # 运动变化率阈值
        sampling_rate=1,  # 由于依赖运动矢量,建议采样率设为1
        scale_factor=1.0  # 保持原始分辨率以获取准确的运动信息
    )
    extractor.save_keyframes("output/motion_vector_keyframes")

    # 比较多种方法
    extractor.process_video(
        video_path="video.mp4",
        output_dir="output/comparison",
        methods=[Method.DIFFERENCE, Method.SSIM,
                 Method.HISTOGRAM, Method.MOTION_VECTOR],
        sampling_rate=1,
        scale_factor=0.5,
        max_frames=5000
    )