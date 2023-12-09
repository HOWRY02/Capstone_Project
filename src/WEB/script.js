const imageInput = document.getElementById('imageInput');
const imageCanvas = document.getElementById('imageCanvas');
const ctx = imageCanvas.getContext('2d');
let img;
let isDragging = false; // Flag to track dragging action
let mouseX, mouseY;
let selectedBox = null;
let boxes = []; // Array to store box coordinates
let resizingBox = null; // Variable to track the box being resized
let isResizing = false; // Flag to track resize status

// let scale = 1;
// let img = null;
function draw() {
  ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
  ctx.drawImage(img, 0, 0, img.width, img.height);

  boxes.forEach((box, index) => {
    ctx.strokeStyle = selectedBox === box ? 'blue' : 'red';
    ctx.lineWidth = 0.6;
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
}
// Adding an event listener to 'imageInput' element when a file is selected
imageInput.addEventListener('change', function (event) {
  // Retrieving the selected file
  const file = event.target.files[0];

  // Checking if a file is selected
  if (file) {
    // Creating a new instance of FileReader
    const reader = new FileReader();

    // Event triggered when FileReader finishes reading the file
    reader.onload = function (e) {
      // Creating a new Image object
      img = new Image();

      // Event triggered when the image has finished loading
      img.onload = function () {
        // Setting the canvas dimensions to match the loaded image
        imageCanvas.width = img.width;
        imageCanvas.height = img.height;

        adjustInputElementsSize(); // Call function to adjust input elements size
        // Drawing the image on the canvas
        ctx.drawImage(img, 0, 0, img.width, img.height);
      };

      // Setting the source of the image to the result of FileReader
      img.src = e.target.result;
    };

    // Reading the selected file as a data URL
    reader.readAsDataURL(file);
  }
});

function findHandle(x, y) {
  for (let i = 0; i < boxes.length; i++) {
    const box = boxes[i];

    let topLeftX, topLeftY, bottomRightX, bottomRightY;

    if (box.width >= 0 && box.height >= 0) {
      topLeftX = box.startX;
      topLeftY = box.startY;
      bottomRightX = box.startX + box.width;
      bottomRightY = box.startY + box.height;
    } else {
      bottomRightX = box.startX;
      bottomRightY = box.startY;
      topLeftX = box.startX + box.width;
      topLeftY = box.startY + box.height;
    }

    const centerX = bottomRightX;
    const centerY = bottomRightY;

    const distX = x - centerX;
    const distY = y - centerY;
    const distance = Math.sqrt(distX * distX + distY * distY);

    if (distance <= 6) {
      return { type: 'resize', boxIndex: i };
    }

    if (
      x >= Math.min(topLeftX, bottomRightX) &&
      x <= Math.max(topLeftX, bottomRightX) &&
      y >= Math.min(topLeftY, bottomRightY) &&
      y <= Math.max(topLeftY, bottomRightY)
    ) {
      return { type: 'drag', boxIndex: i };
    }
  }
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
      const box = { startX: mouseX, startY: mouseY, width: 10, height: 10 };
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
  // Create an array containing boxes data (startX, startY, width, height, and text)
  const boxesToSave = boxes.map(box => ({
    startX: box.startX,
    startY: box.startY,
    width: box.width,
    height: box.height,
    text: box.text || '' // Ensure text property exists or set it to an empty string
  }));

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
        startX: data.startX,
        startY: data.startY,
        width: data.width,
        height: data.height,
        text: data.text || '' // Ensure text property exists or set it to an empty string
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
