// Variables to store the current mode
let currentMode = 'title'; // Default mode is 'title'
let colorTitle = 'red';
let colorQuestion = 'green';
let colorDate = 'blue';
let currentColor = colorTitle;

// Function to set the current mode
function setMode(mode, color) {
  currentMode = mode;
  currentColor = color
  draw();
}

// Event listener for input element to load JSON file
const loadInput = document.getElementById('loadInput');
loadInput.addEventListener('change', loadBoxes); // When the file input changes, trigger the loadBoxes function

// Event listener for saving boxes when a button is clicked
const saveButton = document.getElementById('saveButton');
saveButton.addEventListener('click', saveBoxes); // When the button is clicked, trigger the saveBoxes function

// Select the buttons
const titleButton = document.getElementById('titleButton');
const questionButton = document.getElementById('questionButton');
const dateButton = document.getElementById('dateButton');
const submitButton = document.getElementById('submitButton');

// Event listener for the 'Title Mode' button
titleButton.addEventListener('click', function () {
  setMode('title', colorTitle); // Set mode to 'title' with red color
});

// Event listener for the 'Question Mode' button
questionButton.addEventListener('click', function () {
  setMode('question', colorQuestion); // Set mode to 'question' with green color
});

// Event listener for the 'Question Mode' button
dateButton.addEventListener('click', function () {
  setMode('date', colorDate); // Set mode to 'date' with violet color
});

// Function to save boxes to a JSON file
function saveBoxes() {

  console.log(boxes)

  const boxesToSave = boxes.map(box => {

    let topLeftX, topLeftY, bottomRightX, bottomRightY;

    if (box.width > 0 && box.height > 0) {
      topLeftX = box.startX;
      topLeftY = box.startY;
      bottomRightX = box.startX + box.width;
      bottomRightY = box.startY + box.height;
    } else if (box.width > 0 && box.height < 0) {
      topLeftX = box.startX;
      topLeftY = box.startY + box.height;
      bottomRightX = box.startX + box.width;
      bottomRightY = box.startY;
    } else if (box.width < 0 && box.height < 0) {
      topLeftX = box.startX + box.width;
      topLeftY = box.startY + box.height;
      bottomRightX = box.startX;
      bottomRightY = box.startY;
    } else {
      topLeftX = box.startX + box.width;
      topLeftY = box.startY;
      bottomRightX = box.startX;
      bottomRightY = box.startY + box.height;
    }

    return { box: [topLeftX, topLeftY, bottomRightX, bottomRightY], text: box.text, class: box.class }
  });

  // Convert boxes data to JSON string
  const dataToSave = JSON.stringify(boxesToSave);

  // Create a Blob (Binary Large Object) containing the JSON data
  const blob = new Blob([dataToSave], { type: 'application/json' });

  // Create a URL for the Blob
  const url = URL.createObjectURL(blob);

  // Create an anchor element to trigger the file download
  const a = document.createElement('a');
  a.href = url;
  a.download = 'boxes.json'; // Set the filename for downloaded file
  document.body.appendChild(a);
  a.click(); // Simulate a click on the anchor element to initiate download
  document.body.removeChild(a); // Remove the anchor element
  URL.revokeObjectURL(url); // Revoke the object URL to free up resources
}

// Function to load boxes data from a JSON file
function loadBoxes(event) {
  const file = event.target.files[0]; // Get the selected file

  if (file) {
    const reader = new FileReader(); // Create a FileReader object

    reader.onload = function (e) {
      const loadedData = JSON.parse(e.target.result); // Parse loaded JSON data

      // Load boxes with their associated text from the loaded data
      boxes = loadedData.map(data => ({
        startX: data.box[2],
        startY: data.box[3],
        width: data.box[0] - data.box[2],
        height: data.box[1] - data.box[3],
        text: data.text || '', // Ensure text property exists or set it to an empty string
        class: data.class
      }));
      draw();
    };
    reader.readAsText(file); // Read the contents of the file as text
  }
}

// Event listener for the text input field to update box text on pressing Enter
const inputText = document.getElementById('textInput');
inputText.addEventListener('keypress', function (e) {
  // Check if the 'Enter' key is pressed
  if (e.key === 'Enter') {
    // Check if a box is selected and the input text is not empty
    if (selectedBox !== null && inputText.value.trim() !== '') {
      selectedBox.text = inputText.value.trim(); // Update the selected box text
      inputText.style.display = 'none'; // Hide text input after saving text
      draw();
    }
  }
});
