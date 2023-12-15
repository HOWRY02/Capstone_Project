const imageInput = document.getElementById('imageInput');
const imageCanvas = document.getElementById('imageCanvas');
const ctx = imageCanvas.getContext('2d');
const formImage = document.getElementById("formImage");
const imgSrc = formImage.src;
const boxesString = document.getElementById("hiddenJsonData").textContent.replace(/'/g, '"');
const boxesTemp = JSON.parse(boxesString);
const removeThreshold = 5;

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

// Function to set the current mode
function setMode(mode, color) {
  currentMode = mode;
  currentColor = color
  draw();
}

// Function to remove boxes with absolute height or width < 0.5
function removeSmallBoxes() {
  boxes = boxes.filter(box => Math.abs(box.width) >= removeThreshold && Math.abs(box.height) >= removeThreshold);
  draw();
}

function delareImage() {
  if (isSubmiting) {
    img.src = imgSrc;
  } else {
    img.src = realImgSrc;
  }

  // Setting the canvas dimensions to match the loaded image
  imageCanvas.width = img.width;
  imageCanvas.height = img.height;

  adjustInputElementsSize(); // Call function to adjust input elements size
}

function draw() {
  delareImage();
  ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
  ctx.drawImage(img, 0, 0, img.width, img.height);

  boxes.forEach((box, index) => {
    switch (box.class) {
      case 'title':
        ctx.strokeStyle = colorTitle;
        ctx.strokeStyle = colorTitle; // Set red color for 'title' class
        currentColor = colorTitle;
        break;
      case 'question':
        ctx.strokeStyle = colorQuestion; // Set violet color for 'question' class
        ctx.strokeStyle = colorQuestion;
        currentColor = colorQuestion;
        break;
      case 'date':
        ctx.strokeStyle = colorDate; // Set violet color for 'question' class
        ctx.strokeStyle = colorDate;
        currentColor = colorDate;
        break;
      default:
        ctx.strokeStyle = currentColor; // Set default color if no specific class matches
        break;
    }

    ctx.strokeStyle = selectedBox === box ? 'blue' : currentColor;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(box.startX, box.startY, box.width, box.height);

    // **Comment out the following code to remove the circle**
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(box.startX + box.width, box.startY + box.height, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    if (selectedBox === box) {
      // Display text input for the selected box
      const text = box.text || '';
      const inputText = document.getElementById('textInput');
      inputText.value = text;
      inputText.style.display = 'block';
      inputText.style.top = `${box.startY + box.height + 5}px`; // Adjust text input position
      inputText.style.left = `${box.startX}px`; // Adjust text input position
    }
  });

  if (resizingBox !== null) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fillRect(resizingBox.startX, resizingBox.startY, resizingBox.width, resizingBox.height);
  }
}

// Function to adjust the size of input elements based on imageCanvas size
function adjustInputElementsSize() {
  const canvasRect = imageCanvas.getBoundingClientRect();
  const canvasWidth = canvasRect.width;
  const canvasHeight = canvasRect.height;

  // Calculate the scaled size for input elements
  const scaleFactor = Math.min(canvasWidth, canvasHeight) / 400; // Adjust according to your requirements

  const inputText = document.getElementById('textInput');
  inputText.style.fontSize = `${scaleFactor * 16}px`; // Adjust font size based on canvas size

  const buttons = document.querySelectorAll('input[type="file"], #saveButton');
  buttons.forEach(button => {
    button.style.fontSize = `${scaleFactor * 14}px`; // Adjust button font size
    button.style.padding = `${scaleFactor * 8}px ${scaleFactor * 16}px`; // Adjust button padding
  });

  // Adjust padding for question and title buttonz
  const button_class = document.querySelectorAll('#submitButton, #questionButton, #titleButton, #dateButton');
  button_class.forEach(button => {
    button.style.fontSize = `${scaleFactor * 12}px`; // Adjust button font size
    button.style.padding = `${scaleFactor * 6}px ${scaleFactor * 13}px`; // Adjust button padding
  });
}

// Call the function to delete all boxes
function deleteAllBoxes() {
  // Check if there are boxes in the array
  if (boxes.length > 0) {
    // Remove all boxes from the array
    boxes.splice(0, boxes.length);
    selectedBox = null; // Clear the selectedBox reference
    draw(); // Redraw the canvas after removing all the boxes
  }
}

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


function findHandle(x, y) {
  // Iterate through all the boxes in the 'boxes' array
  for (let i = 0; i < boxes.length; i++) {
    const box = boxes[i]; // Get the current box

    let topLeftX, topLeftY, bottomRightX, bottomRightY;

    // Determine coordinates of the top-left and bottom-right corners of the box
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

    // Calculate the center of the box
    const centerX = bottomRightX;
    const centerY = bottomRightY;

    // Calculate the distance between the mouse pointer and the center of the box
    const distX = x - centerX;
    const distY = y - centerY;
    const distance = Math.sqrt(distX * distX + distY * distY);

    // If the distance is within a threshold (6 in this case), consider it a resize handle
    if (distance <= 6) {
      return { type: 'resize', boxIndex: i }; // Return resize handle type and box index
    }

    // Check if the mouse pointer is inside the bounding box of the current box
    if (
      x >= Math.min(topLeftX, bottomRightX) &&
      x <= Math.max(topLeftX, bottomRightX) &&
      y >= Math.min(topLeftY, bottomRightY) &&
      y <= Math.max(topLeftY, bottomRightY)
    ) {
      return { type: 'drag', boxIndex: i }; // Return drag type and box index
    }
  }

  // If no box or handle is found under the mouse pointer, return type 'none' and box index -1
  return { type: 'none', boxIndex: -1 };
}


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
      const box = { startX: mouseX, startY: mouseY, width: 0, height: 0, class: currentMode };
      boxes.push(box); // Adding the new box to the boxes array
      selectedBox = box; // Setting the newly created box as selected
    }
  }

  // Redraw the canvas to reflect any changes in the boxes
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
      selectedBox.startX = mouseX;
      selectedBox.startY = mouseY;
      selectedBox.width -= dx;
      selectedBox.height -= dy;
    } else if (isResizing && resizingBox !== null) {
      // If resizing a box
      // Calculating and updating the resized box dimensions based on mouse movement
      resizingBox.width = Math.max(0, mouseX - resizingBox.startX);
      resizingBox.height = Math.max(0, mouseY - resizingBox.startY);
    }

    // clearSmallBoxes()
    // Redraw the canvas to reflect box movement or resizing
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
    const inputText = document.getElementById('textInput');
    if (selectedBox !== null && inputText.value.trim() !== '') {
      selectedBox.text = inputText.value.trim();
      inputText.style.display = 'none'; // Hide text input after saving text
    }

    draw(); // Redraw the canvas after handling the mouseup event
  }

  removeSmallBoxes() // Remove small boxes after the mouse is released
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
        draw(); // Redraw the canvas after removing the box
      }
    }
  }
});

// Function to find a box based on the coordinates (x, y)
function findBox(x, y) {
  // Loop through the boxes array
  for (let i = 0; i < boxes.length; i++) {
    const box = boxes[i];
    // Check if the coordinates (x, y) fall within the boundaries of the current box
    if (
      x >= box.startX &&
      x <= box.startX + box.width &&
      y >= box.startY &&
      y <= box.startY + box.height
    ) {
      return i; // Return the index of the box if found
    }
  }
  return -1; // Return -1 if no box is found at the given coordinates
}

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
    draw(); // Redraw the canvas after removing the box
  }
});

// Function to save boxes to a JSON file
function saveBoxes() {
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

      draw(); // Redraw the canvas with the loaded boxes
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
      draw(); // Redraw the canvas to display the updated text
    }
  }
});



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

