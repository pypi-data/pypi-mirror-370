import cv2
import numpy as np
from enum import Enum
from typing import List, Tuple, Optional
import os

class Method(Enum):
    DIFFERENCE = "difference"
    SSIM = "ssim"
    HISTOGRAM = "histogram"
    MOTION = "motion"  # 新增运动矢量方法

class MotionVectorExtractor:
    """运动矢量提取与分析类"""

    def __init__(self, block_size: int = 16):
        self.block_size = block_size
        self.prev_gray = None
        self.feature_params = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        self.tracks = []
        self.track_len = 10

    def reset(self):
        """重置状态"""
        self.prev_gray = None
        self.tracks = []

    def compute_motion_magnitude(self, frame: np.ndarray) -> float:
        """
        计算帧间运动量

        Args:
            frame: 输入帧

        Returns:
            运动量大小 (0~1之间的标准化值)
        """
        if frame is None:
            return 0.0

        # 转换为灰度图
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = frame_gray
            return 0.0

        # 检测特征点
        if len(self.tracks) < self.feature_params['maxCorners']:
            points = cv2.goodFeaturesToTrack(
                frame_gray,
                mask=None,
                **self.feature_params
            )
            if points is not None:
                for x, y in points.reshape(-1, 2):
                    self.tracks.append([(x, y)])

        # 如果没有跟踪点，返回0
        if not self.tracks:
            self.prev_gray = frame_gray
            return 0.0

        # 计算光流
        prev_points = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
        curr_points, status, _ = cv2.calcOpticalFlowPyrLK(
            self.prev_gray,
            frame_gray,
            prev_points,
            None,
            **self.lk_params
        )

        # 更新轨迹
        new_tracks = []
        for tr, (x, y), st in zip(self.tracks, curr_points.reshape(-1, 2), status):
            if not st:
                continue
            tr.append((x, y))
            if len(tr) > self.track_len:
                del tr[0]
            new_tracks.append(tr)
        self.tracks = new_tracks

        # 计算运动量
        if curr_points is not None and prev_points is not None and len(curr_points) > 0:
            # 计算点对之间的欧氏距离
            motion_vectors = curr_points.reshape(-1, 2) - prev_points.reshape(-1, 2)
            magnitudes = np.sqrt(np.sum(motion_vectors ** 2, axis=1))

            # 标准化运动量到0~1之间
            avg_magnitude = np.mean(magnitudes)
            normalized_magnitude = min(1.0, avg_magnitude / (self.block_size * 2))

            self.prev_gray = frame_gray
            return normalized_magnitude

        self.prev_gray = frame_gray
        return 0.0

class AdvancedKeyframeExtractor:
    def __init__(self):
        self.reset()
        self.motion_extractor = MotionVectorExtractor()

    def reset(self):
        """重置提取器状态"""
        self.prev_frame = None
        self.prev_hist = None
        self.keyframes = []
        self.frame_indices = []
        self.motion_extractor.reset()

    def is_keyframe(self,
                    current_frame: np.ndarray,
                    method: Method,
                    threshold: float) -> bool:
        """
        判断是否为关键帧

        Args:
            current_frame: 当前帧
            method: 使用的方法
            threshold: 阈值

        Returns:
            是否为关键帧
        """
        if self.prev_frame is None:
            return True

        if method == Method.MOTION:
            motion_magnitude = self.motion_extractor.compute_motion_magnitude(current_frame)
            return motion_magnitude > threshold

        # 其他方法保持不变...

    def extract_keyframes(self,
                          video_path: str,
                          method: Method = Method.MOTION,  # 默认改为运动矢量方法
                          threshold: float = 0.3,  # 运动矢量方法的默认阈值
                          sampling_rate: int = 1,  # 运动检测建议采用较小的采样率
                          scale_factor: float = 0.5,
                          target_size: Optional[Tuple[int, int]] = None,
                          max_frames: Optional[int] = None,
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None
                          ) -> Tuple[List[np.ndarray], List[int]]:
        """
        提取关键帧 (方法逻辑保持不变，但对运动矢量方法做了特别优化)
        """
        self.reset()
        # ... 其余代码保持不变 ...

    def process_video(self,
                      video_path: str,
                      output_dir: str,
                      methods: List[Method],
                      **kwargs):
        """
        使用多种方法处理同一个视频

        为运动矢量方法设置合适的默认参数
        """
        for method in methods:
            print(f"\n使用 {method.value} 方法处理...")

            # 为每种方法创建子目录
            method_dir = os.path.join(output_dir, method.value)

            # 设置合适的阈值
            if method == Method.MOTION:
                threshold = kwargs.get('threshold', 0.3)  # 运动矢量的默认阈值
                sampling_rate = kwargs.get('sampling_rate', 1)  # 运动检测推荐使用较小的采样率
            elif method == Method.DIFFERENCE:
                threshold = kwargs.get('threshold', 30.0)
            elif method == Method.SSIM:
                threshold = kwargs.get('threshold', 0.7)
            else:  # HISTOGRAM
                threshold = kwargs.get('threshold', 0.8)

            # 提取关键帧
            self.extract_keyframes(
                video_path=video_path,
                method=method,
                threshold=threshold,
                sampling_rate=sampling_rate,
                **kwargs
            )

            # 保存关键帧
            self.save_keyframes(
                output_dir=method_dir,
                prefix=f"{method.value}_frame"
            )

# 使用示例
if __name__ == "__main__":
    extractor = AdvancedKeyframeExtractor()

    # 示例1: 使用运动矢量方法
    keyframes, indices = extractor.extract_keyframes(
        video_path="video.mp4",
        method=Method.MOTION,
        threshold=0.3,  # 运动阈值
        sampling_rate=1,  # 运动检测建议使用较小的采样率
        scale_factor=0.5
    )
    extractor.save_keyframes("output/motion_keyframes")

    # 示例2: 对比所有方法
    extractor.process_video(
        video_path="video.mp4",
        output_dir="output/comparison",
        methods=[Method.MOTION, Method.DIFFERENCE, Method.SSIM, Method.HISTOGRAM],
        sampling_rate=1,
        scale_factor=0.5,
        max_frames=5000  # 只处理前5000帧
    )