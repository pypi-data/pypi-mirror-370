/**
 * Class representing an audio visualizer that draws waveforms on a canvas.
 */
export class AudioVisualizer {
  /**
   * Create an AudioVisualizer.
   * @param {HTMLCanvasElement} canvas - The canvas element where the waveform will be drawn.
   */
  constructor(canvas) {
    this.canvas = canvas;
    this.canvasContext = this.canvas.getContext("2d");
    this.animationFrameId = null;
  }

  /**
   * Draw the waveform on the canvas.
   * @param {AnalyserNode} analyser - The AnalyserNode providing the audio data.
   * @param {number} bufferLength - The length of the data buffer.
   */
  drawWaveform(analyser, bufferLength) {
    const canvasWidth = this.canvas.width;
    const canvasHeight = this.canvas.height;
    const context = this.canvasContext;
    const dataArray = new Uint8Array(bufferLength);

    // Clear the canvas before drawing the new frame
    context.clearRect(0, 0, canvasWidth, canvasHeight);

    // Get the audio data
    analyser.getByteTimeDomainData(dataArray);

    // Set the line width and color
    context.lineWidth = 2;
    context.strokeStyle = "#373bbc";

    // Begin drawing the waveform path
    context.beginPath();

    const sliceWidth = canvasWidth / bufferLength;
    let x = 0;
    const centerY = 40; // Center of the waveform vertically

    // Loop through the data and draw the waveform
    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = v * centerY + centerY;

      if (i === 0) {
        context.moveTo(x, y);
      } else {
        context.lineTo(x, y);
      }

      x += sliceWidth;
    }

    // Stroke the waveform path
    context.stroke();
  }

  /**
   * Start drawing the waveform at a specified frame rate.
   * @param {AnalyserNode} analyser - The AnalyserNode providing the audio data.
   * @param {number} bufferLength - The length of the data buffer.
   */
  startDrawing(analyser, bufferLength) {
    const draw = () => {
      this.drawWaveform(analyser, bufferLength);
      this.animationFrameId = requestAnimationFrame(draw);
    };

    draw();
  }

  /**
   * Stop drawing the waveform.
   */
  stopDrawing() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }
}
