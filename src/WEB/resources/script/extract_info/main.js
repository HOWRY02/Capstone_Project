const imageInput = document.getElementById('imageInput');
const imageCanvas = document.getElementById('imageCanvas');
const ctx = imageCanvas.getContext('2d');
const formImage = document.getElementById("formImage");
const imgSrc = formImage.src;
const boxesString = document.getElementById("hiddenJsonData").textContent.replace(/'/g, '"');
const boxesTemp = JSON.parse(boxesString);
const removeThreshold = 5;

const submitButton = document.getElementById('submitButton');
const textInput = document.getElementById('textInput');
const updateButton = document.getElementById('updateButton');
const container = document.getElementById('displayContainer');


let img = new Image();
let realImgSrc;
let isSubmiting = true;
let isDragging = false; // Flag to track dragging action
let mouseX, mouseY;
let selectedBox = null;
let boxes = []; // Array to store box coordinates
let answer_boxes = []; // Array to store box coordinates
let resizingBox = null; // Variable to track the box being resized
let isResizing = false; // Flag to track resize status

// Variables to store the current mode
let currentMode = 'answer'; // Default mode is 'title'
let colorTitle = 'red';
let colorQuestion = 'green';
let colorAnswer = 'purple';
let colorDate = 'blue';
let currentColor = colorTitle;
const WIDTH = 1000;
const scaleFactor = 1.5;

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

boxes = boxesTemp.map(data => {
    let loc = [{
        startX: data.box[2],
        startY: data.box[3],
        width: data.box[0] - data.box[2],
        height: data.box[1] - data.box[3],
        text: data.text || '', // Ensure text property exists or set it to an empty string
        class: data.class
    }]

    loc = loc.concat(data.answer_text.map(answer_data => ({
        startX: answer_data.box[2],
        startY: answer_data.box[3],
        width: answer_data.box[0] - answer_data.box[2],
        height: answer_data.box[1] - answer_data.box[3],
        text: answer_data.text || '',
        class: answer_data.class
    })))

    return loc;
});

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
        // Reading the selected file as a data URL
        reader.readAsDataURL(file);
        // Event triggered when FileReader finishes reading the file
        reader.onload = function (e) {
            // append new image to the "image-container"
            let image = document.createElement("img");
            image_url = e.target.result;
            image.src = image_url;
           

            // Event triggered when the image has finished loading
            image.onload = function (e) {
                // Resize image
                imageCanvas.width = WIDTH;
                 // let aspect ratio of the image
                let ratio = WIDTH / e.target.width;
                imageCanvas.height = e.target.height * ratio;

                // Draw image on the canvas
                ctx.drawImage(image, 0, 0, imageCanvas.width, imageCanvas.height);
                
                // display the resized image on the canvas
                let new_image_url = ctx.canvas.toDataURL("image/jpeg", 100);
                let new_image = document.createElement("img");
                new_image.src = new_image_url;
                realImgSrc = new_image_url;
                imgSrc = new_image_url;
                // document.getElementsByClassName("image-container").appendChild(new_image);
                adjustInputElementsSize();

            };
        };

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
        resizingBox = boxes[boxIndex[0]][boxIndex[1]]; // Getting the box to be resized
        selectedBox = resizingBox; // Selecting the box when clicking on the resize handle
    } else if (type === 'drag') {
        // If a drag action is detected
        isDragging = true;
        isResizing = false;
        selectedBox = boxes[boxIndex[0]][boxIndex[1]]; // Selecting the box to be dragged
    } else {
        // If neither resize nor drag action is detected
        if (selectedBox === boxes[boxIndex[0]]) {
            // If the clicked box is already selected, deselect it
            selectedBox = null;
        } else {
            // If a new box creation action is detected
            isResizing = true;
            // Creating a new box at the clicked position with initial dimensions
            const box = {
                startX: Math.round(mouseX), startY: Math.round(mouseY),
                width: 0, height: 0, class: currentMode
            };
            boxes.push([box]); // Adding the new box to the boxes array
            resizingBox = box;
            selectedBox = resizingBox; // Setting the newly created box as selected
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

    // Handling box movement or resizing based on the action type
    if (selectedBox !== null) {
        if (isDragging && selectedBox !== null) {
            // Updating box position and dimensions based on mouse movement
            selectedBox.startX = Math.round(mouseX - selectedBox.width);
            selectedBox.startY = Math.round(mouseY - selectedBox.height);
        } else if (isResizing && resizingBox !== null) {
            const dx = mouseX - resizingBox.startX;
            const dy = mouseY - resizingBox.startY;
            // Updating box position and dimensions based on mouse movement
            resizingBox.startX = Math.round(mouseX);
            resizingBox.startY = Math.round(mouseY);
            resizingBox.width -= Math.round(dx);
            resizingBox.height -= Math.round(dy);
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
});

// Function to handle keydown events
document.addEventListener('keydown', (e) => {
    // Check if the pressed key is 'Delete'
    if (e.key === 'Delete') {
        // Check if a box is currently selected
        if (selectedBox !== null) {
            for (let i = 0; i < boxes.length; i++) {
                // Find the index of the selected box in the boxes array
                const index = boxes[i].indexOf(selectedBox);
                // If the selected box is found in the array
                if (index !== -1) {
                    // Remove the selected box from the boxes array
                    boxes[i].splice(index, 1);
                    selectedBox = null; // Clear the selectedBox reference
                }

                if (boxes[i].length === 0) {
                    boxes.splice(i, 1);
                }
            }
            draw();
        }
    }
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

updateButton.addEventListener('click', async () => {
    const jsonData = document.getElementById('templateDisplay').textContent;
    const tableToUpdate = JSON.parse(jsonData)
        .filter(item => item.class === "title")
        .map(item => item.text);

    const response = await fetch(`/confirm_and_create_table?table_name=${tableToUpdate}`, {
        method: 'POST'
    });

    const data = await response.json();

    if (data.tableExists) {
        updateTable(jsonData);
    } else {
        alert(`Table "${tableToUpdate}" does not exist.`)
    }
});

// JavaScript to handle button click and navigate to index.html
document.getElementById('homeButton').addEventListener('click', function () {
    window.location.href = '/'; // This navigates to index.html
});

// JavaScript to handle button click and navigate to create_table.html
document.getElementById('createButton').addEventListener('click', function () {
    window.location.href = '/creatingTable'; // This navigates to create_table.html
});
