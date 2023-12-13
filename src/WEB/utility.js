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