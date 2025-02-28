# Capstone Project

## Overview
Welcome to the Capstone Project repository! This project represents the culmination of our work in the Data Science program at HCMC University of Technology and Education. The goal of this project is to develop an Optical Character Recognition (OCR) system that can accurately detect and recognize text from various document images.

This application processes scanned documents, extracts text, and provides a user-friendly interface for reviewing and editing the recognized text.

## Features
- **User Authentication**: Secure login and registration for users.
- **Real-time Data Processing**: Efficiently processes scanned documents and extracts text in real-time.
- **Interactive UI**: Provides an intuitive and responsive user interface for reviewing and editing recognized text.
- **Document Management**: Allows users to upload, manage, and organize their documents.
- **Text Recognition**: Utilizes advanced OCR techniques to accurately detect and recognize text from images.
- **Data Visualization**: Visualizes the extracted text data for easy analysis and review.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python FastAPI
- **Database**: MySQL
- **Other Tools**: Git, Docker

## Installation
To run this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HOWRY02/Capstone_Project.git
   cd Capstone_Project
   ```

2. **Install dependencies**:
    ```bash
    npm install  # For Node.js projects
    pip install -r requirements.txt  # For Python projects
    ```

3. **Set up environment variables**:
 - Create a .env file in the root directory.
 - Add the following variables:

    ```text
    DATABASE_URL=your_database_url
    API_KEY=your_api_key
    ```

4. **Run the application**:
    ```bash
    npm start  # For Node.js
    python app.py  # For Python
    ```
## Usage

 - Open your browser and navigate to http://localhost:3000.
 - Sign up or log in to access the dashboard.
 - Upload your documents and start the OCR process.
 - Review and edit the recognized text as needed.

## Project Structure

    Capstone_Project/
    ├── src/              # Source code
    ├── docs/             # Documentation files
    ├── tests/            # Test scripts
    ├── .env.example      # Example environment file
    ├── README.md         # This file
    └── [other files]     # e.g., package.json, requirements.txt

## License
This project is licensed under the [License Name, e.g., MIT License] - see the LICENSE file for details.

## Acknowledgments
 - Thanks to our professor, Duc Bui Ha, PhD, for guidance.
 - Inspired by various OCR tools and libraries.

## Contact
For any questions or feedback, please contact Phuc Huynh Vinh at phuchuynhvinh.fwork@gmail.com.
