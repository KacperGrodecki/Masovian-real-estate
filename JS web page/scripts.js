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

    // Paremeters with value entered into a box
    const valueParametersDict = ['lPokoi', 'powierzchnia_corr', 'powierzchniaDzialki_corr', 'rokBudowy_corr', 'lPieter_crr', 'locationX', 'locationY'];
    // Fetch user-provided values for model parameters
    inputsTensorValueParameters = tf.tensor([]);
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach
    valueParametersDict.forEach(
        (element, idx) => {
            let element_value = document.getElementById('userInput_'+element).value
            inputsTensorValueParameters = tf.concat([inputsTensorValueParameters, tf.tensor([parseInt(element_value)])], 0) // parseInt(element_value)
            // console.log(idx, ': ', 'userInput_'+element, ' = ', element_value)
        }
    )
    // console.log('inputsTensorValueParameters:', inputsTensorValueParameters.shape);
    // inputsTensorValueParameters.print();

    // Parameters selectable from drop-down list
    const listParametersDict = {
        'rodzajZabudowy':  ['rodzajZabudowy_0', 'rodzajZabudowy_bliźniak', 'rodzajZabudowy_dworek/pałac', 'rodzajZabudowy_gospodarstwo', 'rodzajZabudowy_kamienica', 'rodzajZabudowy_szeregowiec', 'rodzajZabudowy_wolnostojący'],
        'materialBudynku': ['materialBudynku_0', 'materialBudynku_beton', 'materialBudynku_beton komórkowy', 'materialBudynku_cegła', 'materialBudynku_drewno', 'materialBudynku_inne', 'materialBudynku_keramzyt', 'materialBudynku_pustak', 'materialBudynku_silikat'],
        'stanWykonczenia': ['stanWykonczenia_0', 'stanWykonczenia_do remontu', 'stanWykonczenia_do wykończenia', 'stanWykonczenia_do zamieszkania', 'stanWykonczenia_stan surowy otwarty', 'stanWykonczenia_stan surowy zamknięty'],
        'okna':            ['okna_0', 'okna_aluminiowe', 'okna_brak', 'okna_drewniane', 'okna_plastikowe'],
        'rynek':           ['rynek_pierwotny', 'rynek_wtórny']
    };
    inputsTensorListParameters = tf.tensor([]);
    // console.log(inputsTensorListParameters.shape);
    for (const [key, value] of Object.entries(listParametersDict)) {
        // get value (position for which tensor will have 1 instead of 0)
        let listParameter_value = document.getElementById('userInputSelect_'+key).value;
        
        // create temporary tensor with zeros and 1 in a position corresponding to the user input
        const temporary_buffer = tf.buffer([listParametersDict[key].length], 0);
        temporary_buffer.set(1, parseInt(listParameter_value)); // set value 1 at [location_corresponding_to_the_user_input]
        const temporary_tensor = temporary_buffer.toTensor();       
        inputsTensorListParameters = tf.concat([inputsTensorListParameters, temporary_tensor], 0);
        // inputsTensorListParameters.print();
        // console.log(inputsTensorListParameters.shape)
 
        // log
        // console.log(key, '->', value[parseInt(listParameter_value)], ', position (from 0) -', parseInt(listParameter_value));//, temporary_tensor.shape);
        // temporary_tensor.print();
    }
    // console.log('inputsTensorListParameters:', inputsTensorListParameters.dataSync());
    // inputsTensorListParameters.print();

    // Concat list-parameters and value-parameters
    inputsTensor = tf.tensor([]);
    inputsTensor = tf.concat([inputsTensorValueParameters, inputsTensorListParameters], 0)
    console.log('inputsTensor:', inputsTensor.shape, inputsTensor.dataSync());
    inputsTensor.print();    

    // Normalize user input parameters
    inputsTensor = normalizeUserInput(inputsTensor);
    return inputsTensor    
};


async function normalizeUserInput(inputsTensor) {
    // https://stackoverflow.com/questions/49802499/how-do-i-mutate-value-of-a-tensor-in-tensorflow-js
    const inputsTensor_buffer = tf.buffer(inputsTensor.shape, inputsTensor.dtype, inputsTensor.dataSync());
    inputsTensor_buffer.set(inputsTensor.dataSync()[0]/10, 0);                                                                      // 0 - "lPokoi"/10
    inputsTensor_buffer.set(tf.log(inputsTensor).div(tf.log(10)).div(tf.tensor(10)).dataSync()[1], 1);                              // 1 - log10("powierzchnia_corr")/10
    inputsTensor_buffer.set(tf.log(inputsTensor.add(tf.tensor(1))).div(tf.log(tf.tensor(10))).div(tf.tensor(14)).dataSync()[2], 2); // 2 - log10("powierzchniaDzialki_corr"+1)/14
    inputsTensor_buffer.set(tf.pow(inputsTensor.sub(tf.fill(inputsTensor.shape, 1899)), 4).div(tf.tensor(3e8)).dataSync()[3], 3);   // 3 - ("rokBudowy_corr"-1899)^4/3e8
    inputsTensor_buffer.set(inputsTensor.div(tf.tensor(10)).dataSync()[4], 4);                                                      // 4 - "lPieter_crr"/10
    inputsTensor_buffer.set(inputsTensor.sub(tf.tensor(21)).div(tf.tensor(4)).dataSync()[5], 5);                                    // 5 - ("locationX"-21)/4"
    inputsTensor_buffer.set(inputsTensor.sub(tf.tensor(52)).div(tf.tensor(2)).dataSync()[6], 6);                                    // 6 - ("locationY"-52)/2"

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
    const normalizedPrediction = (await loadedModel).predict(inputsTensor);

    // overwrite element 'result' with predicted value
    // https://dev.to/ramonak/javascript-how-to-access-the-return-value-of-a-promise-object-1bck
    const displayResult = async () => {
        const prediction = await normalizedPrediction;
        unNormalizedPrediction = prediction.mul(20000); // unNormalize: "cena/m"*20000
        document.getElementById('predicted_price_per_m2').innerHTML = tf.round(unNormalizedPrediction).dataSync()[0];
        document.getElementById('predicted_price').innerHTML = tf.round(unNormalizedPrediction.mul(tf.pow(10, tf.tensor(inputsTensor.dataSync()[1]).mul(tf.tensor(10))))).dataSync()[0];
        console.log('Prediction (un-normalized):', tf.round(unNormalizedPrediction).dataSync()[0], tf.round(unNormalizedPrediction.mul(tf.pow(10, tf.tensor(inputsTensor.dataSync()[1]).mul(tf.tensor(10))))).dataSync()[0]);
    }
    displayResult();
}


