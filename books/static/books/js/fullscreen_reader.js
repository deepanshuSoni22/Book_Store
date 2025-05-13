document.addEventListener('DOMContentLoaded', function() {
    // --- Variables for the full-screen reader ---
    const fullscreenViewerContainer = document.getElementById('fullscreen-viewer-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const pageNumSpan = document.getElementById('page_num');
    const pageCountSpan = document.getElementById('page_count');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const zoomInButton = document.getElementById('zoom-in');
    const zoomOutButton = document.getElementById('zoom-out');
    const closeFullscreenButton = document.getElementById('close-fullscreen');

    // State for the full-screen reader
    let pdfDoc = null;
    // Use initialPage passed from the Django template
    let pageNum = parseInt(initialPage) || 1;
    let zoomAdjustment = 1.0; // User-controlled zoom factor relative to fit-to-screen
    let pageRendering = false;
    let pageNumPending = null;
    let canvas = null; // Will be created by renderPage
    let ctx = null;

    // Get device pixel ratio to improve rendering on high-DPI screens
    const devicePixelRatio = window.devicePixelRatio || 1;

    // Specify workerSrc explicitly for PDF.js
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';

    // bookPk and bookFileUrl are now available as global variables
    // because they are defined in the <script> tag before this script is loaded.

    if (!bookFileUrl || !bookPk) {
        console.error("Book URL or PK not provided.");
        loadingIndicator.innerHTML = `
            <div class="text-center text-red-500">
                <div class="inline-block mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                <h3 class="font-serif text-xl font-bold mb-2 text-white">Error Loading PDF</h3>
                <p class="text-gray-300">Book details are missing.</p>
            </div>`;
        loadingIndicator.classList.remove('hidden');
        return; // Stop execution if no URL or PK is provided
    }

    // --- Utility Function to create a high-resolution canvas and its context ---
    /**
     * Creates a canvas element, configures it for HiDPI rendering,
     * and returns the canvas and its 2D rendering context.
     * @param {number} w - The desired CSS width of the canvas.
     * @param {number} h - The desired CSS height of the canvas.
     * @param {number} ratio - The devicePixelRatio.
     * @returns {{canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D}}
     */
    function createHiDPICanvas(w, h, ratio) {
        const canvas = document.createElement('canvas');
        canvas.width = Math.floor(w * ratio); // Use Math.floor to avoid fractional pixels
        canvas.height = Math.floor(h * ratio);
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';

        const ctx = canvas.getContext('2d');
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0); // Apply scaling transform for HiDPI

        return { canvas, ctx };
    }

    // --- Reader Functions ---

    /**
     * Renders a specific page of the PDF.
     * @param {number} num - The page number to render.
     */
    function renderPage(num) {
        pageRendering = true;
        loadingIndicator.classList.remove('hidden');
        if (canvas) canvas.style.display = 'none'; // Hide old canvas during render

        pdfDoc.getPage(num).then(function(page) {
            // Calculate base scale to fit the page within the container
            const viewportUnscaled = page.getViewport({ scale: 1 });
            const containerWidth = fullscreenViewerContainer.clientWidth;
            const containerHeight = fullscreenViewerContainer.clientHeight;

            // The container has padding, so the effective space for the canvas is smaller.
            // We want to fit the page *within* the padded area.
            // Let's calculate scale based on container dimensions minus padding.
            const effectiveWidth = containerWidth - (2 * parseFloat(getComputedStyle(fullscreenViewerContainer).paddingLeft)); // 1rem padding left/right
            const effectiveHeight = containerHeight - (parseFloat(getComputedStyle(fullscreenViewerContainer).paddingTop) + parseFloat(getComputedStyle(fullscreenViewerContainer).paddingBottom)); // 1rem top, 6rem bottom padding

            const scaleX = effectiveWidth / viewportUnscaled.width;
            const scaleY = effectiveHeight / viewportUnscaled.height;
            let baseScaleToFit = Math.min(scaleX, scaleY);

             if (baseScaleToFit <= 0) { // Ensure positive scale
                baseScaleToFit = Math.max(scaleX, scaleY, 0.1); // Fallback to a small scale
            }


            const currentRenderScale = baseScaleToFit * zoomAdjustment;
            const viewport = page.getViewport({ scale: currentRenderScale });

            // Remove existing canvas before creating a new one
            if (canvas && canvas.parentNode) {
                canvas.remove();
            }

            // Create high-resolution canvas and get its context
            const { canvas: newCanvas, ctx: newCtx } = createHiDPICanvas(viewport.width, viewport.height, devicePixelRatio);
            canvas = newCanvas;
            ctx = newCtx;

            canvas.style.display = 'block'; // Will be shown after render
            canvas.style.margin = '0 auto'; // Horizontally center
            fullscreenViewerContainer.appendChild(canvas);

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport,
                renderInteractiveForms: true,
                enableWebGL: true // Recommended for quality
            };

            const renderTask = page.render(renderContext);

            renderTask.promise.then(function() {
                pageRendering = false;
                loadingIndicator.classList.add('hidden');
                if (canvas) canvas.style.display = 'block'; // Show new canvas

                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            }).catch(function(error) {
                console.error("Error rendering page:", error);
                pageRendering = false;
                loadingIndicator.classList.add('hidden');
                 fullscreenViewerContainer.innerHTML = `
                    <div class="h-full flex items-center justify-center text-red-500">
                        <div class="text-center p-8">
                            <div class="inline-block mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                            <h3 class="font-serif text-xl font-bold mb-2 text-white">Error Rendering Page</h3>
                            <p class="text-gray-300">${error.message || 'Unknown error'}</p>
                        </div>
                    </div>`;
            });
        }).catch(function(error){
            console.error("Error getting page " + num + ":", error);
            pageRendering = false;
            loadingIndicator.classList.add('hidden');
             fullscreenViewerContainer.innerHTML = `
                <div class="h-full flex items-center justify-center text-red-500">
                    <div class="text-center p-8">
                        <div class="inline-block mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                        <h3 class="font-serif text-xl font-bold mb-2 text-white">Error Loading Page</h3>
                        <p class="text-gray-300">${error.message || 'Unknown error'}</p>
                    </div>
                </div>`;
        });
        pageNumSpan.textContent = num;
        prevPageButton.disabled = (num <= 1);
        nextPageButton.disabled = (num >= pdfDoc.numPages);
    }

    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }

    function onPrevPage() {
        if (pageNum <= 1) return;
        pageNum--;
        queueRenderPage(pageNum);
    }

    function onNextPage() {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    }

    function zoomIn() {
        zoomAdjustment += 0.25;
        queueRenderPage(pageNum);
    }

    function zoomOut() {
        if (zoomAdjustment <= 0.25) return; // Prevent zooming out too much
        zoomAdjustment -= 0.25;
        queueRenderPage(pageNum);
    }

    function closeFullscreen() {
        // Navigate back to the original reader page using bookPk and current pageNum
        // This matches the 'read_book' URL pattern: /books/book/<int:pk>/read/
        const returnUrl = `/books/book/${bookPk}/read/?page=${pageNum}`;
        window.location.href = returnUrl;
    }

    // --- Event Listeners ---
    prevPageButton.addEventListener('click', onPrevPage);
    nextPageButton.addEventListener('click', onNextPage);
    zoomInButton.addEventListener('click', zoomIn);
    zoomOutButton.addEventListener('click', zoomOut);
    if (closeFullscreenButton) {
        closeFullscreenButton.addEventListener('click', closeFullscreen);
    }


    // Keyboard Navigation
    document.addEventListener('keydown', function(e) {
        switch (e.key) {
            case 'ArrowRight':
                onNextPage();
                break;
            case 'ArrowLeft':
                onPrevPage();
                break;
            case '+':
            case '=': // Often used for zoom in
                zoomIn();
                break;
            case '-':
            case '_': // Often used for zoom out
                zoomOut();
                break;
            case 'Escape': // Allow closing with Escape key
                 closeFullscreen();
                 break;
        }
    });

    // Handle Window Resize
    window.addEventListener('resize', function() {
        if (!pdfDoc) return;
        // Reset zoom adjustment to re-fit the page to the new window size
        zoomAdjustment = 1.0;
        queueRenderPage(pageNum);
    });

     // Disable right-click context menu on viewer area
    fullscreenViewerContainer.addEventListener('contextmenu', function(e) { e.preventDefault(); });


    // --- Initial Load ---
    loadingIndicator.classList.remove('hidden'); // Show loading indicator initially
    const loadingTaskOptions = {
        url: bookFileUrl,
        cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/cmaps/',
        cMapPacked: true,
        standardFontDataUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/standard_fonts/'
    };

    pdfjsLib.getDocument(loadingTaskOptions).promise.then(function(pdfDoc_) {
        pdfDoc = pdfDoc_;
        pageCountSpan.textContent = pdfDoc.numPages;
        // pageNum is already set to initialPage from the template
        renderPage(pageNum); // Initial render
    }).catch(function (reason) {
        console.error("PDF loading error:", reason);
        loadingIndicator.classList.add('hidden'); // Hide loading indicator on error
        fullscreenViewerContainer.innerHTML = `
            <div class="h-full flex items-center justify-center">
                <div class="text-center p-8 text-red-500">
                    <div class="inline-block mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                    <h3 class="font-serif text-xl font-bold text-white mb-2">Error Loading PDF</h3>
                    <p class="text-gray-300">${reason.message || 'Unknown error'}</p>
                </div>
            </div>`;
    });

});
