from yta_video_opengl.reader import VideoReader
from yta_video_opengl.writer import VideoWriter
from yta_video_opengl.utils import iterate_stream_frames_demuxing
from yta_validation import PythonValidator
from typing import Union


# TODO: Where can I obtain this dynamically (?)
PIXEL_FORMAT = 'yuv420p'

# TODO: Maybe rename to 'Media' (?)
class Video:
    """
    Class to wrap the functionality related to
    handling and modifying a video.
    """

    @property
    def start_pts(
        self
    ) -> int:
        """
        The start packet time stamp (pts), needed 
        to optimize the packet iteration process.
        """
        return int(self.start / self.reader.time_base)
    
    @property
    def end_pts(
        self
    ) -> Union[int, None]:
        """
        The end packet time stamp (pts), needed to
        optimize the packet iteration process.
        """
        return (
            int(self.end / self.reader.time_base)
            # TODO: What do we do if no duration (?)
            if self.duration is not None else
            None
        )
    
    @property
    def audio_start_pts(
        self
    ) -> int:
        """
        The start packet time stamp (pts), needed 
        to optimize the packet iteration process.
        """
        return int(self.start / self.reader.audio_time_base)
    
    @property
    def audio_end_pts(
        self
    ) -> Union[int, None]:
        """
        The end packet time stamp (pts), needed to
        optimize the packet iteration process.
        """
        return (
            int(self.end / self.reader.audio_time_base)
            # TODO: What do we do if no duration (?)
            if self.duration is not None else
            None
        )
    
    @property
    def duration(
        self
    ):
        """
        The duration of the video.
        """
        return self.end - self.start

    @property
    def frames(
        self
    ):
        """
        Iterator to yield all the frames, one by
        one, within the range defined by the
        'start' and 'end' parameters provided when
        instantiating it.

        This method returns a tuple of 3 elements:
        - `frame` as a `VideoFrame` instance
        - `t` as the frame time moment
        - `index` as the frame index
        """
        for frame in self.reader.get_frames(self.start, self.end):
            yield frame

        for frame in self.reader.get_audio_frames(self.start, self.end):
            yield frame

        # for frame in iterate_stream_frames_demuxing(
        #     container = self.reader.container,
        #     video_stream = self.reader.video_stream,
        #     audio_stream = self.reader.audio_stream,
        #     video_start_pts = self.start_pts,
        #     video_end_pts = self.end_pts,
        #     audio_start_pts = self.audio_start_pts,
        #     audio_end_pts = self.audio_end_pts
        # ):
        #     yield frame

    def __init__(
        self,
        filename: str,
        start: float = 0.0,
        end: Union[float, None] = None
    ):
        self.filename: str = filename
        """
        The filename of the original video.
        """
        # TODO: Detect the 'pixel_format' from the
        # extension (?)
        self.reader: VideoReader = VideoReader(self.filename)
        """
        The pyav video reader.
        """
        self.start: float = start
        """
        The time moment 't' in which the video
        should start.
        """
        self.end: Union[float, None] = (
            # TODO: Is this 'end' ok (?)
            self.reader.duration
            if end is None else
            end
        )
        """
        The time moment 't' in which the video
        should end.
        """
        
    def save_as(
        self,
        filename: str
    ) -> 'Video':
        writer =  VideoWriter(filename)
        #writer.set_video_stream(self.reader.video_stream.codec.name, self.reader.fps, self.reader.size, PIXEL_FORMAT)
        writer.set_video_stream_from_template(self.reader.video_stream)
        writer.set_audio_stream_from_template(self.reader.audio_stream)

        # TODO: I need to process the audio also, so
        # build a method that do the same but for 
        # both streams at the same time
        for frame, t, index in self.frames:
            if PythonValidator.is_instance_of(frame, 'VideoFrame'):
                print(f'Saving video frame {str(index)}, with t = {str(t)}')
                writer.mux_video_frame(
                    frame = frame
                )
            else:
                print(f'Saving audio frame {str(index)} ({str(round(float(t * self.reader.fps), 2))}), with t = {str(t)}')
                writer.mux_audio_frame(
                    frame = frame
                )

        writer.mux_audio_frame(None)
        writer.mux_video_frame(None)

        # TODO: Maybe move this to the '__del__' (?)
        writer.output.close()
        self.reader.container.close()