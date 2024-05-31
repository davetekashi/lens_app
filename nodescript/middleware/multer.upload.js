require('dotenv').config()
const multer = require('multer');

// Set up Multer for handling file uploads
const storage = multer.memoryStorage();

/**
 * @description - This function will extact and filter the form data fore the image file
 * @param {Object}
 * @returns {Promise<any>}
 */
const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
    // Check if the file type is supported
    fileFilter: (req, file, cb) => {
        if (['image/jpeg', 'image/png', 'image/jpg'].includes(file.mimetype)) {
            return cb(null, true);
        }
        cb(new Error('Invalid file type. Supported types: JPEG, PNG, JPG.'));
    }
});


exports.bundleImageBuffer = (req, res, next) => {
    upload.single('image')
        (req, res, function (err) {
            if (err) {
                return res.status(400).json({ error: 'File upload failed. ' + err });
            }
            // File upload successful, continue to the next middleware
            next();
        });
}

exports.bundleMultiImageBuffer = (req, res, next) => {
    upload.array('images', 5)
        (req, res, function (err) {
            if (err) {
                return res.status(400).json({ error: 'File upload failed. ' + err.message });
            }
            // File upload successful, continue to the next middleware
            next();
        });
}
