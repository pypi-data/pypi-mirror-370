/**
 * AudioWorkletProcessor to handle audio processing tasks.
 * This processor handles multiple input channels, copies the input data,
 * sends it to the main thread, and optionally mixes down to mono for output.
 */
class MyAudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.isRecording = false;

        // Listen for messages from the main thread
        this.port.onmessage = (event) => {
            // Check if the message is to start or stop recording
            if (event.data.isRecording !== undefined) {
                this.isRecording = event.data.isRecording;
            }
        };
    }

    /**
     * Processes the audio data.
     * @param {Array} inputs - The input audio data.
     * @param {Array} outputs - The output audio data.
     * @param {Object} parameters - Additional parameters.
     * @returns {boolean} - Indicates whether the processor should remain active.
     */
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        const output = outputs[0];
        const numberOfChannels = input.length;

        // Copy the input data to the output
        for (let channel = 0; channel < output.length; channel++) {
            const outputChannel = output[channel];
            for (let i = 0; i < input[0].length; i++) {
                let sum = 0;
                for (let j = 0; j < numberOfChannels; j++) {
                    sum += input[j][i];
                }

                // Mix down to mono by averaging the channels
                outputChannel[i] = sum / numberOfChannels;
            }
        }

        // Send the mono PCM data to the main thread
        this.port.postMessage(output[0]);

        return true;
    }
}

// Register the processor with the given name
registerProcessor('audio-processor', MyAudioProcessor);
