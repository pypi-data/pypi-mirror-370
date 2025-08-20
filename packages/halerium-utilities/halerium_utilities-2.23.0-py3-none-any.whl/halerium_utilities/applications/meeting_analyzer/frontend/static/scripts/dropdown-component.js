export class DropdownComponent {
  constructor(audioDevices, changeAudioSourceCallback) {
    this.toggleDropdown = this.toggleDropdown.bind(this);
    this.handleOutsideClick = this.handleOutsideClick.bind(this);
    this.dropdownMenu = document.querySelector(".dropdownMenu");
    this.dropdownArrow = document.querySelector(".dropdownArrow");
    this.audioDevices = audioDevices;
    this.changeAudioSourceCallback = changeAudioSourceCallback;

    this.init();
  }

  init() {
    this.populateDropdownMenu();
    document
      .querySelector(".dropdownButton")
      .addEventListener("click", this.toggleDropdown);
    document.addEventListener("click", this.handleOutsideClick);
  }

  toggleDropdown(event) {
    event.preventDefault();
    this.dropdownMenu.style.display =
      this.dropdownMenu.style.display === "block" ? "none" : "block";
    this.dropdownArrow.classList.toggle("open");
  }

  handleOutsideClick(event) {
    // if (this.dropdownMenu && !this.dropdownMenu.contains(event.target) && !event.target.matches('.dropdownButton")')) {
    if (!event.target.closest(".dropdown")) {
      this.dropdownMenu.style.display = "none";
      this.dropdownArrow.classList.remove("open");
    }
  }

  populateDropdownMenu() {
    // Populate dropdown menu with available audio input devices
    this.audioDevices.forEach((device) => {
      const label = document.createElement("label");
      label.classList.add("dropdownItem");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = "audioDevice";
      input.value = device.deviceId;
      input.addEventListener("change", this.changeAudioSourceCallback);
      label.appendChild(input);
      label.appendChild(
        document.createTextNode(
          device.label || `Microphone (${device.deviceId.substr(0, 6)}...)`
        )
      );
      this.dropdownMenu.appendChild(label);
    });

    // Add system audio option
    const label = document.createElement("label");
    label.classList.add("dropdownItem");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = "system-audio";
    input.value = "system-audio";
    input.addEventListener("change", this.changeAudioSourceCallback);
    label.appendChild(input);
    label.appendChild(document.createTextNode("System audio"));
    this.dropdownMenu.appendChild(label);

    // autoselect the default value in the dropdown if there, else, select the first item
    // on macOS and iOS, there is no default device, so select the first item
    const defaultInput = document.querySelector(
      '.dropdownItem input[value="default"]'
    );
    console.log("defaultInput:", defaultInput);
    if (defaultInput) {
      defaultInput.checked = true;
    } else {
      const firstInput = document.querySelector(".dropdownItem input");
      firstInput.checked = true;
    }

    // set the width of the dropdown menu to the width of the button
    const buttonWidth = document.querySelector(".dropdownButton").offsetWidth;
    this.dropdownMenu.style.width = `${buttonWidth}px`;
  }
}
