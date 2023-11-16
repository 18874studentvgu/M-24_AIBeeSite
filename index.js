const express = require('express')
const app = express()
const router = require('./router')

const ejs = require('ejs')
app.set('view engine','ejs')

const fileUpload = require('express-fileupload')
app.use(fileUpload({debug: false}))

//const mongoose = require('mongoose')

//mongoose.connect('mongodb://0.0.0.0:27017/products', { useNewUrlParser: true })
//    .then(async function (params) {
//        console.log("connected to product database")

//        //checking if the db is empty, add a dummy product if so
//        let ProductInformation = require('./models/ProductInformationModel')
//        console.log(await ProductInformation.exists({}))
//        if ((await ProductInformation.exists({})) === null) {
//            console.log("Note: empty product database, adding a test entry")
//            let id = new Buffer.from('9059089199879','utf-8')
//            console.log(id.toString('hex'))
//            ProductInformation.create({
//                product_name: "The Mistery Fruit from Higher Dimentions",
//                _id: '9059089199879'
//            })
//        }
//    })

const PORT = 5000

app.use(express.static('public'))

app.use('/', router)

app.listen(PORT, () => console.log(`Listening on ${PORT}`))

