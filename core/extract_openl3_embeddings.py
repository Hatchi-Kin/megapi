"""
extract_openl3_embeddings.py

This script defines classes and functions for extracting mel spectrograms and embeddings from audio files using the Essentia library and a TensorFlow model. The primary focus is on the MelSpectrogramOpenL3 class, which computes mel spectrograms with specific parameters tailored for OpenL3 embeddings extraction.

Classes:
    MelSpectrogramOpenL3: Computes mel spectrograms from audio files.

Usage:
    To use this script, instantiate the MelSpectrogramOpenL3 class with the desired hop time and call its compute method with the path to an audio file. This will return the mel spectrogram of the audio file, which can then be used for further processing or embeddings extraction.
"""

from pathlib import Path
import essentia.standard as es
import numpy as np
from essentia import Pool


class MelSpectrogramOpenL3:
    """
    A class for computing mel spectrograms from audio files using Essentia.

    Attributes:
        hop_time (float): The hop time in seconds between successive audio frames.
    """

    def __init__(self, hop_time):
        """
        Initializes the MelSpectrogramOpenL3 with specified parameters for audio processing.

        Args:
            hop_time (float): The hop time in seconds between successive audio frames.
        """
        self.hop_time = hop_time

        # Audio processing parameters
        self.sr = 48000
        self.n_mels = 128
        self.frame_size = 2048
        self.hop_size = 242
        self.a_min = 1e-10
        self.d_range = 80
        self.db_ref = 1.0

        # Derived parameters
        self.patch_samples = int(1 * self.sr)
        self.hop_samples = int(self.hop_time * self.sr)

        # Essentia standard algorithms for audio processing
        self.w = es.Windowing(size=self.frame_size, normalized=False)
        self.s = es.Spectrum(size=self.frame_size)
        self.mb = es.MelBands(highFrequencyBound=self.sr / 2,
                             inputSize=self.frame_size // 2 + 1,
                             log=False,
                             lowFrequencyBound=0,
                             normalize="unit_tri",
                             numberBands=self.n_mels,
                             sampleRate=self.sr,
                             type="magnitude",
                             warpingFormula="slaneyMel",
                             weighting="linear")

    def compute(self, audio_file):
        """
        Computes the mel spectrogram for a given audio file.

        Args:
            audio_file (str): The path to the audio file.

        Returns:
            np.ndarray: A numpy array containing the mel spectrogram.
        """
        audio = es.MonoLoader(filename=audio_file, sampleRate=self.sr)()

        batch = []
        for audio_chunk in es.FrameGenerator(audio, frameSize=self.patch_samples, hopSize=self.hop_samples):
            melbands = np.array([self.mb(self.s(self.w(frame))) for frame in es.FrameGenerator(
                audio_chunk, frameSize=self.frame_size, hopSize=self.hop_size, validFrameThresholdRatio=0.5)])
            
            # Logarithmic scaling and normalization
            melbands = 10.0 * np.log10(np.maximum(self.a_min, melbands))
            melbands -= 10.0 * np.log10(np.maximum(self.a_min, self.db_ref))
            melbands = np.maximum(melbands, melbands.max() - self.d_range)
            melbands -= np.max(melbands)

            batch.append(melbands.copy())
        return np.vstack(batch)


class EmbeddingsOpenL3:
    """
    A class for extracting embeddings from audio files using a TensorFlow model.

    Attributes:
        graph_path (Path): The path to the TensorFlow model graph.
        hop_time (float): The hop time in seconds for the embeddings extraction.
        batch_size (int): The size of batches for processing.
        melbands (int): The number of mel bands to use.
    """

    def __init__(self, graph_path, hop_time=1, batch_size=60, melbands=128):
        """
        Initializes the EmbeddingsOpenL3 with specified parameters for embeddings extraction.

        Args:
            graph_path (str): The path to the TensorFlow model graph.
            hop_time (float): The hop time in seconds for the embeddings extraction.
            batch_size (int): The size of batches for processing.
            melbands (int): The number of mel bands to use.
        """
        self.hop_time = hop_time
        self.batch_size = batch_size

        self.graph_path = Path(graph_path)

        # Input and output sizes for the TensorFlow model
        self.x_size = 199
        self.y_size = melbands
        self.squeeze = False

        # Permutation for tensor transposition
        self.permutation = [0, 3, 2, 1]

        # Input and output layer names in the TensorFlow model
        self.input_layer = "melspectrogram"
        self.output_layer = "embeddings"

        # Mel spectrogram extractor
        self.mel_extractor = MelSpectrogramOpenL3(hop_time=self.hop_time)

        # TensorFlow model for embeddings extraction
        self.model = es.TensorflowPredict(graphFilename=str(self.graph_path),
                                          inputs=[self.input_layer],
                                          outputs=[self.output_layer],
                                          squeeze=self.squeeze)

    def compute(self, audio_file):
        """
        Extracts embeddings from an audio file.

        Args:
            audio_file (str): The path to the audio file.

        Returns:
            np.ndarray: A numpy array containing the extracted embeddings.
        """
        mel_spectrogram = self.mel_extractor.compute(audio_file)

        hop_size_samples = self.x_size

        batch = self.__melspectrogram_to_batch(mel_spectrogram, hop_size_samples)

        pool = Pool()
        embeddings = []
        nbatches = int(np.ceil(batch.shape[0] / self.batch_size))
        for i in range(nbatches):
            start = i * self.batch_size
            end = min(batch.shape[0], (i + 1) * self.batch_size)
            pool.set(self.input_layer, batch[start:end])
            out_pool = self.model(pool)
            embeddings.append(out_pool[self.output_layer].squeeze())

        return np.vstack(embeddings)

    def __melspectrogram_to_batch(self, melspectrogram, hop_time):
        """
        Converts a mel spectrogram into a batch of fixed-size patches.

        Args:
            melspectrogram (np.ndarray): The mel spectrogram.
            hop_time (int): The hop time in samples for creating patches.

        Returns:
            np.ndarray: A batch of mel spectrogram patches.
        """
        npatches = int(np.ceil((melspectrogram.shape[0] - self.x_size) / hop_time) + 1)
        batch = np.zeros([npatches, self.x_size, self.y_size], dtype="float32")
        for i in range(npatches):
            last_frame = min(i * hop_time + self.x_size, melspectrogram.shape[0])
            first_frame = i * hop_time
            data_size = last_frame - first_frame

            if data_size <= 0:
                batch = np.delete(batch, i, axis=0)
                break
            else:
                batch[i, :data_size] = melspectrogram[first_frame:last_frame]

        batch = np.expand_dims(batch, 1)
        batch = es.TensorTranspose(permutation=self.permutation)(batch)
        return batch
