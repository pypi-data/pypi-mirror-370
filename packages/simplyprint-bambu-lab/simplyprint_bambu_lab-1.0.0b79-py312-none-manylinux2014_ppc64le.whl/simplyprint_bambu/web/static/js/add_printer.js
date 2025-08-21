// Included from views/add_printer.html

(() => {
    /** @type {HTMLSelectElement} */
    const modelSelect = document.getElementById('model');

    /** @type {Element|null} */
    let selectedGuide = null;

    /** 
     * @param {string} model 
     * @returns {string|null} Id of guide to show
     */
    const getGuideToShow = model => {
        switch (model) {
            case 'X1C':
            case 'X1':
                return 'guide-x1';
            case 'P1P':
            case 'P1S':
                return 'guide-p1';
            case 'A1':
            case 'A1Mini':
                return 'guide-a1';
            default:
                return null;
        }
    }

    const updateShownGuides = () => {
        const newGuideId = getGuideToShow(modelSelect.value);

        if (selectedGuide && selectedGuide.id !== newGuideId)
            selectedGuide.classList.add('d-none');

        if (newGuideId === null)
            return;

        selectedGuide = document.getElementById(newGuideId);
        selectedGuide?.classList.remove('d-none');
    }

    modelSelect.addEventListener('change', updateShownGuides);
    updateShownGuides();
})();