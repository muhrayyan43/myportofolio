/**
 * Experience page, backed by the DRF API at /api/v1/experiences/:
 * paginated list with debounced search, "load more", in-place star
 * toggle, add-experience modal, and delete.
 *
 * Every write (POST/PATCH/DELETE) goes through sendJson(), which sends
 * a JSON body and the X-CSRFToken header. Server data is rendered with
 * textContent only, never innerHTML.
 *
 * Depends on globals loaded by base.html before this deferred script
 * runs: getCookie, debounce, fetchJson (static/js/utils.js) and
 * showToast (static/js/toast.js).
 */
(function () {
    'use strict';

    /** Delay before a search request fires after the last keystroke. */
    const SEARCH_DEBOUNCE_MS = 400;
    /** Placeholder id baked into the URL templates by {% url ... 0 %}. */
    const URL_ID_PLACEHOLDER = '/00000000-0000-0000-0000-000000000000/';

    const MESSAGES = {
        emptyAll: 'Belum ada experience yang ditambahkan.',
        emptySearch: (query) => `Tidak ada hasil untuk "${query}".`,
        loadMore: (loaded, total) => `Muat lebih banyak (${loaded} dari ${total})`,
        loadMoreBusy: 'Memuat...',
        loadMoreRetry: 'Gagal memuat. Coba lagi',
        loadMoreFailed: 'Data berikutnya gagal dimuat. Silakan coba lagi.',
        saving: 'Menyimpan...',
        createSuccess: 'Experience berhasil ditambahkan.',
        deleteSuccess: 'Experience berhasil dihapus.',
        confirmDelete: (title) => `Hapus "${title}"?`,
        networkError: 'Tidak dapat terhubung ke server atau respons tidak valid. Silakan coba lagi.',
    };

    const root = document.getElementById('experience-app');
    if (!root) return;

    const config = {
        listUrl: root.dataset.listUrl,
        detailUrlTemplate: root.dataset.detailUrlTemplate,
        starUrlTemplate: root.dataset.starUrlTemplate,
        editUrlTemplate: root.dataset.editUrlTemplate,
        loginUrl: root.dataset.loginUrl,
        isAuthenticated: root.dataset.isAuthenticated === 'true',
        canEdit: root.dataset.canEdit === 'true',
        canDelete: root.dataset.canDelete === 'true',
    };

    const elements = {
        searchForm: document.getElementById('experience-search-form'),
        searchInput: document.getElementById('experience-search-input'),
        list: document.getElementById('experience-list'),
        loading: document.getElementById('experience-loading'),
        empty: document.getElementById('experience-empty'),
        emptyMessage: document.getElementById('experience-empty-message'),
        error: document.getElementById('experience-error'),
        retryButton: document.getElementById('experience-retry'),
        count: document.getElementById('experience-count'),
        loadMoreWrap: document.getElementById('experience-load-more-wrap'),
        loadMoreButton: document.getElementById('experience-load-more'),
        // Rendered only for users allowed to create data; may be null.
        modal: document.getElementById('experience-form-modal'),
        form: document.getElementById('experience-form'),
    };

    /** Single source of truth for the list. */
    const state = {
        query: '',
        nextUrl: null,       // DRF "next" link; null when on the last page
        isLoading: false,
        totalCount: 0,
        loadedCount: 0,
        loadMoreFailed: false,
        requestId: 0,        // increments per request; stale replies are ignored
    };

    /** In-flight list request, aborted when a newer one starts. */
    let activeController = null;

    // ------------------------------------------------------------------
    // Small helpers
    // ------------------------------------------------------------------

    /**
     * CSRF strategy: SessionAuthentication checks the CSRF token on every
     * POST/PUT/PATCH/DELETE from a logged-in user, so each write sends it
     * in the X-CSRFToken header, read from the csrftoken cookie.
     * @returns {Record<string, string>}
     */
    function csrfHeaders() {
        return { 'X-CSRFToken': getCookie('csrftoken') || '' };
    }

    /**
     * Send a write request to the API.
     * @param {string} url
     * @param {'POST'|'PUT'|'PATCH'|'DELETE'} method
     * @param {Object} [payload] - Sent as JSON when given.
     * @returns {Promise<any>} Parsed response, or null for 204.
     */
    function sendJson(url, method, payload) {
        const headers = csrfHeaders();
        if (payload !== undefined) headers['Content-Type'] = 'application/json';
        return fetchJson(url, {
            method,
            headers,
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
    }

    /**
     * Build a URL for one experience from a template like "/experience/0/star/".
     * @param {string} template
     * @param {number|string} id
     * @returns {string}
     */
    function urlFor(template, id) {
        return template.replace(URL_ID_PLACEHOLDER, `/${encodeURIComponent(id)}/`);
    }

    function currentQuery() {
        return elements.searchInput.value.trim();
    }

    /**
     * Create an element whose text is set via textContent, so server data
     * is always rendered as text and never parsed as HTML (XSS-safe).
     * @param {string} tag
     * @param {string} [className]
     * @param {string} [text]
     * @returns {HTMLElement}
     */
    function createElement(tag, className, text) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text !== undefined && text !== null) element.textContent = text;
        return element;
    }

    /**
     * Format an ISO date as e.g. "Jan 2024" (Indonesian locale).
     * @param {string|null} isoDate
     * @returns {string}
     */
    function formatMonth(isoDate) {
        if (!isoDate) return '';
        const date = new Date(`${isoDate}T00:00:00`);
        if (Number.isNaN(date.getTime())) return isoDate;
        return date.toLocaleDateString('id-ID', { month: 'short', year: 'numeric' });
    }

    // ------------------------------------------------------------------
    // Rendering
    // ------------------------------------------------------------------

    /**
     * Show exactly one of: loading | empty | error | list.
     * @param {'loading'|'empty'|'error'|'list'} name
     */
    function showState(name) {
        elements.loading.classList.toggle('hide', name !== 'loading');
        elements.empty.classList.toggle('hide', name !== 'empty');
        elements.error.classList.toggle('hide', name !== 'error');
        elements.list.classList.toggle('hide', name !== 'list');
        root.setAttribute('aria-busy', String(name === 'loading'));
    }

    /** Sync the "load more" button with the current state. */
    function renderLoadMore() {
        const visible = Boolean(state.nextUrl) && state.loadedCount > 0;
        elements.loadMoreWrap.classList.toggle('hide', !visible);
        if (!visible) return;

        const button = elements.loadMoreButton;
        button.disabled = state.isLoading;
        button.setAttribute('aria-busy', String(state.isLoading));
        if (state.isLoading) {
            button.textContent = MESSAGES.loadMoreBusy;
        } else if (state.loadMoreFailed) {
            button.textContent = MESSAGES.loadMoreRetry;
        } else {
            button.textContent = MESSAGES.loadMore(state.loadedCount, state.totalCount);
        }
    }

    /**
     * Render the star button for a given state.
     * @param {HTMLButtonElement} button
     * @param {boolean} isStarred
     * @param {number} starCount
     */
    function applyStarState(button, isStarred, starCount) {
        const icon = createElement('span', '', '★');
        icon.setAttribute('aria-hidden', 'true');
        button.classList.toggle('is-starred', isStarred);
        button.setAttribute('aria-pressed', String(isStarred));
        button.replaceChildren(
            icon,
            document.createTextNode(isStarred ? ' Unstar ' : ' Star '),
            createElement('span', 'star-count', String(starCount)),
        );
    }

    function buildStarButton(item) {
        const button = createElement('button', 'button button-star');
        button.type = 'button';
        button.dataset.action = 'toggle-star';
        button.dataset.id = item.id;
        applyStarState(button, item.is_starred, item.star_count);
        return button;
    }

    function buildDeleteButton(item) {
        const button = createElement('button', 'button button-danger button-small', 'Hapus');
        button.type = 'button';
        button.dataset.action = 'delete';
        button.dataset.id = item.id;
        button.dataset.title = item.title;
        return button;
    }

    /**
     * Build one experience card from a JSON item.
     * @param {Object} item - One serialized experience from the API.
     * @param {number} index - Absolute position, for the 01, 02 badge.
     * @returns {HTMLElement}
     */
    function buildCard(item, index) {
        const card = createElement('article', 'project-card experience-card');
        card.dataset.id = item.id;

        const top = createElement('div', 'project-card-top');
        top.append(
            createElement('span', 'experience-number', String(index + 1).padStart(2, '0')),
            createElement('span', 'project-year', item.category_display),
        );

        const endLabel = item.ended_at ? formatMonth(item.ended_at) : 'Sekarang';
        const period = `${formatMonth(item.started_at)} – ${endLabel}`;

        const actions = createElement('div', 'card-actions');
        actions.append(buildStarButton(item));
        if (config.canEdit) {
            const editLink = createElement('a', 'button button-small', 'Edit');
            editLink.href = urlFor(config.editUrlTemplate, item.id);
            actions.append(editLink);
        }
        if (config.canDelete) {
            actions.append(buildDeleteButton(item));
        }

        card.append(
            top,
            createElement('h2', 'project-title', item.title),
            createElement('p', 'experience-period', period),
            createElement('p', 'project-description', item.description),
            actions,
        );
        return card;
    }

    /**
     * Append cards to the list without touching those already shown.
     * @param {Object[]} items
     * @param {number} offset - Number of cards already rendered.
     */
    function appendCards(items, offset) {
        const fragment = document.createDocumentFragment();
        items.forEach((item, i) => fragment.append(buildCard(item, offset + i)));
        elements.list.append(fragment);
    }

    // ------------------------------------------------------------------
    // Data loading
    // ------------------------------------------------------------------

    /** First-page URL for the current search: /api/v1/experiences/?title=... */
    function firstPageUrl() {
        const url = new URL(config.listUrl, window.location.origin);
        if (state.query) url.searchParams.set('title', state.query);
        return url;
    }

    /**
     * Load one page of experiences.
     *
     * reset=true starts over at page 1 (initial load, new search, after a
     * create or delete) and replaces the list. reset=false follows the
     * DRF "next" link and appends. Each call gets a request id; a reply
     * that arrives after a newer request started is ignored, and the
     * network request itself is aborted, so a slow old response can never
     * overwrite fresher results.
     *
     * @param {{reset: boolean}} options
     */
    async function loadPage({ reset }) {
        if (!reset && (state.isLoading || !state.nextUrl)) return;

        if (activeController) activeController.abort();
        const controller = new AbortController();
        activeController = controller;
        const requestId = ++state.requestId;

        state.isLoading = true;
        state.loadMoreFailed = false;
        if (reset) {
            state.query = currentQuery();
            state.nextUrl = null;
            state.loadedCount = 0;
            showState('loading');
        }
        renderLoadMore();

        const url = reset ? firstPageUrl() : state.nextUrl;

        try {
            const data = await fetchJson(url, { signal: controller.signal });
            if (requestId !== state.requestId) return;

            const results = Array.isArray(data.results) ? data.results : [];
            if (reset) elements.list.replaceChildren();
            appendCards(results, state.loadedCount);

            state.loadedCount += results.length;
            state.totalCount = Number(data.count) || 0;
            state.nextUrl = data.next || null;
            elements.count.textContent = String(state.totalCount).padStart(2, '0');

            if (state.loadedCount === 0) {
                elements.emptyMessage.textContent = state.query
                    ? MESSAGES.emptySearch(state.query)
                    : MESSAGES.emptyAll;
                showState('empty');
            } else {
                showState('list');
            }
        } catch (error) {
            if (error.name === 'AbortError' || requestId !== state.requestId) return;
            if (reset) {
                showState('error');
            } else {
                // Keep the cards already shown; offer a retry on the button.
                state.loadMoreFailed = true;
                showToast('Gagal memuat', MESSAGES.loadMoreFailed, 'error');
            }
        } finally {
            if (requestId === state.requestId) {
                state.isLoading = false;
                activeController = null;
                renderLoadMore();
            }
        }
    }

    // ------------------------------------------------------------------
    // Star toggle
    // ------------------------------------------------------------------

    /**
     * Toggle the star of one experience in place (no reload).
     * Anonymous visitors are sent to the login page instead.
     * @param {HTMLButtonElement} button
     */
    async function toggleStar(button) {
        if (!config.isAuthenticated) {
            const next = window.location.pathname + window.location.search;
            window.location.href = `${config.loginUrl}?next=${encodeURIComponent(next)}`;
            return;
        }

        button.disabled = true;
        try {
            const data = await sendJson(urlFor(config.starUrlTemplate, button.dataset.id), 'POST');
            applyStarState(button, data.is_starred, data.star_count);
        } catch (error) {
            showToast('Gagal memberi bintang', error.message, 'error');
        } finally {
            button.disabled = false;
        }
    }

    // ------------------------------------------------------------------
    // Delete (owner only; the API answers 403 for everyone else)
    // ------------------------------------------------------------------

    /**
     * DELETE one experience, then reload the list so numbering, the
     * counter and pagination stay consistent.
     * @param {HTMLButtonElement} button
     */
    async function deleteExperience(button) {
        if (!window.confirm(MESSAGES.confirmDelete(button.dataset.title))) return;

        button.disabled = true;
        try {
            await sendJson(urlFor(config.detailUrlTemplate, button.dataset.id), 'DELETE');
            showToast('Berhasil', MESSAGES.deleteSuccess, 'success');
            loadPage({ reset: true });
        } catch (error) {
            showToast('Gagal menghapus', error.message, 'error');
            button.disabled = false;
        }
    }

    // ------------------------------------------------------------------
    // Add-experience modal
    // ------------------------------------------------------------------

    function clearFieldErrors(form) {
        form.querySelectorAll('[data-error-for]').forEach((node) => {
            node.textContent = '';
            node.classList.add('hide');
        });
        form.querySelectorAll('[aria-invalid="true"]').forEach((node) => {
            node.removeAttribute('aria-invalid');
        });
    }

    /**
     * Show DRF validation errors ({"title": ["..."]}) under their inputs.
     * Errors for fields without a slot (e.g. "non_field_errors") go to
     * the general error line.
     * @param {HTMLFormElement} form
     * @param {Record<string, string[]>} errors
     */
    function showFieldErrors(form, errors) {
        const general = form.querySelector('[data-error-for="__all__"]');
        Object.entries(errors).forEach(([field, messages]) => {
            const slot = form.querySelector(`[data-error-for="${CSS.escape(field)}"]`) || general;
            if (slot) {
                slot.textContent = [slot.textContent, ...messages].filter(Boolean).join(' ');
                slot.classList.remove('hide');
            }
            const input = form.elements.namedItem(field);
            if (input && typeof input.setAttribute === 'function') {
                input.setAttribute('aria-invalid', 'true');
            }
        });
    }

    function flattenErrors(errors) {
        return Object.values(errors).flat()
            .filter((message) => typeof message === 'string')
            .join(' ');
    }

    /** Fields sent to the API; optional ones become null when left blank. */
    const FORM_FIELDS = ['title', 'description', 'category', 'thumbnail', 'started_at', 'ended_at'];
    const NULLABLE_FIELDS = new Set(['thumbnail', 'ended_at']);

    /**
     * Read the modal form into a JSON payload. Fields are listed
     * explicitly so the csrfmiddlewaretoken input is never sent as data.
     * @param {HTMLFormElement} form
     * @returns {Object}
     */
    function payloadFromForm(form) {
        const data = new FormData(form);
        return Object.fromEntries(FORM_FIELDS.map((name) => {
            const value = String(data.get(name) ?? '');
            return [name, NULLABLE_FIELDS.has(name) && !value.trim() ? null : value];
        }));
    }

    /**
     * Map a failed save request to the right feedback: 400 shows field
     * errors plus a toast, 403 shows the permission message from the API.
     * @param {HTMLFormElement} form
     * @param {Error & {status?: number, data?: any}} error
     */
    function handleSaveError(form, error) {
        if (error.status === 400 && error.data && typeof error.data === 'object') {
            showFieldErrors(form, error.data);
            showToast('Gagal menyimpan', flattenErrors(error.data), 'error');
        } else if (error.status === 403) {
            showToast('Akses ditolak', error.message, 'error');
        } else {
            showToast('Gagal menyimpan', MESSAGES.networkError, 'error');
        }
    }

    /** Wire the modal form. No-op for roles that don't get the modal. */
    function initCreateForm() {
        const { modal, form } = elements;
        if (!modal || !form) return;

        const submitButton = form.querySelector('button[type="submit"]');
        const submitLabel = submitButton.textContent;

        // Focus the first field when the modal opens.
        modal.addEventListener('toggle', (event) => {
            if (event.newState !== 'open') return;
            const firstField = form.querySelector('input:not([type="hidden"]), textarea, select');
            if (firstField) firstField.focus();
        });

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearFieldErrors(form);
            submitButton.disabled = true;
            submitButton.textContent = MESSAGES.saving;

            try {
                await sendJson(config.listUrl, 'POST', payloadFromForm(form));
                form.reset();
                modal.hidePopover();
                showToast('Berhasil', MESSAGES.createSuccess, 'success');
                loadPage({ reset: true });
            } catch (error) {
                handleSaveError(form, error);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = submitLabel;
            }
        });
    }

    // ------------------------------------------------------------------
    // Event wiring
    // ------------------------------------------------------------------

    // Skip the request when the effective query did not change
    // (e.g. a trailing space typed and deleted).
    const debouncedSearch = debounce(() => {
        if (currentQuery() !== state.query) loadPage({ reset: true });
    }, SEARCH_DEBOUNCE_MS);

    elements.searchInput.addEventListener('input', debouncedSearch);

    elements.searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        debouncedSearch.cancel();
        loadPage({ reset: true });
    });

    elements.retryButton.addEventListener('click', () => loadPage({ reset: true }));
    elements.loadMoreButton.addEventListener('click', () => loadPage({ reset: false }));

    // Cards are rebuilt on each load, so listen on the container
    // (event delegation) instead of on every button.
    elements.list.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;
        if (button.dataset.action === 'toggle-star') toggleStar(button);
        if (button.dataset.action === 'delete') deleteExperience(button);
    });

    initCreateForm();
    loadPage({ reset: true });
})();