const tesseract = require("node-tesseract-ocr")
const vision = require('@google-cloud/vision');

// Set up Google Cloud Vision client
const client = new vision.ImageAnnotatorClient({
    keyFilename: 'service-key.json'
});


/**
 * @description - This funtion calls the google vision api and extract the text from the image 
 * @param {Buffer} buffer 
 * @returns {String}
 */
exports.extractWithGoogleVision = async (buffer) => {
    const [result] = await client.textDetection({ image: { content: buffer } });
    const detections = result.textAnnotations;
    return detections.length > 0 ? detections[0].description : '';
}

/**
 * @description - This funtion extract the text from the image using tesseract-ocr
 * @param {Buffer} buffer - The image buffer to extract the text from
 * @returns {String}
 */
exports.extractWithTesseract = async (buffer) => {
    const config = {
        lang: "eng",
        oem: 1,
        psm: 3,
    }

    const extractedText = await tesseract.recognize(buffer, config)
    console.log('RAW DATA ---> ', extractedText)
    return extractedText
}