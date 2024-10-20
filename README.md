# optiread FastAPI Application

This FastAPI application performs Optical Character Recognition (OCR) on uploaded images to extract useful information such as company name, manufacturing date, and expiry date. The application uses EasyOCR for text extraction and OpenCV for image processing.

## Features

-   Upload an image and receive extracted information in JSON format.
-   Draws bounding boxes around recognized text in the image.
-   Returns the processed image as a base64-encoded string.

## Technologies Used

-   FastAPI
-   EasyOCR
-   OpenCV
-   Pillow
-   NumPy

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    cd ocrex
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Start the FastAPI server using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

The application will be accessible at [http://localhost:8000](http://localhost:8000).

## API Endpoints

### Upload Image for OCR

-   **Endpoint**: `/extract/`
-   **Method**: `POST`
-   **Request**:
    -   **Content-Type**: `multipart/form-data`
    -   **Body**:
        -   `file`: The image file to be processed (JPEG, PNG, etc.).

#### Example Request (using cURL)

    ```bash
    curl -X POST "http://localhost:8000/extract/" -F "file=@path_to_your_image.jpg"
    ```

#### Example Response

```json
{
    "company_name": "Example Company",
    "manufacturing_date": "01 JAN 2022",
    "expiry_date": "01 JAN 2023",
    "ocr_output_image": "base64_encoded_image_string",
    "recognized_text": [
        "Example Company",
        "Mfg Date: 01 JAN 2022",
        "Exp Date: 01 JAN 2023"
    ]
}
```

### Response Fields

-   **company_name**: The name of the company as extracted from the image.
-   **manufacturing_date**: The manufacturing date recognized from the image.
-   **expiry_date**: The expiry date recognized from the image.
-   **ocr_output_image**: The processed image with bounding boxes drawn around recognized text, encoded as a base64 string.
-   **recognized_text**: An array of recognized text strings from the image for debugging purposes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
