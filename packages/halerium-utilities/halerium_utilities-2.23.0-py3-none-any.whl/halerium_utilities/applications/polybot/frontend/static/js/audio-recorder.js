import { getBaseUrl } from "./url-handler.js";

export class AudioRecorder {
  constructor(audioDevices, dataCallbackFunction) {
    this.streams = [];
    this.audioContext = null;
    this.sampleRate = 16000;
    this.analyser = null;
    this.processor = null;
    this.isRecording = false;
    this.isListening = false;
    this.selectedAudioDevices = audioDevices || [];
    this.callback = dataCallbackFunction;

    // if selectedAudioDevices is empty, add the default device
    if (this.selectedAudioDevices.length === 0) {
      console.warn("No audio devices selected. Selecting default device.");
      this.selectedAudioDevices.push("default");
    }

    console.debug(
      "AudioRecorder initialized with audio devices:",
      this.selectedAudioDevices
    );
  }

  async setupAudioStreaming() {
    try {
      // get audio context
      this.audioContext = await this.getAudioContext();

      // get audio streams
      this.streams = await this.getAudioStreams();

      // add and configure analyser for audio visualization
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 512;

      // add audio processor module and create audio worklet node for processing audio
      await this.audioContext.audioWorklet.addModule(
        getBaseUrl() + "static/js/audio-processor.js"
      );
      this.processor = new AudioWorkletNode(
        this.audioContext,
        "audio-processor"
      );

      // connect audio streams to the audio processor and analyser
      this.streams.forEach((stream) => {
        const audioSourceNode =
          this.audioContext.createMediaStreamSource(stream);
        audioSourceNode.connect(this.processor);
        audioSourceNode.connect(this.analyser);
      });

      // get the sample rate
      this.sampleRate = this.audioContext.sampleRate;

      console.debug(
        "Accessing selected audio devices:",
        this.selectedAudioDevices
      );

      return true;
    } catch (error) {
      console.error(`Error accessing selected audio devices: ${error.message}`);
      return false;
    }
  }

  /**
   * Gets the audio context.
   * @returns {Promise<AudioContext>} The audio context.
   */
  async getAudioContext(samplerate = 16000) {
    try {
      console.debug("Getting audio context");

      const newAudioContext = new (window.AudioContext ||
        window.webkitAudioContext)({
        sampleRate: samplerate,
      });
      return newAudioContext;
    } catch (error) {
      console.error(`Error while getting AudioContext: ${error}`);
      return null;
    }
  }

  /**
   * Gets the audio stream for the selected audio input devices.
   * @returns {Promise<MediaStream[]>} The audio streams.
   */
  async getAudioStreams() {
    const streams = [];
    for (const deviceId of this.selectedAudioDevices) {
      console.debug("Getting audio stream for device:", deviceId);

      if (deviceId === "system-audio") {
        // Handle system audio
        streams.push(await this.getSystemAudioStream());
      } else {
        let audioConstraints;
        if (deviceId && deviceId !== "default") {
          audioConstraints = {
            audio: {
              deviceId: { exact: deviceId },
            },
          };
          // for some reason this leads to an OverConstrained error in Safari, so we need to remove the deviceId constraint here
        } else {
          audioConstraints = { audio: true };
        }
        try {
          // Get audio stream for the selected device
          const newStream = await navigator.mediaDevices.getUserMedia(
            audioConstraints
          );

          // check if stream contains audio
          console.debug("Audio stream:", newStream.getAudioTracks()[0].label);

          // add the destination stream to the streams array
          streams.push(newStream);
        } catch (error) {
          switch (error.name) {
            case "NotFoundError":
            case "DevicesNotFoundError":
              alert("No audio input devices found.");
              break;
            case "SourceUnavailableError":
              alert("Audio input device is not available.");
              break;
            case "PermissionDeniedError":
            case "SecurityError":
              alert(
                "Permission denied. Please allow access to the microphone to use this feature."
              );
              break;
            default:
              alert(
                "Error accessing audio stream. Please check your audio input devices."
              );
              break;
          }
          console.error(`Error accessing audio stream: ${error}`);
        }
      }
    }
    return streams;
  }

  /**
   * Gets the system audio stream.
   * @returns {Promise<MediaStream>} The system audio stream.
   */
  async getSystemAudioStream() {
    try {
      const captureStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
        systemAudio: "include",
      });

      // Stop video tracks if any (only want audio)
      captureStream.getVideoTracks().forEach((track) => track.stop());

      // return the destination stream
      return captureStream;
    } catch (error) {
      if (
        error.name === "NotAllowedError" ||
        error.name === "PermissionDeniedError"
      ) {
        alert(
          "Audio Permissions denied: Please allow access to the microphone to use this feature."
        );
      }
      console.error("Error accessing system audio stream:", error);
      throw error;
    }
  }

  /**
   * Sets up audio processing and visualization.
   */
  async startRecording() {
    try {
      // setup the audio processor event handler
      this.processor.port.onmessage = (event) => {
        if (this.isRecording) {
          // convert float32 to int16 (PCM)
          const float32Array = new Float32Array(event.data);
          const int16Array = new Int16Array(float32Array.length);
          for (let i = 0; i < float32Array.length; i++) {
            int16Array[i] = Math.max(
              -32768,
              Math.min(32767, float32Array[i] * 32768)
            );
          }
          // this.wsAudioHandler.sendMessage(int16Array.buffer);
          // console.log(`Recording audio: ${int16Array.length} samples`);
          this.callback(int16Array.buffer);
        } else {
          // console.log('Not recording');
        }
      };
    } catch (error) {
      console.error(`Error recording audio stream: ${error.message}`);
      return;
    }

    // Visualize the audio as waves
    this.bufferLength = this.analyser.frequencyBinCount;

    // update recording status
    this.isRecording = true;
  }

  stopRecording() {
    // Update recording state
    this.isRecording = false;

    // Tell audio processor to stop processing audio
    if (this.processor) {
      this.processor.port.postMessage({ isRecording: this.isRecording });
    }

    // if (this.wsAudioHandler) {
    //   // Send audio-end message via WebSocket
    //   this.wsAudioHandler.sendMessage(JSON.stringify({ type: "audio-end" }));
    // }

    // Stop the media recorder
    if (this.mediaRecorder) {
      this.mediaRecorder.stop();
    }

    // Disconnect the audio processor
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }

    // Close the audio context
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    // Stop the audio streams
    if (this.streams) {
      this.streams.forEach((stream) =>
        stream.getTracks().forEach((track) => track.stop())
      );
      this.streams = [];
    }

    console.debug("Recording stopped");
  }
}
