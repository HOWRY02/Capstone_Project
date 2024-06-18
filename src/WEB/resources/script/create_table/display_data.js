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

async function displayFields(boxes) {
    // Select the resultHeading for adjust the font size
    const resultHeading = document.getElementById('resultHeading');

    // Select the display-list div
    const displayListDiv = document.getElementById("display-list");

    // Select the listElement to display the json 
    const listElement = document.getElementById('listElement');
    const titleElement = document.getElementById('titleList');
    const questionElement = document.getElementById('questionList');
    const dateElement = document.getElementById('dateList');
    const answerElement = document.getElementById('answerList');

    // Clear the existing content of all list elements
    titleElement.innerHTML = 'Title';
    questionElement.innerHTML = 'Question';
    dateElement.innerHTML = 'Date';
    answerElement.innerHTML = 'Answer';

    const imageCanvas = document.getElementById('imageCanvas');
    const canvasRect = imageCanvas.getBoundingClientRect();
    const canvasWidth = canvasRect.width;
    const canvasHeight = canvasRect.height;
    // Calculate the scaled size for input elements
    const scaleFactor = Math.min(canvasWidth, canvasHeight) / 500; // Adjust according to your requirements
    displayListDiv.style.fontSize = `${scaleFactor * 12}px`; // Adjust font size based on canvas size
    resultHeading.style.fontSize = `${scaleFactor * 14}px`; // Adjust font size based on canvas size



    boxes.forEach(async item => {
        const listContainer = document.createElement('ul')
        const listItem = document.createElement('li');
        const map = await mapping;
        listItem.textContent = map[item.text] || "Key not found in mapping";
        if (listItem.textContent == "Key not found in mapping") {
            listItem.textContent = item.text;
        };
        if (item.class.includes('title')) {
            //add item.text to the content of titleList as a list
            listContainer.appendChild(listItem)
            titleElement.appendChild(listContainer);
        }

        else if (item.class.includes('question')) {
            //add item.text to the content of titleList as a list
            listContainer.appendChild(listItem)
            questionElement.appendChild(listContainer);
        }

        else if (item.class.includes('date')) {
            //add item.text to the content of titleList as a list
            listContainer.appendChild(listItem)
            dateElement.appendChild(listContainer);
        }
        else if (item.class.includes('answer')) {
            //add item.text to the content of titleList as a list
            listContainer.appendChild(listItem)
            answerElement.appendChild(listContainer);
        }


    });
}

// Function to handle the event
// async function handleEvent() {
//     const jsonData = document.getElementById('templateDisplay').textContent;
//     console.log(jsonData); // Check the content of jsonData

//     try {
//         const parsedData = JSON.parse(jsonData); // Parse the JSON string
//         displayFields(parsedData); // Pass the parsed array to displayFields
//     } catch (error) {
//         console.error('Error parsing JSON:', error);
//     }
// }

// // Add event listener for click
// document.addEventListener('click', handleEvent);
