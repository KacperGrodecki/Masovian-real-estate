// User's input
// https://www.handsonembedded.com/hands-on-aiot-simple-linear-regression/simple-linear-regression-in-tensorflow-js-with-bootstrap/


const inputMax = tf.tensor(230);
const inputMin = tf.tensor(46);
const labelMax = tf.tensor(46.599998474121094);
const labelMin = tf.tensor(9);            

async function loadModel() {
        // https://support.mozilla.org/en-US/questions/1264280
        // change privacy_file_unique_origin to false in about:config
        // https://towardsdatascience.com/how-to-deploy-tensorflow-models-to-the-web-81da150f87f7
        const loadedModel = await tf.loadLayersModel('model/my_model.json');
        console.log(loadedModel);
        return loadedModel;
    };
    
    function predict(loadedModel) {
        // take user's input
        const userInput = document.getElementById('userInput').value
        const inputTensor = tf.tensor([parseInt(userInput)]).reshape([1, 1]);  
        const normalizedInput = inputTensor.sub(inputMin).div(inputMax.sub(inputMin));             
        console.log('Normalized User\'s input value and shape:', normalizedInput.dataSync()[0], normalizedInput.shape);

        // load model and predict the result
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
        const normalizedPrediction = loadedModel.then(loadedModel => {
            let normalizedPrediction = loadedModel.predict(normalizedInput);
            // console.log(normalizedPrediction.dataSync()[0]);
            return normalizedPrediction
        })

        // overwrite element 'result' with predicted value
        // https://dev.to/ramonak/javascript-how-to-access-the-return-value-of-a-promise-object-1bck
        const displayResult = async () => {
            const prediction = await normalizedPrediction;
            unNormalizedPrediction = prediction.mul(labelMax.sub(labelMin)).add(labelMin)
            document.getElementById('result').innerHTML = tf.round(unNormalizedPrediction).dataSync()[0];
            console.log('Prediction (un-normalized):', tf.round(unNormalizedPrediction).dataSync()[0]);
        }
        displayResult();

    }

    // load model immediately to avoid delay when user clicks 'Predict'
    const loadedModel = loadModel();  
    console.log('Model loaded');