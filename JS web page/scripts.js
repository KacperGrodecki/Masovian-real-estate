// https://www.handsonembedded.com/hands-on-aiot-simple-linear-regression/simple-linear-regression-in-tensorflow-js-with-bootstrap/


// Model loading
async function loadModel() {
    // https://support.mozilla.org/en-US/questions/1264280
    // change privacy_file_unique_origin to false in about:config
    // https://towardsdatascience.com/how-to-deploy-tensorflow-models-to-the-web-81da150f87f7
    // const loadedModel = await tf.loadLayersModel('https://raw.githubusercontent.com/KacperGrodecki/nieruchomosci-mazowieckie/0.0.4/jsmodel_norm/model.json');
    const loadedModel = await tf.loadLayersModel('https://raw.githubusercontent.com/KacperGrodecki/nieruchomosci-mazowieckie/0.0.4/jsmodel/model.json');
    console.log('Model: ', loadedModel);
    return loadedModel;
    };
    

// load model immediately to avoid delay when user clicks 'Predict'
const loadedModel = loadModel();  
console.log('Model loaded');




// Taking user input parameters and returnig them as tensor
function getUserInput() {
    // Define model parameters
    const modelParameters = ['lPokoi', 'powierzchnia_corr', 'powierzchniaDzialki_corr', 'rokBudowy_corr', 'lPieter_crr', 'locationX', 'locationY', 'rodzajZabudowy_0', 'rodzajZabudowy_bliźniak', 'rodzajZabudowy_dworek/pałac', 'rodzajZabudowy_gospodarstwo', 'rodzajZabudowy_kamienica', 'rodzajZabudowy_szeregowiec', 'rodzajZabudowy_wolnostojący', 'materialBudynku_0', 'materialBudynku_beton', 'materialBudynku_beton_komórkowy', 'materialBudynku_cegła', 'materialBudynku_drewno', 'materialBudynku_inne', 'materialBudynku_keramzyt', 'materialBudynku_pustak', 'materialBudynku_silikat', 'stanWykonczenia_0', 'stanWykonczenia_do_remontu', 'stanWykonczenia_do_wykończenia', 'stanWykonczenia_do_zamieszkania', 'stanWykonczenia_stan_surowy_otwarty', 'stanWykonczenia_stan_surowy_zamknięty', 'okna_0', 'okna_aluminiowe', 'okna_brak', 'okna_drewniane', 'okna_plastikowe', 'rynek_pierwotny', 'rynek_wtórny'];
 
    // Fetch user-provided values for model parameters
    inputsTensor = tf.tensor([]);
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach
    modelParameters.forEach(
        (element, idx) => {
            let element_value = document.getElementById('userInput_'+element).value
            inputsTensor = tf.concat([inputsTensor, tf.tensor([parseInt(element_value)])], 0) // parseInt(element_value)
            // console.log(idx, ': ', 'userInput_'+element, ' = ', element_value)
        }
    )
    // console.log(modelParameters.length, inputsTensor.shape);
    // inputsTensor.print();

    // Normalize user input parameters
    inputsTensor = normalizeUserInput(inputsTensor);

    return inputsTensor    
};


async function normalizeUserInput(inputsTensor) {
    // https://stackoverflow.com/questions/49802499/how-do-i-mutate-value-of-a-tensor-in-tensorflow-js
    const inputsTensor_buffer = tf.buffer(inputsTensor.shape, inputsTensor.dtype, inputsTensor.dataSync());
    inputsTensor_buffer.set(inputsTensor.dataSync()[0]/10, 0);                                                      // 0 - "lPokoi"/10
    inputsTensor_buffer.set(tf.log(inputsTensor.dataSync()[1]).dataSync()/10, 1);     // 1 - "powierzchnia_corr"/10
    inputsTensor_buffer.set(tf.log(inputsTensor.add(tf.tensor(1))).dataSync()[2]/14, 2);      // 2 - log("powierzchniaDzialki_corr"+1)/14
    inputsTensor_buffer.set(tf.pow(inputsTensor.sub(tf.fill(inputsTensor.shape, 1899)), 4).dataSync()[3]/3e8, 3);   // 3 - ("rokBudowy_corr"-1899)^4/3e8
    inputsTensor_buffer.set(inputsTensor.dataSync()[4]/10, 4);                                                      // 4 - "lPieter_crr"/10
    inputsTensor_buffer.set((inputsTensor.dataSync()[5]-21)/4, 5);                                                  // 5 - ("locationX"-21)/4"
    inputsTensor_buffer.set((inputsTensor.dataSync()[6]-52)/2, 6);                                                  // 6 - ("locationY"-52)/2"

    const inputsTensorNormalized = inputsTensor_buffer.toTensor();
    // console.log('inputsTensorNormalized:', inputsTensorNormalized.dataSync()[6])
    tf.slice(inputsTensorNormalized, 0, 7).print();
    // inputsTensorNormalized.print();

    return inputsTensorNormalized
}









// Predict with model loaded from file
async function predict(loadedModel) {
    // Take User input (already normalized)
    var inputsTensor = await getUserInput();
    
    // Reshape User input (I wasn't able to do it in getUserInput(), because it was a Promise there)
    inputsTensor = inputsTensor.reshape([1, inputsTensor.shape[0]]);
    console.log('inputsTensor.shape: ', inputsTensor.shape);
    console.log('inputsTensor: ', inputsTensor.dataSync());

    // load model and predict the result
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
    const normalizedPrediction = loadedModel.then(loadedModel => {
        let normalizedPrediction = loadedModel.predict(inputsTensor); // .cast('float32')
        // console.log(normalizedPrediction.dataSync()[0]);
        return normalizedPrediction
    })

    // overwrite element 'result' with predicted value
    // https://dev.to/ramonak/javascript-how-to-access-the-return-value-of-a-promise-object-1bck
    const displayResult = async () => {
        const prediction = await normalizedPrediction;
        unNormalizedPrediction = prediction.mul(20000); // unNormalize: "cena/m"*20000
        document.getElementById('result').innerHTML = tf.round(unNormalizedPrediction).dataSync()[0];
        console.log('Prediction (un-normalized):', tf.round(unNormalizedPrediction).dataSync()[0]);
    }
    displayResult();

}