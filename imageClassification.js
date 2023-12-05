const tf = require('@tensorflow/tfjs-node');
const modelPath = require('path').resolve(__dirname,'SavedModel');


module.exports = (file) => {
//res.sendFile(path.resolve(__dirname,'pages/contact.html'))
	let path = require('path').join(__dirname, 'public/upload',file);
			console.log(path)
	require('fs').readFile(path, async function (err,data) {
			console.log(err)
			console.log("1")
		if(!err){
			console.log("2")
			let model = await tf.node.loadSavedModel(modelPath);
			console.log("3")
			let imageTensor = tf.node.decodeImage(data);
			console.log(modelMath.predict(imageTensor))
			console.log(modelMath)
			return modelMath.predict(imageTensor);
		} else {
			return {"msg":"Error: no can read files"}
		}
	})
}
