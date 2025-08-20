class TandA {
  constructor() {
    this.btnTranscribeAnalyzeFiles = document.getElementById(
      "btnTranscribeAnalyzeFiles"
    );
    this.divFileNames = document.querySelectorAll(".fileName");
    this.busyProgress = document.getElementById("busyProgress");
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.sessionId = document.getElementById(
      "btnTranscribeAnalyzeFiles"
    ).dataset.sessionid;
  }

  setupEventListeners() {
    if (this.btnTranscribeAnalyzeFiles) {
      this.btnTranscribeAnalyzeFiles.addEventListener("click", (event) => {
        event.preventDefault();
        this.sendForTandA();
      });
    }
  }

  async sendForTandA() {
    // get all file names from the divs
    this.divFileNames = document.querySelectorAll(".fileName");
    const fileNames = [];
    for (const divFileName of this.divFileNames) {
      fileNames.push(divFileName.textContent);
    }

    if (!fileNames.length) {
      alert("Please upload and select a file first.");
      return;
    }

    const formData = new FormData();
    fileNames.forEach((fileName) => {
      formData.append("fileNames", fileName);
    });

    // display a busy bar
    this.busyProgress.style.display = "flex";

    // hide the button
    this.btnTranscribeAnalyzeFiles.style.display = "none";

    try {
      const response = await fetch(
        `upload/${this.sessionId}/transcribe_and_analyze_files`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.text();
      document.open();
      document.write(data);
      document.close();
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while transcribing and analyzing the files.");

      // hide the busy bar
      this.busyProgress.style.display = "none";

      // show the button
      this.btnTranscribeAnalyzeFiles.style.display = "block";
    }
  }
}

// Initialize the Selector class when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  new TandA();
});
