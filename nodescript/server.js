const { bundleImageBuffer, bundleMultiImageBuffer } = require("./middleware/multer.upload");
const { extractAccountDetails } = require("./controller/filter/accountDetails");
const { extractWithGoogleVision } = require("./controller/ocr/extractTexts");
const { Readable } = require('stream');
const mongoose = require('mongoose');
const express = require("express");
require('dotenv').config();

const database_url = process.env.DB_URL;
const port = process.env.PORT || 3000;

const app = express();
app.use(express.json({ limit: "16kb" }));
app.use(express.urlencoded({ extended: true, limit: "16kb" }));
app.use(express.static("public")); // configure static file to save images locally

let gfs;

app.post('/api/v1/register-user-lense-images', bundleMultiImageBuffer, async (req, res) => {
    try {
        const files = req.files;
        const { accountName, accountNumber, bankName, bankCode, phoneNo, email } = req.body;

        if (!files || files.length === 0) {
            return res.status(400).json({ error: 'No files uploaded' });
        }

        // Loop through uploaded files and upload them to GridFS
        for (const file of req.files) {
            const metadata = { userId: 'uniqueId 1', accountName, accountNumber, bankName, bankCode, phoneNo, email }
            const uploadStream = gfs.openUploadStream(`${Date.now()}-${file.originalname}`,
                { metadata: metadata }
            )
            const fileStream = Readable.from(file.buffer);
            fileStream.pipe(uploadStream);

            await new Promise((resolve, reject) => {
                uploadStream.on('finish', resolve);
                uploadStream.on('error', reject);
            });
        }

        res.status(200).json({ message: 'Files uploaded successfully' });
    } catch (error) {
        console.error('Error processing user:', error);
        res.status(500).json({ message: 'Error processing user' });
    }
});

app.post('/api/v1/extract-account-details', bundleImageBuffer, async (req, res) => {
    try {
        const file = req.file;
        if (!file) {
            return res.status(400).send('No file uploaded.');
        }
        const extractedText = await extractWithGoogleVision(file.buffer);
        const result = await extractAccountDetails(extractedText);
        if (result.length > 1) {
            return res.status(200).json(result);
        }

        res.status(404).json({ message: 'Account details not found' });
    } catch (e) {
        console.log(e);
        res.status(500).json({ message: e.message || 'Internal Server Error' });
    }
});

app.listen(port, async () => {
    try {
        const conn = mongoose.createConnection(database_url, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
        conn.once('open', () => {
            // gfs = Grid(conn.db, mongoose.mongo);
            // gfs.collection('uploads');
            // console.log('GridFS initialized');
            gfs = new mongoose.mongo.GridFSBucket(conn.db, {
                bucketName: 'uploads'
            })
            console.log('GridFS initialized');
        });

        await mongoose.set('strictQuery', true);
        console.log(`Server listening on port ${port} and database connected`);
    } catch (error) {
        console.error('Failed to connect to the database:', error);
    }
});
