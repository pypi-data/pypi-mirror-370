/**
 * Get the URL of the current page
 * @returns {string} - The URL of the current page
 */
export function getUrl() {
  return window.location.href;
}

/**
 * Get the base URL of the current page
 * @example
 * If the URL is https://pro.halerium.com/apps/<uuid4>/8501/<api-endpoint>?param1=value1&param2=value2
 * returns https://pro.halerium.com/apps/<uuid4>/8501/
 * @param {*} p
 * @returns
 */
export function getBaseUrl(p = "", s = "") {
  const url = s == "" ? window.location.href : s;
  const parsedUrl = new URL(url);
  const protocol = p == "" ? parsedUrl.protocol : p;
  const pathComponents = parsedUrl.pathname
    .split("/")
    .filter((component) => component !== "");
  const baseUrl = `${protocol}//${parsedUrl.hostname}/apps/${pathComponents
    .slice(1, 3)
    .join("/")}/`;

  return baseUrl;
}

/**
 * Get the URL parameters of the current page
 * @returns {Object} - Object containing the URL parameters
 * @example
 * If the URL is http://example.com/?param1=value1&param2=value2
 * returns {param1: 'value1', param2: 'value2'}
 **/
export function getUrlParams() {
  // get the url parameters
  const urlParams = new URLSearchParams(window.location.search);
  const params = Array.from(urlParams.entries());
  const paramsDict = {};
  params.forEach((param) => {
    paramsDict[param[0]] = param[1];
  });

  return paramsDict;
}
