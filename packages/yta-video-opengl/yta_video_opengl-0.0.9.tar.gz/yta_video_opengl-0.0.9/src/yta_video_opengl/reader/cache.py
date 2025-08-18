"""
The pyav container stores the information based
on the packets timestamps (called 'pts'). Some
of the packets are considered key_frames because
they include those key frames.

Also, this library uses those key frames to start
decodifying from there to the next one, obtaining
all the frames in between able to be read and
modified.

This cache system will look for the range of 
frames that belong to the key frame related to the
frame we are requesting in the moment, keeping in
memory all those frames to be handled fast. It
will remove the old frames if needed to use only
the 'size' we set when creating it.
"""
from yta_video_opengl.utils import t_to_pts, pts_to_t, pts_to_index
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from yta_validation.parameter import ParameterValidator
from fractions import Fraction
from collections import OrderedDict
from typing import Union


class VideoFrameCache:
    """
    Class to manage the frames cache of a video
    within a video reader instance.
    """

    @property
    def fps(
        self
    ) -> float:
        """
        The frames per second as a float.
        """
        return (
            float(self.stream.average_rate)
            if self.stream.type == 'video' else
            float(self.stream.rate)
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the stream.
        """
        return self.stream.time_base

    def __init__(
        self,
        container: InputContainer,
        stream: Union[VideoStream, AudioStream],
        size: int = 50
    ):
        ParameterValidator.validate_mandatory_instance_of('container', container, InputContainer)
        ParameterValidator.validate_mandatory_instance_of('stream', stream, [VideoStream, AudioStream])
        ParameterValidator.validate_mandatory_positive_int('size', size)

        self.container: InputContainer = container
        """
        The pyav container.
        """
        self.stream: Union[VideoStream, AudioStream] = stream
        """
        The pyav stream.
        """
        self.cache: OrderedDict = OrderedDict()
        """
        The cache ordered dictionary.
        """
        self.size = size
        """
        The size (in number of frames) of the cache.
        """
        self.key_frames_pts: list[int] = []
        """
        The list that contains the timestamps of the
        key frame packets, ordered from begining to
        end.
        """

        self._prepare()

    def _prepare(
        self
    ):
        # Index key frames
        for packet in self.container.demux(self.stream):
            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

        self.container.seek(0)

    def _get_nearest_keyframe_fps(
        self,
        pts: int
    ):
        """
        Get the fps of the keyframe that is the
        nearest to the provided 'pts'. Useful to
        seek and start decoding frames from that
        keyframe.
        """
        return max([
            key_frame_pts
            for key_frame_pts in self.key_frames_pts
            if key_frame_pts <= pts
        ])

    def _get_frame_by_pts(
        self,
        pts: int
    ):
        """
        Get the frame that has the provided 'pts'.

        This method will start decoding frames from the
        most near key frame (the one with the nearer
        pts) until the one requested is found. All those
        frames will be stored in cache.

        This method must be called when the frame 
        requested is not stored in the caché.
        """
        # Look for the most near key frame
        key_frame_pts = self._get_nearest_keyframe_fps(pts)

        # Go to the key frame that includes it
        self.container.seek(key_frame_pts, stream = self.stream)

        decoded = None
        for frame in self.container.decode(self.stream):
            # TODO: Could 'frame' be None (?)
            if frame.pts is None:
                continue

            # Store in cache if needed
            if frame.pts not in self.cache:
                # TODO: The 'format' must be dynamic
                self.cache[frame.pts] = frame.to_ndarray(format = "rgb24")

                # Clean cache if full
                if len(self.cache) > self.size:
                    self.cache.popitem(last = False)

            if frame.pts >= pts:
                decoded = self.cache[frame.pts]
                break

        return decoded

    def get_frame(
        self,
        index: int
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the frame with the given 'index' from
        the cache.
        """
        # TODO: Maybe we can accept 't' and 'pts' also
        target_pts = int(index / self.fps / self.time_base)

        return (
            self.cache[target_pts]
            if target_pts in self.cache else
            self._get_frame_by_pts(target_pts)
        )

    def get_frames(
        self,
        start: float = 0,
        end: Union[float, None] = None
    ):
        """
        Get all the frames in the range between
        the provided 'start' and 'end' time in
        seconds.
        """
        # TODO: I create this method by default using
        # the cache. Think about how to implement it
        # and apply it here, please.
        # Go to the nearest key frame
        start = t_to_pts(start, self.time_base)
        end = (
            t_to_pts(end, self.time_base)
            if end is not None else
            None
        )
        key_frame_pts = self._get_nearest_keyframe_fps(start)

        # Go to the nearest key frame to start decoding
        self.container.seek(key_frame_pts, stream = self.stream)

        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                if frame.pts is None:
                    continue

                if frame.pts < start:
                    continue

                if (
                    end is not None and
                    frame.pts > end
                ):
                    return
                
                # TODO: Maybe send a @dataclass instead (?)
                yield (
                    frame,
                    pts_to_t(frame.pts, self.time_base),
                    pts_to_index(frame.pts, self.time_base, self.fps)
                )
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self