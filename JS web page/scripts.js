// https://www.handsonembedded.com/hands-on-aiot-simple-linear-regression/simple-linear-regression-in-tensorflow-js-with-bootstrap/


// Load file with normalization parameters
// https://stackoverflow.com/questions/49432579/await-is-only-valid-in-async-function
async function fetchNormalizationParameters() {
    // Load normalization parameters
    const result = await fetch('https://raw.githubusercontent.com/matthiaskozubal/tests/0b15e0516d72f8a4e58adc8cd215de45b45448ef/normalization_parameters.json'); // https://github.com/matthiaskozubal/tests/blob/0b15e0516d72f8a4e58adc8cd215de45b45448ef/normalization_parameters.json
    const NormalizationParameters = await result.json();
    // console.log('Normalization parameters inputMax:', NormalizationParameters.inputMax);
    return NormalizationParameters
}


// Manually declared normalization parameters
// const inputMax = tf.tensor(230);
const inputMin = tf.tensor(46);
const labelMax = tf.tensor(46.599998474121094);
const labelMin = tf.tensor(9);  


// Model loading
async function loadModel() {
        // https://support.mozilla.org/en-US/questions/1264280
        // change privacy_file_unique_origin to false in about:config
        // https://towardsdatascience.com/how-to-deploy-tensorflow-models-to-the-web-81da150f87f7
        const loadedModel = await tf.loadLayersModel('https://raw.githubusercontent.com/matthiaskozubal/tests/main/cars_my_model.json');
        console.log('Model: ', loadedModel);
        return loadedModel;
    };
    

function getUserInput() {
    const userInput = document.getElementById('userInput').value;
    const inputTensor = tf.tensor([parseInt(userInput)]).reshape([1, 1]);  


    // This is the way
    const modelParameters = ['lPokoi', 'powierzchnia_corr', 'powierzchniaDzialki_corr', 'rokBudowy_corr', 'cena/m', 'lPieter_crr', 'locationX', 'locationY', 'rodzajZabudowy_0', 'rodzajZabudowy_bliźniak', 'rodzajZabudowy_dworek/pałac', 'rodzajZabudowy_gospodarstwo', 'rodzajZabudowy_kamienica', 'rodzajZabudowy_szeregowiec', 'rodzajZabudowy_wolnostojący', 'materialBudynku_0', 'materialBudynku_beton', 'materialBudynku_beton_komórkowy', 'materialBudynku_cegła', 'materialBudynku_drewno', 'materialBudynku_inne', 'materialBudynku_keramzyt', 'materialBudynku_pustak', 'materialBudynku_silikat', 'stanWykonczenia_0', 'stanWykonczenia_do_remontu', 'stanWykonczenia_do_wykończenia', 'stanWykonczenia_do_zamieszkania', 'stanWykonczenia_stan_surowy_otwarty', 'stanWykonczenia_stan_surowy_zamknięty', 'okna_0', 'okna_aluminiowe', 'okna_brak', 'okna_drewniane', 'okna_plastikowe', 'rynek_pierwotny', 'rynek_wtórny'];
    inputsTensor = tf.tensor([]);
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach
    modelParameters.forEach(
        (element, idx) => {
            let element_value = document.getElementById('userInput_'+element).value
            inputsTensor = tf.concat([inputsTensor, tf.tensor([parseInt(element_value)])], 0) // parseInt(element_value)
            // console.log(idx, ': ', 'userInput_'+element, ' = ', element_value)
        }
            
    )
    inputsTensor.print();
    // console.log(modelParameters.length, inputsTensor.shape);



    return inputTensor    
};

    
// Predict with model loaded from file
async function predict(loadedModel) {
    // take User input and normalize it
    const inputTensor = getUserInput();

    // normalize user input
    const normalizationParameters = await fetchNormalizationParameters();
    const inputMax = tf.tensor(normalizationParameters.inputMax);
    const inputMin = tf.tensor(normalizationParameters.inputMin);
    const labelMax = tf.tensor(normalizationParameters.labelMax);
    const labelMin = tf.tensor(normalizationParameters.labelMin);
    // console.log('Normalization parameters inputMax:', inputMax);
    
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