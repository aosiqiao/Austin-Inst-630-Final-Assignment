pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

const pdfLinks = {
    1: "https://cdn.glitch.global/54661111-a46b-4532-97ce-f1a5cfe86b4b/article%201.pdf?v=1733405950927",
    2: "https://cdn.glitch.global/54661111-a46b-4532-97ce-f1a5cfe86b4b/article%202.pdf?v=1733406103355",
    3: "https://cdn.glitch.global/54661111-a46b-4532-97ce-f1a5cfe86b4b/article%203.pdf?v=1733406105646",
};


async function loadArticle(articleNumber) {
    const pdfUrl = pdfLinks[articleNumber];
    if (!pdfUrl) {
        console.error(`No URL found for article ${articleNumber}`);
        return;
    }

    await loadPdf(pdfUrl); // Load PDF
    const extractedText = await extractTextFromPdf(pdfUrl); // Extract text
    const keywords = extractKeywords(extractedText); // Extract keywords
    renderWordCloud(keywords); // Render word cloud
}

async function loadPdf(pdfUrl) {
    const pdfViewer = document.getElementById("pdf-viewer");
    pdfViewer.innerHTML = ""; // Clear previous content

    try {
        const pdf = await pdfjsLib.getDocument(pdfUrl).promise;

        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 1.5 });

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        pdfViewer.appendChild(canvas);
        await page.render({ canvasContext: context, viewport }).promise;
    } catch (error) {
        pdfViewer.innerHTML = `<p style="color: red;">Failed to load PDF: ${error.message}</p>`;
        console.error("Error loading PDF:", error);
    }
}

async function extractTextFromPdf(pdfUrl) {
    try {
        const pdf = await pdfjsLib.getDocument(pdfUrl).promise;
        let fullText = '';

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            textContent.items.forEach(item => fullText += item.str + ' ');
        }

        return fullText;
    } catch (error) {
        console.error("Error extracting text from PDF:", error);
        return '';
    }
}

function extractKeywords(text) {
    const stopWords = new Set([
        'the', 'and', 'is', 'in', 'of', 'to', 'a', 'with', 'on', 'for', 'this', 'that', 'it', 'are', 'an', 'as',
        'at', 'by', 'be', 'from', 'or', 'was', 'we', 'you', 'your'
    ]);

    const tokens = text
        .toLowerCase()
        .split(/\s+/) 
        .filter(word => word.length > 3 && !stopWords.has(word) && /^[a-z]+$/.test(word)); 

    const keywordCounts = tokens.reduce((acc, word) => {
        acc[word] = (acc[word] || 0) + 1;
        return acc;
    }, {});

    return Object.entries(keywordCounts).map(([word, count]) => ({
        text: word,
        size: Math.min(50, count * 5) 
    }));
}

function renderWordCloud(words) {
    const width = 600;
    const height = 250;

    const layout = d3.layout.cloud()
        .size([width, height])
        .words(words)
        .padding(5)
        .fontSize(d => d.size)
        .on("end", draw);

    layout.start();

    function draw(words) {
        const wordCloudContainer = document.getElementById('word-cloud');
        wordCloudContainer.innerHTML = ''; 

        d3.select('#word-cloud')
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`)
            .selectAll("text")
            .data(words)
            .enter()
            .append("text")
            .style("font-size", d => `${d.size}px`)
            .style("fill", "#007BFF")
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x}, ${d.y}) rotate(${d.rotate})`)
            .text(d => d.text);
    }
}
