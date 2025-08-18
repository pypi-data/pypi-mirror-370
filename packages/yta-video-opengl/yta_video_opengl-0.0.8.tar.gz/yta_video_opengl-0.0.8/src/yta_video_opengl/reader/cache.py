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
from collections import OrderedDict


class VideoFrameCache:
    """
    Class to manage the frames cache of a video
    within a video reader instance.
    """

    @property
    def container(
        self
    ) -> 'InputContainer':
        """
        Shortcut to the video reader instance container.
        """
        return self.reader_instance.container
    
    @property
    def stream(
        self
    ) -> 'VideoStream':
        """
        Shortcut to the video reader instance video
        stream.
        """
        return self.reader_instance.video_stream

    def __init__(
        self,
        reader: 'VideoReader',
        size: int = 50
    ):
        self.reader_instance: 'VideoReader' = reader
        """
        The video reader instance this cache belongs
        to.
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

        # Index key frames
        for packet in self.container.demux(self.stream):
            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

        self.container.seek(0)
        # TODO: Maybe this is better (?)
        #self.reader_instance.reset()

    def _get_frame_by_pts(
        self,
        target_pts
    ):
        """
        Get the frame that has the provided 'target_pts'.

        This method will start decoding frames from the
        most near key frame (the one with the nearer
        pts) until the one requested is found. All those
        frames will be stored in cache.

        This method must be called when the frame 
        requested is not stored in the caché.
        """
        # Look for the most near key frame
        key_frame_pts = max([
            key_frame_pts
            for key_frame_pts in self.key_frames_pts
            if key_frame_pts <= target_pts
        ])

        # Go to the key frame that includes it
        self.container.seek(key_frame_pts, stream = self.stream)

        decoded = None
        for frame in self.container.decode(self.stream):
            # TODO: Could 'frame' be None (?)
            pts = frame.pts
            if pts is None:
                continue

            # Store in cache if needed
            if pts not in self.cache:
                # TODO: The 'format' must be dynamic
                self.cache[pts] = frame.to_ndarray(format = "rgb24")

                # Clean cache if full
                if len(self.cache) > self.size:
                    self.cache.popitem(last = False)

            if pts >= target_pts:
                decoded = self.cache[pts]
                break

        return decoded

    def get_frame(
        self,
        index: int
    ) -> 'VideoFrame':
        """
        Get the frame with the given 'index' from
        the cache.
        """
        # convertir frame_number a PTS (timestamps internos)
        time_base = self.stream.time_base
        fps = float(self.stream.average_rate)
        target_pts = int(index / fps / time_base)

        return (
            self.cache[target_pts]
            if target_pts in self.cache else
            self._get_frame_by_pts(target_pts)
        )
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self