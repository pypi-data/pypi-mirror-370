import lameenc
import logging
from pathlib import Path
import tempfile
import os
from datetime import datetime


class AudioProcessor:
    def __init__(
        self,
        samplerate: int,
        session_id: str,
        output_dir: Path = Path("./audio"),
        temp_dir: Path = Path("./temp"),
        temp_prefix: str = "mma_",
    ):
        """
        Audio manager to manage audio recording's IO.

        Args:
            samplerate (int): Sample rate of audio recording (e.g. 16000).
            session_id (str): Unique identifier for the recording session.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"AudioProcessor instance created for session {session_id}.")

        self.samplerate = samplerate
        self.session_id = session_id

        # setup LAME encoder
        self.encoder = lameenc.Encoder()
        self.encoder.set_bit_rate(128)
        self.encoder.set_in_sample_rate(self.samplerate)
        self.encoder.set_channels(1)
        self.encoder.set_quality(7)

        # setup output and temporary directories and files
        self.output_path = output_dir
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.temp_path = temp_dir
        self.temp_path.mkdir(parents=True, exist_ok=True)
        self.tempfile = tempfile.NamedTemporaryFile(
            delete=False,
            dir=self.temp_path,
            prefix=temp_prefix,
            suffix=".raw",
        )

        # flag to indicate if recording is in progress
        self.is_recording = True

    def write_chunk(self, chunk: bytes):
        """
        Write audio data directly to the temporary file.

        Args:
            chunk (bytes): Audio data to write to the temporary file.
        """
        try:
            # write the chunk to the temporary file and flush the buffer to disk
            self.tempfile.write(chunk)
        except Exception as e:
            self.logger.error(f"Error writing chunk to temporary file: {e}")

    def export_to_mp3(self):
        """
        Stops the recording, encodes the temporary file to MP3, and cleans up.
        """
        self.is_recording = False
        self.tempfile.close()
        try:
            with open(self.tempfile.name, "rb") as raw_audio:
                raw_data = raw_audio.read()
            mp3_data = self.encoder.encode(raw_data)
            mp3_data += self.encoder.flush()

            now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S%f")
            mp3_filepath = self.output_path / f"{now}_{self.session_id}.mp3"

            with open(mp3_filepath, "wb") as mp3_file:
                mp3_file.write(mp3_data)

            self.logger.debug(f"Saved MP3 audio file to {mp3_filepath}")
        except Exception as e:
            self.logger.error(f"Error encoding or saving MP3 file: {e}")
            mp3_filepath = None
        else:
            os.remove(self.tempfile.name)
            self.logger.debug(f"Temporary file {self.tempfile.name} deleted")
        finally:
            return mp3_filepath
