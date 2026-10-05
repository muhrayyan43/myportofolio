/**
 * Shared front-end helpers, loaded on every page from base.html.
 *
 * Everything here is a plain function declaration on purpose: classic
 * <script> tags share one global scope, so a top-level `const`/`let`
 * here would throw a redeclaration error the moment a page script
 * reused the same name.
 */

/**
 * Read a cookie value by name.
 * @param {string} name - Cookie name, e.g. "csrftoken".
 * @returns {string|null} Decoded value, or null when absent.
 */
function getCookie(name) {
    if (!document.cookie) return null;
    const prefix = `${name}=`;
    for (const raw of document.cookie.split(';')) {
        const cookie = raw.trim();
        if (cookie.startsWith(prefix)) {
            return decodeURIComponent(cookie.slice(prefix.length));
        }
    }
    return null;
}

/**
 * Escape HTML-special characters so a value renders as text.
 * Quotes are escaped too because values may land inside attributes.
 * @param {*} value - Any value; null/undefined become "".
 * @returns {string}
 */
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

/**
 * Delay calls to `fn` until `delay` ms have passed without a new call.
 * The returned function exposes `.cancel()` to drop a pending call
 * (used when the user presses Enter and wants results immediately).
 * @param {Function} fn
 * @param {number} delay - Milliseconds.
 * @returns {Function & {cancel: Function}}
 */
function debounce(fn, delay) {
    let timerId;
    function debounced(...args) {
        clearTimeout(timerId);
        timerId = setTimeout(() => fn.apply(this, args), delay);
    }
    debounced.cancel = function () {
        clearTimeout(timerId);
    };
    return debounced;
}

/**
 * fetch() wrapper that always resolves to parsed JSON or throws.
 *
 * - Sends `Accept: application/json` so views can tell AJAX apart.
 * - Reads the body as text first, so a non-JSON reply (e.g. Django's
 *   HTML 403 page on a CSRF failure) never crashes JSON.parse.
 * - On a non-2xx status, throws an Error carrying `status` and the
 *   parsed `data` (e.g. validation errors) for the caller to inspect.
 * - AbortError from an AbortController signal propagates unchanged.
 *
 * @param {string|URL} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>} Parsed JSON body.
 */
async function fetchJson(url, options = {}) {
    const { headers = {}, ...rest } = options;
    const response = await fetch(url, {
        credentials: 'same-origin',
        ...rest,
        headers: { Accept: 'application/json', ...headers },
    });

    const raw = await response.text();
    let data = null;
    if (raw) {
        try {
            data = JSON.parse(raw);
        } catch (parseError) {
            data = null;
        }
    }

    if (!response.ok) {
        const error = new Error(
            (data && data.message) || `Permintaan gagal (status ${response.status}).`
        );
        error.status = response.status;
        error.data = data;
        throw error;
    }

    if (data === null) {
        const error = new Error('Respons server tidak dapat dibaca.');
        error.status = response.status;
        throw error;
    }

    return data;
}