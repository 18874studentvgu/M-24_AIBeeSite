// const mongoose = require('mongoose')
//let ProductInformation = require('./models/ProductInformationModel')

module.exports.indexPage = (req,res) => {
//    res.send('Wellcome to the product lookup site!')
//	response.sendFile(path.resolve(__dirname, 'pages/index.html'))
	res.render('index')	
}

module.exports.postPage = (req,res) => {
	res.render('post')
}

module.exports.aboutPage = (req, res) => {
//res.sendFile(path.resolve(__dirname,'pages/about.html'))
	res.render('about');
}

module.exports.contactPage = (req, res) => {
//res.sendFile(path.resolve(__dirname,'pages/contact.html'))
	res.render('contact');
}

module.exports.imagePredictPage = (req, res) => {
//res.sendFile(path.resolve(__dirname,'pages/about.html'))
	//check for 'img' param
	let response = req.query;
	if(typeof (req.query["img"]) != "undefined") {
		let stats;
		//check if image exists on server
		try {
			let imageName=encodeURIComponent(req.query["img"]);
			let path = require('path').resolve(__dirname, 'public/upload', imageName);
			stats =require('fs').statSync(path);
			//if the code after this still being run, the file exists
			
			//AI stuffs goes here
			///
			let prediction = {"msg": "place holder Perdiction"}
			response = Object.assign(response, prediction)
			
		} catch(e) {
			console.warn("Cannot access files");
			response["img"] = "../assets/img/deathbee.jpg"
			response = Object.assign(response,{"msg": "Cannot access files"})
			}
	}
	res.render('imagePredict',{response});
}

module.exports.imageUpload = (req, res) => {
//res.sendFile(path.resolve(__dirname,'pages/about.html'))
	let image = req.files.image;
	mimetype = String(image.mimetype).split('/');
	
	//check if file isn't actually an image, redirect without save the file
	if(mimetype[0] !== 'image') {
		console.warn("File is not of an Image type");
		res.redirect('/predict/photo');
		} 
		else {
			let imageName = `${image.md5}.${mimetype[1]}`;
			image.mv(require('path')
				.resolve(__dirname, 'public/upload', imageName), 
				function (error) {
					let path=require('path').resolve(__dirname, 'public/upload', imageName)
					console.log(`Image is saved @${path}`);
					res.redirect(`/predict/photo?img=${imageName}`);
					}) 
		}
//	res.redirect('/predict/photo');
}

//module.exports.productInformation_GET = (req,res) => {
//    ProductInformation.findById((req.params.productID).trim()).exec()
//    .then(function(doc){
//        if(doc){
//            console.log(doc)            
//            res.send(doc)
//        } else {
//            res.send('We can\'t seem to find such product')

//        }
//        })
//    .catch(function(error){
//        console.log(error)

//        res.send('Something went wrong! Contact the admin!')
//    })
//}
