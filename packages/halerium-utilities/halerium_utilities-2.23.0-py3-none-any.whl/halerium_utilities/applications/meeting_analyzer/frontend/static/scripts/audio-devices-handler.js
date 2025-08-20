export class AudioDevicesHandler {
    constructor() {
    }


    /**
     * Fetches available audio input devices and populates the audio input select dropdown.
     */
    async asyncGetAudioInputDevices() {
        let stream = null;
        try {
            // Request permission to access audio input devices
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Enumerate all available devices
            const devices = await navigator.mediaDevices.enumerateDevices();
            const audioInputDevices = devices.filter(device => device.kind === 'audioinput');

            return audioInputDevices;

        } catch (error) {
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            alert('Audio Permissions denied: Please allow access to the microphone to use this feature.');
            }
            console.error('Error accessing audio input devices:', error);
            return [];
        } finally {
            if (stream) {
            stream.getTracks().forEach(track => track.stop());
            }
        }
    }
}