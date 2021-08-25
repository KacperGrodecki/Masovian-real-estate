console.log('Hello TensorFlow');


// Load and format input data
/**
 * Get the car data reduced to just the variables we are interested and cleaned of missing data.
 */
async function getData() {
    const carsDataResponse = await fetch('https://storage.googleapis.com/tfjs-tutorials/carsData.json');
    const carsData = await carsDataResponse.json();
    const cleaned = carsData.map(car => ({
        mpg: car.Miles_per_Gallon,
        horsepower: car.Horsepower,
    })).filter(car => (car.mpg != null && car.horsepower != null));

    // https://stackoverflow.com/questions/3580239/javascript-array-get-range-of-items
    // console.log(cleaned[4]);
    // console.log(cleaned.slice(0, 4));
    return cleaned;
}


// Visualize formated input data
async function run() {
    // Load and plot the original input data that we are going to train on.
    const data = await getData();
    const values = data.map(d => ({
        x: d.horsepower,
        y: d.mpg,
    }));

    tfvis.render.scatterplot(
        {name: 'Horsepower vs. MPG'},
        {values},
        {
            xLabel: 'Horsepower',
            yLabel: 'MPG',
            height: 300
        }
    );

    // Convert the data to a form we can use for training.
    const tensorData = convertToTensor(data);
    const {inputs, labels} = tensorData;

    /**
     * https://stackoverflow.com/questions/762011/whats-the-difference-between-using-let-and-var
     * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let
     * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
     */
    // {
    //     let{a, b} = {a: 'apple', b: 'banana'};
    //     console.log(JSON.stringify(a));
    // }

    // Train the model
    await trainModel(model, inputs, labels);
    console.log('Done Training');

    // Make predictions
    /**
     * Make some predictions using the model and compare them to the original data
     */
    testModel(model, data, tensorData);
}


// Define the model architecture
/**
 * (which functions will the model run when it is executing", or alternatively "what algorithm will our model use to compute its answers").
 */
function createModel() {
    // Create a sequential model
    const model = tf.sequential();

    // Add a single input layer
    model.add(tf.layers.dense({inputShape: [1], units: 1, useBias: true}));

    // Add another hidden layer(s)
    model.add(tf.layers.dense({units: 50, activation: 'sigmoid'}));
    model.add(tf.layers.dense({units: 50, activation: 'sigmoid'}));
    model.add(tf.layers.dense({units: 50, activation: 'sigmoid'}));
    model.add(tf.layers.dense({units: 50, activation: 'sigmoid'}));
    model.add(tf.layers.dense({units: 50, activation: 'sigmoid'}));


    // Add an output layer
    model.add(tf.layers.dense({units: 1, useBias: true}));

    return model;
    }

const model = createModel();
tfvis.show.modelSummary({name: 'Model Summary'}, model);


// Prepare the data for training
/** 
 * Convert the input data to tensors that we can use for machine learning.
 * We will also do the important best practices of _shuffling_ the data and _normalizing_ the data MPG on the y-axis.
 */
function convertToTensor(data) {
  // Wrapping these calculations in a tidy will dispose any intermediate tensors.
  return tf.tidy(() => {
      // Step 1. Shuffle the data
      tf.util.shuffle(data);

      // Step 2. Convert data to Tensor
      const inputs = data.map(d => d.horsepower);
      const labels = data.map(d => d.mpg);

      const inputTensor = tf.tensor2d(inputs, [inputs.length, 1]);
      const labelTensor = tf.tensor2d(labels, [labels.length, 1]);

      // Step 3. Normalize the data to the range 0 - 1 using min-max scaling
      const inputMax = inputTensor.max();
      const inputMin = inputTensor.min();
      const labelMax = labelTensor.max();
      const labelMin = labelTensor.min();
      
      const normalizedInputs = inputTensor.sub(inputMin).div(inputMax.sub(inputMin));
      const normalizedLabels = labelTensor.sub(labelMin).div(labelMax.sub(labelMin));

      return {
          inputs: normalizedInputs,
          labels: normalizedLabels,
          // Return the min/max bounds so we can use them later.
          /**
           * We want to keep the values we used for normalization during training so that we can un-normalize the outputs to get them back into our original scale and to allow us to normalize future input data the same way.
           */
          inputMax,
          inputMin,
          labelMax,
          labelMin,
      }
  });
}


// Train the model
async function trainModel(model, inputs, labels) {
  // Prepare the model for training.
  model.compile({
      optimizer: tf.train.adam(),
      loss: tf.losses.meanSquaredError,
      metrics: ['mse'],
  });

  const batchSize = 32;
  const epochs = 200;

  return await model.fit(inputs, labels, {
      batchSize,
      epochs,
      shuffle: true,
      callbacks: tfvis.show.fitCallbacks(
          {name: 'Training Performance'},
          ['loss', 'mse'],
          {height: 200, callbacks: ['onEpochEnd']}
      )
  });
}


// Make Predictions
function testModel(model, inputData, normalizationData) {
    const {inputMax, inputMin, labelMax, labelMin} = normalizationData;

    /** Generate predictions for a uniform range of numbers between 0 and 1;
     * We un-normalize the data by doing the inverse of the min-max scaling that we did earlier.
     */

    const [xs, preds] = tf.tidy(() =>{
        
        const xs = tf.linspace(0, 1, 100);
        const preds = model.predict(xs.reshape([100, 1])); // [num_examples, num_features_per_example]

        const unNormXs = xs.mul(inputMax.sub(inputMin)).add(inputMin);

        const unNormPreds = preds.mul(labelMax.sub(labelMin)).add(labelMin);

        // Un-normalize the data
        // https://stackoverflow.com/questions/63985396/what-do-i-use-instead-of-tensor-datasync-to-get-the-predicted-value-in-tensorf
        // https://meowni.ca/posts/on-tfjs-datasync/
        return [unNormXs.dataSync(), unNormPreds.dataSync()]; // .dataSync() is a method we can use to get a typedarray of the values stored in a tensor
    });
    
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/from   
    const predictedPoints = Array.from(xs).map((val, i) => {
        return {x: val, y: preds[i]}        
    });
    // console.log(predictedPoints);

    // const originalPoints = inputData;
    const originalPoints = inputData.map(d => ({
        x: d.horsepower, y: d.mpg,
    }));
    // console.log(originalPoints.slice(0,4));

    tfvis.render.scatterplot(
        {name: 'Model Predictions vs Original Data'},
        {values: [originalPoints, predictedPoints], series: ['original', 'predicted']},
        {
            xLabel: 'Horsepower',
            yLabel: 'MPG',
            height: 300
        }
    );
}



// Console
document.addEventListener('DOMContentLoaded', run);
document.addEventListener('DOMContentLoaded', (event) => {console.log('DOM fully loaded and parsed')});


