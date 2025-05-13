document.addEventListener('DOMContentLoaded', function() {
    // --- Variables for the main reader ---
    const mainViewerContainer = document.getElementById('pdf-viewer-container');
    const mainLoadingIndicator = document.getElementById('loading-indicator');
    const mainPageNumSpan = document.getElementById('page_num');
    const mainPageCountSpan = document.getElementById('page_count');
    const mainPrevPageButton = document.getElementById('prev-page');
    const mainNextPageButton = document.getElementById('next-page');
    const mainZoomInButton = document.getElementById('zoom-in');
    const mainZoomOutButton = document.getElementById('zoom-out');
    const openFullscreenPageButton = document.getElementById('open-fullscreen-page'); // New button variable

    // --- Breakpoints in px ---
    const PHONE_MAX = 425;  // small phones
    const MOBILE_MAX = 640; // tailwind "sm"
    const TABLET_MAX = 1024; // tailwind "lg"

    // Look for URL overrides like ?mainScale=1.3
    const urlParams = new URLSearchParams(window.location.search);
    const overrideM = parseFloat(urlParams.get('mainScale'));
    // Get initial page number from URL if navigating back from fullscreen
    const initialPageFromUrl = parseInt(urlParams.get('page')) || 1;


    // Get device pixel ratio to improve rendering on high-DPI screens
    const devicePixelRatio = window.devicePixelRatio || 1;

    // Compute initial scale for the main viewer
    function getInitialMainScale() {
        if (!isNaN(overrideM)) {
            return overrideM;
        }
        const w = window.innerWidth;
        if (w <= PHONE_MAX) {
            return 0.59; // higher zoom on very small screens for main viewer
        } else if (w <= MOBILE_MAX) {
            return 1.2;  // improved "mobile" setting for main viewer
        } else if (w <= TABLET_MAX) {
            return 1.5;  // tablets for main viewer
        } else {
            return 1.5;  // desktops for main viewer
        }
    }

    // Initialize main viewer scale
    let mainScale = getInitialMainScale();

    // Main Reader State
    let mainPdfDoc = null;
    let mainPageNum = initialPageFromUrl; // Use initial page from URL
    let mainPageRendering = false;
    let mainPageNumPending = null;
    let mainCanvas = null; // Will be created by renderMainPage
    let mainCtx = null;

    // Get book file URL and book primary key from data attributes
    const bookFileUrl = mainViewerContainer.dataset.bookUrl;
    const bookPk = mainViewerContainer.dataset.bookPk; // Get book PK


    // Specify workerSrc explicitly for PDF.js
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';


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

    // --- Main Reader Functions ---

    /**
     * Renders a specific page of the PDF in the main viewer.
     * @param {number} num - The page number to render.
     */
    function renderMainPage(num) {
        mainPageRendering = true;
        mainLoadingIndicator.classList.remove('hidden'); // Show loading indicator
        if (mainCanvas) mainCanvas.style.display = 'none'; // Hide old canvas during render

        mainPdfDoc.getPage(num).then(function(page) {
            const viewport = page.getViewport({ scale: mainScale });

            // Remove existing canvas before creating a new one
            if (mainCanvas && mainCanvas.parentNode) {
                mainCanvas.remove();
            }

            // Create high-resolution canvas and get its context
            const { canvas: newCanvas, ctx: newCtx } = createHiDPICanvas(viewport.width, viewport.height, devicePixelRatio);
            mainCanvas = newCanvas;
            mainCtx = newCtx;

            mainCanvas.style.display = 'block';
            mainCanvas.style.margin = '0 auto'; // Center the canvas
            mainViewerContainer.appendChild(mainCanvas);

            const renderContext = {
                canvasContext: mainCtx,
                viewport: viewport,
                renderInteractiveForms: true,
                enableWebGL: true // Recommended for quality
            };

            const renderTask = page.render(renderContext);

            renderTask.promise.then(function() {
                mainPageRendering = false;
                mainLoadingIndicator.classList.add('hidden'); // Hide loading indicator
                if(mainCanvas) mainCanvas.style.display = 'block'; // Show new canvas

                if (mainPageNumPending !== null) {
                    renderMainPage(mainPageNumPending);
                    mainPageNumPending = null;
                }
            }).catch(function(error) {
                console.error("Error rendering main page:", error);
                mainPageRendering = false;
                mainLoadingIndicator.classList.add('hidden'); // Hide loading indicator
                // Optionally display an error message in the viewer
                 mainViewerContainer.innerHTML = `
                    <div class="h-full flex items-center justify-center">
                        <div class="text-center p-8">
                            <div class="inline-block text-red-500 mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                            <h3 class="font-serif text-xl font-bold text-slate mb-2">Error Rendering Page</h3>
                            <p class="text-gray-600">${error.message || 'Unknown error'}</p>
                        </div>
                    </div>`;
            });
        }).catch(function(error){
            console.error("Error getting main page " + num + ":", error);
            mainPageRendering = false;
            mainLoadingIndicator.classList.add('hidden'); // Hide loading indicator
             mainViewerContainer.innerHTML = `
                <div class="h-full flex items-center justify-center">
                    <div class="text-center p-8">
                        <div class="inline-block text-red-500 mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                        <h3 class="font-serif text-xl font-bold text-slate mb-2">Error Loading Page</h3>
                        <p class="text-gray-600">${error.message || 'Unknown error'}</p>
                    </div>
                </div>`;
        });
        mainPageNumSpan.textContent = num;
        mainPrevPageButton.disabled = (num <= 1);
        mainNextPageButton.disabled = (num >= mainPdfDoc.numPages);
    }

    function queueRenderMainPage(num) {
        if (mainPageRendering) {
            mainPageNumPending = num;
        } else {
            renderMainPage(num);
        }
    }

    function onMainPrevPage() {
        if (mainPageNum <= 1) return;
        mainPageNum--;
        queueRenderMainPage(mainPageNum);
    }

    function onMainNextPage() {
        if (mainPageNum >= mainPdfDoc.numPages) return;
        mainPageNum++;
        queueRenderMainPage(mainPageNum);
    }

    function mainZoomIn() {
        mainScale += 0.25;
        queueRenderMainPage(mainPageNum);
    }

    function mainZoomOut() {
        if (mainScale <= 0.25) return; // Prevent zooming out too much
        mainScale -= 0.25;
        queueRenderMainPage(mainPageNum);
    }

    // --- Full-screen Page Navigation ---
    function openFullscreenPageHandler() {
        // Construct the URL for the new full-screen reader page
        // Pass book_pk and current page number
        const fullscreenUrl = `/books/fullscreen_reader/?book_pk=${bookPk}&page=${mainPageNum}`;

        // Open the new page in a new tab/window
        window.open(fullscreenUrl, '_blank');
    }

    if (openFullscreenPageButton) {
        openFullscreenPageButton.addEventListener('click', openFullscreenPageHandler);
    }

    // --- Keyboard Navigation Handlers ---
    function handleMainViewerKeydown(e) {
        // Only handle if modal is NOT open (which it isn't anymore)
        switch (e.key) {
            case 'ArrowRight':
                onMainNextPage();
                break;
            case 'ArrowLeft':
                onMainPrevPage();
                break;
            // Add main viewer zoom shortcuts if desired
            // case '+':
            // case '=':
            //     mainZoomIn();
            //     break;
            // case '-':
            // case '_':
            //     mainZoomOut();
            //     break;
        }
    }
    document.addEventListener('keydown', handleMainViewerKeydown);


    // --- Resize Handlers ---
    function handleMainViewerResize() {
        if (!mainPdfDoc) return;

        // Recalculate main scale based on new device width
        mainScale = getInitialMainScale();
        queueRenderMainPage(mainPageNum);
    }
    window.addEventListener('resize', handleMainViewerResize);


    // --- Event Listeners for Controls ---
    // Main Reader Controls
    mainPrevPageButton.addEventListener('click', onMainPrevPage);
    mainNextPageButton.addEventListener('click', onMainNextPage);
    mainZoomInButton.addEventListener('click', mainZoomIn);
    mainZoomOutButton.addEventListener('click', mainZoomOut);

    // Disable right-click context menu on viewer areas
    mainViewerContainer.addEventListener('contextmenu', function(e) { e.preventDefault(); });


    // --- Initial Load for the main reader ---
    mainLoadingIndicator.classList.remove('hidden'); // Show loading indicator initially
    const mainLoadingTaskOptions = {
        url: bookFileUrl,
        cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/cmaps/',
        cMapPacked: true,
        standardFontDataUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/standard_fonts/'
    };

    pdfjsLib.getDocument(mainLoadingTaskOptions).promise.then(function(pdfDoc_) {
        mainPdfDoc = pdfDoc_;
        mainPageCountSpan.textContent = mainPdfDoc.numPages;
        renderMainPage(mainPageNum); // Initial render using initialPageFromUrl
    }).catch(function (reason) {
        console.error("Main PDF loading error:", reason);
        mainLoadingIndicator.classList.add('hidden'); // Hide loading indicator on error
        mainViewerContainer.innerHTML = `
            <div class="h-full flex items-center justify-center">
                <div class="text-center p-8">
                    <div class="inline-block text-red-500 mb-4"><i class="fas fa-exclamation-circle text-5xl"></i></div>
                    <h3 class="font-serif text-xl font-bold text-slate mb-2">Error Loading PDF</h3>
                    <p class="text-gray-600">${reason.message || 'Unknown error'}</p>
                </div>
            </div>`;
    });
});
