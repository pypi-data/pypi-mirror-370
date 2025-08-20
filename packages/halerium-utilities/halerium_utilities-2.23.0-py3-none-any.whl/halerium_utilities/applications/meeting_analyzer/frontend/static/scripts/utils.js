function getBaseUrl(p="") {
    const url = window.location.href;
    const parsedUrl = new URL(url);
    const protocol = p == "" ? parsedUrl.protocol : p;
    const hostname = parsedUrl.hostname;
    const pathname = parsedUrl.pathname;
    const pathComponents = pathname.split('/').filter(component => component !== '');
    const baseUrl = `${protocol}//${hostname}/apps/${pathComponents.slice(1, 3).join('/')}/`;

    return baseUrl;
}

export { getBaseUrl };