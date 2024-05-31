const mongoose = require('mongoose');

const ImageSchema = new mongoose.Schema({
    // accountNumber: { type: Number, required: true },
    // accountName: { type: String, required: true },
    // bankName: { type: String, required: true },
    // bankCode: { type: String, required: true },
    // phoneNo: { type: String, required: true },
    // email: { type: String, required: true },
    images: { type: Array, required: true }
})

const ImageModel = mongoose.model('User', ImageSchema)

module.exports = ImageModel