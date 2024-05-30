const express = require('express');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/register', upload.array('images', 5), async (req, res) => {
    const { accountName, accountNumber, bankName, bankCode, phoneNo, email } = req.body;

    // Prepare form data
    const formData = new FormData();
    formData.append('accountName', accountName);
    formData.append('accountNumber', accountNumber);
    formData.append('bankName', bankName);
    formData.append('bankCode', bankCode);
    formData.append('phoneNo', phoneNo);
    formData.append('email', email);

    req.files.forEach(file => {
        formData.append('files', fs.createReadStream(file.path), file.originalname);
    });

    try {
        const response = await axios.post('http://localhost:8000/process_user', formData, {
            headers: formData.getHeaders()
        });

        // Clean up uploaded files
        req.files.forEach(file => {
            fs.unlinkSync(file.path);
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error processing user:', error);
        res.status(500).json({ message: 'Error processing user' });
    }
});

app.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
