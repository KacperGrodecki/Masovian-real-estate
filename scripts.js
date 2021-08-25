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

    // Train the model
    await trainModel(model, inputs, labels);
    console.log('Done Training');
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
  const epochs = 100;

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


// Console
document.addEventListener('DOMContentLoaded', run);
document.addEventListener('DOMContentLoaded', (event) => {console.log('DOM fully loaded and parsed')});