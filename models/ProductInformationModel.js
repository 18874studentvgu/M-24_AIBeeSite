const mongoose = require('mongoose')

const ProductInformationSchema = new mongoose.Schema({
    _id: {
        require: true,
        default: new mongoose.Types.ObjectId(),
        type: String
    },
    product_name: {
        require: true,
        default: "Unset",
        type: String
    },
    product_manufacter: {
        require: true,
        default: "Unset",
        type: String
    },
    from: {
        require: true,
        default: "Unset",
        type: String
    },
    product_contains: [{
        require: true,
        default: "Unset",
        type: String
    }],
    energy_per_100g: {
        require: true,
        default: -1,
        type: Number
    },
    expiry_time: {
        require: true,
        default: "0.25 day since manufactured date",
        type: String
    },

})

module.exports = mongoose.model("ProductInformation",ProductInformationSchema)