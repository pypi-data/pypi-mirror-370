"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video.
"""
from yta_video_opengl.reader.cache import VideoFrameCache
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.input import InputContainer
from fractions import Fraction
from av import open as av_open
from typing import Union
from dataclasses import dataclass


@dataclass
class VideoReaderFrame:
    """
    Class to wrap a frame of a video that is
    being read, that can be a video or audio
    frame, and has been decoded.
    """

    @property
    def is_video(
        self
    ):
        """
        Flag to indicate if the instance is a video
        frame.
        """
        return PythonValidator.is_instance_of(self.value, VideoFrame)
    
    @property
    def is_audio(
        self
    ):
        """
        Flag to indicate if the instance is an audio
        frame.
        """
        return PythonValidator.is_instance_of(self.value, AudioFrame)
    
    @property
    def as_numpy(
        self
    ):
        """
        The frame as a numpy array.
        """
        return self.value.to_ndarray(format = self.pixel_format)
    
    def __init__(
        self,
        # TODO: Add the type, please
        frame: any,
        t: float = None,
        pixel_format: str = 'rgb24'
    ):
        self.value: Union[AudioFrame, VideoFrame] = frame
        """
        The frame content, that can be audio or video
        frame.
        """
        self.t: float = t
        """
        The 't' time moment of the frame.
        """
        self.pixel_format: str = pixel_format
        """
        The pixel format of the frame.
        """

@dataclass
class VideoReaderPacket:
    """
    Class to wrap a packet of a video that is
    being read, that can contain video or audio
    frames.
    """

    @property
    def is_video(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes video
        frames or not.
        """
        return self.value.stream.type == 'video'
    
    @property
    def is_audio(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes audio
        frames or not.
        """
        return self.value.stream.type == 'audio'

    def __init__(
        self,
        packet: Packet
    ):
        self.value: Packet = packet
        """
        The packet, that can include video or audio
        frames and can be decoded.
        """

    def decode(
        self
    ) -> list['SubtitleSet']:
        """
        Get the frames but decoded, perfect to make
        modifications and encode to save them again.
        """
        return self.value.decode()
        

class VideoReader:
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def frame_iterator(
        self
    ) -> 'Iterator[VideoFrame]':
        """
        Iterator to iterate over all the video frames
        decodified.
        """
        return self.container.decode(self.video_stream)
    
    @property
    def next_frame(
        self
    ) -> Union[VideoFrame, None]:
        """
        Get the next video frame (decoded) from the
        iterator.
        """
        return next(self.frame_iterator)

    @property
    def audio_frame_iterator(
        self
    ) -> 'Iterator[AudioFrame]':
        """
        Iterator to iterate over all the audio frames
        decodified.
        """
        return self.container.decode(self.audio_stream)
        
    @property
    def next_audio_frame(
        self
    ) -> Union[AudioFrame, None]:
        """
        Get the next audio frame (decoded) from the
        iterator.
        """
        return next(self.audio_frame_iterator)
    
    @property
    def packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified).
        """
        return self.container.demux(self.video_stream)
    
    @property
    def next_packet(
        self
    ) -> Union[Packet, None]:
        """
        Get the next video packet (not decoded) from
        the iterator.
        """
        return next(self.packet_iterator)
    
    @property
    def audio_packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the audio frames
        as packets (not decodified).
        """
        return self.container.demux(self.audio_stream)
    
    @property
    def next_audio_packet(
        self
    ) -> Union[Packet, None]:
        """
        Get the next audio packet (not decoded) from
        the iterator.
        """
        return next(self.packet_iterator)
    
    @property
    def packet_with_audio_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified) including also the
        audio as packets.
        """
        return self.container.demux((self.video_stream, self.audio_stream))

    @property
    def next_packet_with_audio(
        self
    ) -> Union[Packet, None]:
        """
        Get the next video frames packet (or audio
        frames packet) from the iterator. Depending
        on the position, the packet can be video or
        audio.
        """
        return next(self.packet_with_audio_iterator)

    @property
    def codec_name(
        self
    ) -> str:
        """
        Get the name of the video codec.
        """
        return self.video_stream.codec_context.name
    
    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return self.audio_stream.codec_context.name

    @property
    def number_of_frames(
        self
    ) -> int:
        """
        The number of frames in the video.
        """
        return self.video_stream.frames
    
    @property
    def number_of_audio_frames(
        self
    ) -> int:
        """
        The number of frames in the audio.
        """
        return self.audio_stream.frames
    
    @property
    def fps(
        self
    ) -> Fraction:
        """
        The fps of the video.
        """
        # They return it as a Fraction but...
        return self.video_stream.average_rate
    
    @property
    def audio_fps(
        self
    ) -> Fraction:
        """
        The fps of the audio.
        """
        # TODO: What if no audio (?)
        return self.audio_stream.average_rate
    
    @property
    def time_base(
        self
    ) -> Fraction:
        """
        The time base of the video.
        """
        return self.video_stream.time_base

    @property
    def audio_time_base(
        self
    ) -> Fraction:
        """
        The time base of the audio.
        """
        return self.audio_stream.time_base
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            self.video_stream.width,
            self.video_stream.height
        )
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video, in pixels.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video, in pixels.
        """
        return self.size[1]
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str,
        # Use 'rgba' if alpha channel
        pixel_format: str = 'rgb24'
    ):
        self.filename: str = filename
        """
        The filename of the video source.
        """
        self.pixel_format: str = pixel_format
        """
        The pixel format.
        """
        self.container: InputContainer = None
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self.video_stream: VideoStream = None
        """
        The stream that includes the video.
        """
        # TODO: What if no audio (?)
        self.audio_stream: AudioStream = None
        """
        The stream that includes the audio.
        """
        self.cache: VideoFrameCache = None
        """
        The frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def reset(
        self
    ) -> 'VideoReader':
        """
        Reset all the instances, closing the file
        and opening again.

        This will also return to the first frame.
        """
        if self.container is not None:
            # TODO: Maybe accept forcing it (?)
            self.container.seek(0)
            #self.container.close()
        else:
            self.container = av_open(self.filename)
            # TODO: Should this be 'AUTO' (?)
            self.video_stream = self.container.streams.video[0]
            self.video_stream.thread_type = 'AUTO'
            self.audio_stream = self.container.streams.audio[0]
            self.audio_stream.thread_type = 'AUTO'
            self.cache = VideoFrameCache(self)

    def iterate(
        self
    ) -> 'Iterator[Union[VideoFrame, AudioFrame]]':
        """
        Iterator to iterate over the video frames
        (already decoded).
        """
        for frame in self.frame_iterator:
            yield VideoReaderFrame(
                frame = frame,
                t = float(frame.pts * self.time_base),
                pixel_format = self.pixel_format
            )

    def iterate_with_audio(
        self,
        do_decode_video: bool = True,
        do_decode_audio: bool = False
    ) -> 'Iterator[Union[VideoReaderFrame, VideoReaderPacket, None]]':
        """
        Iterator to iterate over the video and audio
        packets, decoded only if the parameters are
        set as True.

        If the packet is decoded, it will return each
        frame individually as a VideoReaderFrame 
        instance. If not, the whole packet as a
        VideoReaderPacket instance.
        """
        for packet in self.packet_with_audio_iterator:
            is_video = packet.stream.type == 'video'

            do_decode = (
                (
                    is_video and
                    do_decode_video
                ) or
                (
                    not is_video and
                    do_decode_audio
                )
            )

            if do_decode:
                for frame in packet.decode():
                    # Return each frame decoded
                    yield VideoReaderFrame(frame)
            else:
                # Return the packet as it is
                yield VideoReaderPacket(packet)

    # TODO: Will we use this (?)
    def get_frame(
        self,
        index: int
    ) -> 'VideoFrame':
        """
        Get the frame with the given 'index', using
        the cache system.
        """
        return self.cache.get_frame(index)
    
    def close(
        self
    ) -> None:
        """
        Close the container to free it.
        """
        self.container.close()




"""
When reading packets directly from the stream
we can receive packets with size=0, but we need
to process them and decode (or yield them). It
is only when we are passing packets to the mux
when we need to ignore teh ones thar are empty
(size=0).

TODO: Do we need to ignore all? By now, ignoring
not is causing exceptions, and ignoring them is
making it work perfectly.
"""