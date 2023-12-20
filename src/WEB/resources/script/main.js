const imageInput = document.getElementById('imageInput');
const imageCanvas = document.getElementById('imageCanvas');
const ctx = imageCanvas.getContext('2d');
const formImage = document.getElementById("formImage");
const imgSrc = formImage.src;
const boxesString = document.getElementById("hiddenJsonData").textContent.replace(/'/g, '"');
const boxesTemp = JSON.parse(boxesString);
const removeThreshold = 5;

const loadInput = document.getElementById('loadInput');
const saveButton = document.getElementById('saveButton');
const titleButton = document.getElementById('titleButton');
const questionButton = document.getElementById('questionButton');
const dateButton = document.getElementById('dateButton');
const submitButton = document.getElementById('submitButton');
const textInput = document.getElementById('textInput');
const createButton = document.getElementById('createButton');

let img = new Image();
let realImgSrc;
let isSubmiting = true;
let isDragging = false; // Flag to track dragging action
let mouseX, mouseY;
let selectedBox = null;
let boxes = []; // Array to store box coordinates
let resizingBox = null; // Variable to track the box being resized
let isResizing = false; // Flag to track resize status

// Variables to store the current mode
let currentMode = 'title'; // Default mode is 'title'
let colorTitle = 'red';
let colorQuestion = 'green';
let colorDate = 'blue';
let currentColor = colorTitle;

tempImg = new Image();
tempImg.onload = function () {
  // Setting the canvas dimensions to match the loaded image
  imageCanvas.width = tempImg.width;
  imageCanvas.height = tempImg.height;

  adjustInputElementsSize(); // Call function to adjust input elements size
  // Drawing the image on the canvas
  ctx.drawImage(tempImg, 0, 0, tempImg.width, tempImg.height);
};
tempImg.src = imgSrc;

boxes = boxesTemp.map(data => ({
  startX: data.box[2],
  startY: data.box[3],
  width: data.box[0] - data.box[2],
  height: data.box[1] - data.box[3],
  text: data.text || '', // Ensure text property exists or set it to an empty string
  class: data.class
}));

// Adding an event listener to 'imageInput' element when a file is selected
imageInput.addEventListener('change', function (event) {
  // delete Allboxes if there are any 
  deleteAllBoxes()
  // Retrieving the selected file
  const file = event.target.files[0];

  // Checking if a file is selected
  if (file) {
    // Creating a new instance of FileReader
    const reader = new FileReader();

    // Event triggered when FileReader finishes reading the file
    reader.onload = function (e) {
      // Creating a new Image object
      imgFile = new Image();

      // Event triggered when the image has finished loading
      imgFile.onload = function () {
        // Setting the canvas dimensions to match the loaded image
        imageCanvas.width = imgFile.width;
        imageCanvas.height = imgFile.height;

        adjustInputElementsSize(); // Call function to adjust input elements size
        // Drawing the image on the canvas
        ctx.drawImage(imgFile, 0, 0, imgFile.width, imgFile.height);
      };

      // Setting the source of the image to the result of FileReader
      imgFile.src = e.target.result;
      realImgSrc = imgFile.src;
    };

    // Reading the selected file as a data URL
    reader.readAsDataURL(file);
    isSubmiting = false;
  }
});

// Adding a mousedown event listener to the imageCanvas
imageCanvas.addEventListener('mousedown', (e) => {
  // Getting the position of the canvas relative to the viewport
  const rect = imageCanvas.getBoundingClientRect();

  // Calculating the mouse coordinates relative to the canvas
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;

  // Determining the type of action and the index of the box based on the mouse coordinates
  const { type, boxIndex } = findHandle(mouseX, mouseY);

  // Handling different actions based on the detected type
  if (type === 'resize') {
    // If a resize action is detected
    isDragging = false;
    isResizing = true;
    resizingBox = boxes[boxIndex]; // Getting the box to be resized
    selectedBox = resizingBox; // Selecting the box when clicking on the resize handle
  } else if (type === 'drag') {
    // If a drag action is detected
    isDragging = true;
    selectedBox = boxes[boxIndex]; // Selecting the box to be dragged
  } else {
    // If neither resize nor drag action is detected
    if (selectedBox !== null && selectedBox === boxes[boxIndex]) {
      // If the clicked box is already selected, deselect it
      selectedBox = null;
    } else {
      // If a new box creation action is detected
      isDragging = true;
      // Creating a new box at the clicked position with initial dimensions
      const box = { startX: Math.round(mouseX), startY: Math.round(mouseY),
                    width: 0, height: 0, class: currentMode };
      boxes.push(box); // Adding the new box to the boxes array
      selectedBox = box; // Setting the newly created box as selected
    }
  }
  draw();
});

// Function handling mouse movement on the imageCanvas
imageCanvas.addEventListener('mousemove', (e) => {
  // Getting the position of the canvas relative to the viewport
  const rect = imageCanvas.getBoundingClientRect();

  // Calculating the mouse coordinates relative to the canvas
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;

  // Checking if dragging action is ongoing
  if (isDragging) {
    // Handling box movement or resizing based on the action type
    if (selectedBox !== null && !isResizing) {
      // If dragging a box (not resizing)
      const dx = mouseX - selectedBox.startX;
      const dy = mouseY - selectedBox.startY;

      // Updating box position and dimensions based on mouse movement
      selectedBox.startX = Math.round(mouseX);
      selectedBox.startY = Math.round(mouseY);
      selectedBox.width -= Math.round(dx);
      selectedBox.height -= Math.round(dy);
    } else if (isResizing && resizingBox !== null) {
      // If resizing a box
      // Calculating and updating the resized box dimensions based on mouse movement
      resizingBox.width = Math.round(Math.max(0, mouseX - resizingBox.startX));
      resizingBox.height = Math.round(Math.max(0, mouseY - resizingBox.startY));
    }
    draw();
  }
});

// Adding comment to the event listener for 'mouseup' on imageCanvas
imageCanvas.addEventListener('mouseup', () => {
  // Check if dragging or resizing is in progress
  if (isDragging || isResizing) {
    isDragging = false;
    isResizing = false;
    resizingBox = null;

    // Update text for the selected box if it exists and the input text is not empty
    const textInput = document.getElementById('textInput');
    if (selectedBox !== null && textInput.value.trim() !== '') {
      selectedBox.text = textInput.value.trim();
      textInput.style.display = 'none'; // Hide text input after saving text
    }
    draw();
  }
  removeSmallBoxes() // Remove small boxes after the mouse is released
});

// Function to handle the contextmenu event on the imageCanvas
imageCanvas.addEventListener('contextmenu', (e) => {
  e.preventDefault(); // Prevent the default context menu from appearing

  // Get the position of the mouse relative to the imageCanvas
  const rect = imageCanvas.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;

  // Find the index of the box at the clicked position
  const boxIndex = findBox(mouseX, mouseY);

  // If a box exists at the clicked position
  if (boxIndex !== -1) {
    // Remove the box from the boxes array
    boxes.splice(boxIndex, 1);
    draw();
  }
});

// Function to handle keydown events
document.addEventListener('keydown', (e) => {
  // Check if the pressed key is 'Delete'
  if (e.key === 'Delete') {
    // Check if a box is currently selected
    if (selectedBox !== null) {
      // Find the index of the selected box in the boxes array
      const index = boxes.indexOf(selectedBox);
      // If the selected box is found in the array
      if (index !== -1) {
        // Remove the selected box from the boxes array
        boxes.splice(index, 1);
        selectedBox = null; // Clear the selectedBox reference
        draw();
      }
    }
  }
});

// Event listener for input element to load JSON file
loadInput.addEventListener('change', function (e) {
  loadBoxes(e); // When the file input changes, trigger the loadBoxes function
});

// Event listener for saving boxes when a button is clicked
saveButton.addEventListener('click', function () {
  saveBoxes(boxes); // When the button is clicked, trigger the saveBoxes function
});

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

// Event listener for the text input field to update box text on pressing Enter
textInput.addEventListener('keypress', function (e) {
  // Check if the 'Enter' key is pressed
  if (e.key === 'Enter') {
    // Check if a box is selected and the input text is not empty
    if (selectedBox !== null && textInput.value.trim() !== '') {
      selectedBox.text = textInput.value.trim(); // Update the selected box text
      textInput.style.display = 'none'; // Hide text input after saving text
      draw();
    }
  }
});

createButton.addEventListener('click', async () => {
  const jsonData = document.getElementById('templateDisplay').textContent;
  const tableToCreate = JSON.parse(jsonData)
    .filter(item => item.class === "title")
    .map(item => item.text);

  const response = await fetch(`/confirm_and_create_table?table_name=${tableToCreate}`, {
    method: 'POST'
  });

  const data = await response.json();

  if (data.tableExists) {
    const confirmation = confirm(`Table "${tableToCreate}" already exists. Do you want to proceed with creating the table?`);
    if (confirmation) {
      createTable(jsonData);
    } else {
      console.log('Table creation cancelled.');
    }
  } else {
    createTable(jsonData);
  }
});

