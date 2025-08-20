export class MarkdownRenderer {
  constructor() {
    try {
      this.renderer = new marked.Renderer();
    } catch (error) {
      console.error("Error creating markdown renderer", error.message);
    }
    this.init();
    this.updateRendererOptions();
  }

  init() {
    this.renderer.link = (result) => {
      return `<a href="${result.href}" title="${result.title}" target="_blank">${result.text}</a>`;
    };

    this.renderer.image = (result) => {
      if (result.href.startsWith("attachment:")) {
        return `<img class="halimg" filename="${result.href}" title="${result.title}" alt="${result.text}" />`;
      }
      return `<img src="${result.href}" title="${result.title}" alt="${result.text}" />`;
    };

    this.renderer.code = (result) => {
      const code = result.text;
      const language = result.lang;

      var btn_ctc =
        '<button class="copy-btn" onclick="window.chatManager.copyToClipboard(this)">Copy code</button>';
      var lang_lbl = `<span class="lang-lbl">${language}</span>`;
      try {
        var escapedCode = this.escapeHTML(code);
      } catch (error) {
        console.error("Error escaping code", error.message);
        var escapedCode = code;
      }
      return `<pre>${lang_lbl}${btn_ctc}<code class=hljs ${language}>${escapedCode}</code></pre>`; // add copy button and language label
    };
    this.renderer.blockquote = (quote) => {
      const text = marked.parse(quote.text);
      return `${text}<br>`; // remove blockquote
    };
  }

  /**
   * Updates the options of the renderer.
   */
  updateRendererOptions() {
    marked.setOptions({ renderer: this.renderer });
  }

  /**
   * Parses the markdown text and returns the HTML.
   * @param {string} text
   * @returns {string} The HTML representation of the markdown text.
   */
  parseMarkdown(text) {
    let parsed = marked.parse(text);
    return parsed;
  }

  /**
   * Escapes HTML special characters in a string.
   * @param {string} str - The string to be escaped.
   * @returns {string} The escaped string.
   */
  escapeHTML(str) {
    return str.replace(/[&<>'"]/g, function (tag) {
      const charsToReplace = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;",
      };
      return charsToReplace[tag] || tag;
    });
  }
}
