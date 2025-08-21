(() => {
    /** @param {HTMLElement} element */
    const initTooltips = element => {
        const tooltipTriggerList = element.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    }

    /** @param {HTMLElement} element */
    const destroyTooltips = element => {
        const tooltipTriggerList = element.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => bootstrap.Tooltip.getInstance(tooltipTriggerEl))
        tooltipList.filter(t => !!t).forEach(tooltip => tooltip.dispose())
    }

    if (!window.hasAddedBootstrapTooltips) {
        document.body.addEventListener('htmx:afterSwap', (e) => {
            const el = e.detail.target;
            initTooltips(el);
        });

        document.body.addEventListener('htmx:beforeSwap', (e) => {
            const el = e.detail.target;
            destroyTooltips(el);
        });

        window.hasAddedBootstrapTooltips = true;
    }

    window.onload = () => {
        // Init tooltips for entire document
        initTooltips(document);
    }
})();