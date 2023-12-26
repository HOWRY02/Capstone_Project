// Function to adjust the size of input elements based on imageCanvas size
function adjustInputElementsSize() {
  const canvasRect = imageCanvas.getBoundingClientRect();
  const canvasWidth = canvasRect.width;
  const canvasHeight = canvasRect.height;

  // Calculate the scaled size for input elements
  const scaleFactor = Math.min(canvasWidth, canvasHeight) / 400; // Adjust according to your requirements

  const inputText = document.getElementById('textInput');
  inputText.style.fontSize = `${scaleFactor * 16}px`; // Adjust font size based on canvas size

  const templateDisplay = document.getElementById('templateDisplay');
  templateDisplay.style.fontSize = `${scaleFactor * 10}px`; // Adjust font size based on canvas size

  const buttons = document.querySelectorAll('input[type="file"], #saveButton, #createButton');
  buttons.forEach(button => {
    button.style.fontSize = `${scaleFactor * 14}px`; // Adjust button font size
    button.style.padding = `${scaleFactor * 8}px ${scaleFactor * 16}px`; // Adjust button padding
  });

  // Adjust padding for question and title buttonz
  const button_class = document.querySelectorAll('#submitButton, #questionButton, #answerButton, #titleButton, #dateButton');
  button_class.forEach(button => {
    button.style.fontSize = `${scaleFactor * 12}px`; // Adjust button font size
    button.style.padding = `${scaleFactor * 6}px ${scaleFactor * 13}px`; // Adjust button padding
  });
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

  adjustInputElementsSize(imageCanvas); // Call function to adjust input elements size
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
        ctx.strokeStyle = colorQuestion; // Set green color for 'question' class
        ctx.strokeStyle = colorQuestion;
        currentColor = colorQuestion;
        break;
      case 'answer':
          ctx.strokeStyle = colorAnswer; // Set yellow color for 'answer' class
          ctx.strokeStyle = colorAnswer;
          currentColor = colorAnswer;
          break;
      case 'date':
        ctx.strokeStyle = colorDate; // Set violet color for 'date' class
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
  const boxesToSave = formatBoxesToSave(boxes);
  document.getElementById('templateDisplay').textContent = JSON.stringify(boxesToSave);
}

// Function to remove boxes with absolute height or width < 0.5
function removeSmallBoxes() {
  boxes = boxes.filter(box => Math.abs(box.width) >= removeThreshold && Math.abs(box.height) >= removeThreshold);
  draw();
}

// Call the function to delete all boxes
function deleteAllBoxes() {
  // Check if there are boxes in the array
  if (boxes.length > 0) {
    // Remove all boxes from the array
    boxes.splice(0, boxes.length);
    selectedBox = null; // Clear the selectedBox reference
    draw();
  }
}

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

// Function to set the current mode
function setMode(mode, color) {
  currentMode = mode;
  currentColor = color
  draw();
}

function formatBoxesToSave(boxes) {
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
  return boxesToSave;
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
        startX: Math.round(data.box[2]),
        startY: Math.round(data.box[3]),
        width: Math.round(data.box[0] - data.box[2]),
        height: Math.round(data.box[1] - data.box[3]),
        text: data.text || '', // Ensure text property exists or set it to an empty string
        class: data.class
      }));
      draw();
    };
    reader.readAsText(file); // Read the contents of the file as text
  }
}

// Function to save boxes to a JSON file
function saveBoxes(boxes) {

  const boxesToSave = formatBoxesToSave(boxes);

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

function createTable(jsonData) {
  fetch('/create_table_proceed', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ data: jsonData })
  })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => alert(error.message));
}
