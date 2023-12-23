// const mongoose = require('mongoose')
const path = require('path');

module.exports.indexPage = (req,res) => {
//    res.send('Wellcome to the product lookup site!')
//	response.sendFile(path.resolve(__dirname, 'pages/index.html'))
	const {MongoClient} = require('mongodb');
	let uri = 'mongodb://0.0.0.0:27017/prediction_database'
	MongoClient.connect(uri)
			.then(async function (client) {
				let results = await client.db('prediction_database')
					 .collection('img_classification')
					 .find({},{ projection: { _id:1 } },{ "returnKey":true })
					 .toArray()
				client.close()
				res.render('index', {results})	
			})
			.catch((err) => console.log(err) );
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
	function sleep(ms) {
	  return new Promise((resolve) => {
		setTimeout(resolve, ms);
	  });
	}
	let response = req.query;
	//check for 'img' param
	if(typeof (response["img"]) != "undefined") {
		let stats;
		//check if image exists on server
		try {
			let imageName=encodeURIComponent(req.query["img"]);
			let filePath = path.resolve(__dirname, 'public/upload', imageName);
			stats =require('fs').statSync(filePath);
			//if the code after this still being run, the file exists
			
			const {MongoClient} = require('mongodb');
			let uri = 'mongodb://0.0.0.0:27017/prediction_database'
			MongoClient.connect(uri)
					.then(async function (client) {
						let component = {"msg":null, "predict":null};
						console.log("connected to database");
						
						//multi attempt database lookup thingy
						const MAX_RETRY=5; //just ur local constant
						const TIME_INTERVAL=500
						let attempt = 0;
						let result = null;
						do {
							/*expected timeout values are:
							  attempt timeout
							        0      0s
							        1    2.0s
							        2    1.5s
							        3    1.0s
							        4    0.5s
							  (could be wrong if some1 change the consts)
							*/
							let timeOut = ((MAX_RETRY- attempt) % MAX_RETRY) * TIME_INTERVAL;
//							console.log(timeOut)
							await sleep(timeOut);
							result = await client.db('prediction_database')
								 .collection('img_classification')
								 .findOne( { '_id':imageName } );
							if(result !== null){
								break;
								}
							console.log(`${imageName}: attmpt #${attempt}, no match, retrying...`)
						} while( (attempt++) < MAX_RETRY);
						if(result === null){
								component["msg"] = "Result is not in database (try refeshing the page or reupload the image!)"
								response["img"] = `../upload/${imageName}`;
							} else {
								let arr = (result['reportPath']).split('/');
								let reportName = arr[arr.length-1];
//								component["predict"] = result["prediction"];
								response["img"] = reportName;
								component["msg"] = result["msg"];
							}
						client.close()
						response = Object.assign(component, response)
//						console.log(response);
						res.render('imagePredict',{response});
					}).catch((err) => console.log(err) )
					//.finally(() => this.close());
			return;
			
		} catch(e) {
			//console.warn("Cannot access files");
			console.warn(e.message);
			response["img"] = "../assets/img/deathbee.jpg"
			response = Object.assign(response,{ "msg": "Cannot access files","predict":null })
			}
	}
//	response["img"] = "../assets/img/deathbee.jpg"
	res.render('imagePredict',{response});
}

module.exports.imageUpload = (req, res) => {
//res.sendFile(path.resolve(__dirname,'pages/about.html'))
	try{
		let image = req.files.image;
		mimetype = String(image.mimetype).split('/');
		
		//check if file isn't actually an image, redirect without save the file
		if(mimetype[0] !== 'image') {
			console.warn("File is not of an Image type");
			throw new Error('File is not of an Image type')
			} 
			else {
				let imageName = `${image.md5}.${mimetype[1]}`;
				image.mv(require('path')
					.resolve(__dirname, 'public/upload', imageName), 
					function (error) {
						let filePath=path.resolve(__dirname, 'public/upload', imageName)
						console.log(`Image is saved @${filePath}`);
						res.redirect(`/predict/photo?img=${imageName}`);
						}) 
			}
	} catch (e){
		errMess = encodeURIComponent(e);
//		errImg = encodeURIComponent("../assets/img/deathbee.jpg");
		res.redirect(`/predict/photo?msg=${errMess}`);
	
	}
}

exports.error = function(req, res) {
    res.status(404).send('404 Not Found!');
}

