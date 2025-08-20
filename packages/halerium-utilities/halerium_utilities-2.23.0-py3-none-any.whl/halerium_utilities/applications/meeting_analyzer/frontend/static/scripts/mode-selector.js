class Selector {
  constructor() {
    this.btnUploadFile = document.getElementById("btnUploadFile");
    this.btnRecordMeeting = document.getElementById("btnRecordMeeting");
    this.fileInput = document.querySelector(
      'input[type="file"][name="fileInput"]'
    );
    this.uploadForm = document.getElementById("uploadForm");
    this.uploadProgress = document.getElementById("uploadProgress");
    this.uploadProgressBar = document.getElementById("progressBar");
    this.uploadProgressBarText = document.getElementById("progressText");
    this.init();
  }

  init() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    if (this.btnUploadFile) {
      this.btnUploadFile.addEventListener("click", (event) => {
        event.preventDefault();
        this.fileInput.click();
      });
    }

    if (this.fileInput) {
      this.fileInput.addEventListener("change", () => {
        if (this.fileInput.files.length > 0) {
          this.uploadFiles();
        }
      });
    }
  }

  async uploadFiles() {
    const files = this.fileInput.files;
    if (!files.length) {
      alert("Please select at least one file first.");
      return;
    }

    const formData = new FormData();

    for (const file of files) {
      formData.append("fileInputs", file);
    }

    try {
      this.btnRecordMeeting.disabled = true;
      this.btnRecordMeeting.style.backgroundColor = "#ccc";
      this.btnRecordMeeting.style.borderColor = "#ccc";
      this.btnUploadFile.style.borderColor = "#ccc";
      this.btnUploadFile.disabled = true;
      this.btnUploadFile.style.display = "none";
      this.uploadProgress.style.display = "flex";

      const xhr = new XMLHttpRequest();
      xhr.open("POST", this.uploadForm.action, true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          this.uploadProgressBar.style.width = `${percentComplete}%`;
          this.uploadProgressBarText.textContent = `${Math.round(
            percentComplete
          )}%`;
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const data = xhr.responseText;
          document.open();
          document.write(data);
          document.close();
        } else {
          alert(
            "There was an error uploading the files. Please reload the page and try again."
          );
          throw new Error("Network response was not ok");
        }
      };

      xhr.onerror = () => {
        this.uploadProgress.style.display = "none";
        this.btnUploadFile.display = "block";
      };

      xhr.send(formData);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      // here we could reset all the buttons.
    }
  }
}

// Initialize the Selector class when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  new Selector();
});
