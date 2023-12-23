const express = require('express')
const router = express.Router()
const controller = require('./controller')

router.get(['/', '/index'],controller.indexPage)

router.get(['/post', '/post.html'],controller.postPage)

router.get(['/about', '/about.html'],controller.aboutPage)

router.get(['/contact', '/contact.html'],controller.contactPage)

router.get('/predict/photo',controller.imagePredictPage)

router.post('/image/store',controller.imageUpload)


//router.get('/productInformation/:productID',controller.productInformation_GET)

router.get('*', controller.error);

module.exports = router
