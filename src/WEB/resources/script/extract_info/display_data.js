
// Function to fetch JSON data from the FastAPI endpoint
async function fetchMappingData() {
    try {
        // Make a GET request to the endpoint /get-mapping
        const response = await fetch('/get-mapping');

        // Check if the request was successful
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Parse the JSON data from the response and return it
        return await response.json();
    } catch (error) {
        // Handle any errors that occur during the fetch operation
        console.error('Error fetching JSON data:', error);
        return null;
    }
}
mapping = fetchMappingData()
console.log(mapping)


function displayFields(boxes) {
    const container = document.getElementById('displayContainer');
    const imageCanvas = document.getElementById('imageCanvas');
    const canvasRect = imageCanvas.getBoundingClientRect();
    const canvasWidth = canvasRect.width;
    const canvasHeight = canvasRect.height;
    // Calculate the scaled size for input elements
    const scaleFactor = Math.min(canvasWidth, canvasHeight) / 500; // Adjust according to your requirements
    container.style.fontSize = `${scaleFactor * 12}px`; // Adjust font size based on canvas size
    // Clear previous content
    container.innerHTML = '<h2>EXTRACTED INFORMATION</h2>';

    boxes.forEach(async item => {
        const fieldContainer = document.createElement('div');
        fieldContainer.className = 'field-container';

        const fixedText = document.createElement('span');
        fixedText.className = 'fixed-text';
        console.log(item.text);

        try {
            const map = await mapping;
            const replacedValue = map[item.text] || "Key not found in mapping";
            fixedText.textContent = replacedValue + ': ' + item.ocr_text;
        } catch (error) {
            console.error("Error:", error);
        }

        fieldContainer.appendChild(fixedText);
        container.appendChild(fieldContainer);
    });
}

// Function to handle the event
async function handleEvent() {
    const jsonData = document.getElementById('templateDisplay').textContent;
    console.log(jsonData); // Check the content of jsonData

    try {
        const parsedData = JSON.parse(jsonData); // Parse the JSON string
        displayFields(parsedData); // Pass the parsed array to displayFields
    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
}

// Add event listener for click
document.addEventListener('click', handleEvent);
