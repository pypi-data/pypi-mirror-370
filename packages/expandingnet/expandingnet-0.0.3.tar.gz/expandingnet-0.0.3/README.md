# ExpandingNet: new data-driven neural network

## Project description

Author: Kaike Sa Teles Rocha Alves

ExpandingNet is a package that contains a new data-driven neural network developed by Kaike Alves. 

    Author: Kaike Sa Teles Rocha Alves (PhD)
    Email: kaikerochaalves@outlook.com or kaike.alves@estudante.ufjf.br


Doi to cite the code: http://dx.doi.org/10.5281/zenodo.16898511

Github repository: https://github.com/kaikerochaalves/ExpandingNet.git

Cite:

## Description:

ExpandingNet: An Expanding Neural Network model that dynamically adjusts its
architecture during training.

The aim is to find the optimal network structure for a given regression task.

This class implements a neural network that can grow by adding neurons to its hidden
layers and potentially adding new hidden layers based on the validation
performance. It aims to find an optimal network structure for a given
regression task.

One relevant note about this approach is that every layer is connected to
the original inputs, and the previous hidden layer and output, keeping
track of the errors

The growth process involves two main phases:
1.  **Layer Expansion:** The last hidden layer is incrementally expanded by
    adding neurons until performance on a validation set no longer improves
    or a maximum number of neurons is reached.
2.  **Network Deepening (Optional, with Cross-Validation):** If
    `cross_validation` is True, new hidden layers are added sequentially.
    The input to each new layer includes the original input features and the
    outputs (and hidden activations) of the preceding layer. Each new layer
    also undergoes an expansion phase. If `cross_validation` is False,
    new layers are added, and their inputs are concatenated similarly, but
    the training data splitting is not managed by TimeSeriesSplit.

The model uses early stopping based on a patience parameter to prevent
overfitting during the expansion of each layer. Learning rate decay is
also applied.

Summary:
    
Core Architecture: It's an Adaptive Multi-Layer Perceptron (AMLP). \
    This is crucial. It uses a series of MLP layers.

Unique Components/Innovations:

Dynamic Growth: The model starts small (1 neuron in the first hidden layer)
and expands both the number of neurons within a layer (expand_layer) 
and can deepen by adding new hidden layers. This "growth" or "evolution" 
is a major differentiator.

Adaptive Nature: It adapts its structure based on validation performance, 
using early stopping and learning rate decay during expansion. 
This speaks to its intelligence and efficiency.

Residual-like Connections: "Every layer is connected to the original inputs, 
and the previous hidden layer and output, keeping track of the errors." 
This is a significant architectural feature, akin to skip connections
or a residual network structure, allowing information to flow more directly 
and combatting vanishing gradients. This is a very powerful concept for deep networks.

Time Series Specific: Explicitly uses TimeSeriesSplit for cross-validation 
when adding new layers, making it inherently suited for time series data.

Primary Advantages/Selling Points:

Optimal Structure: Aims to "find the optimal network structure." 
This implies efficiency and custom fit.

Robustness/Performance: The adaptive nature, early stopping,
and learning rate decay suggest robustness and good performance.

Scalability: Can grow in depth and width.

Problem Solved: Time series forecasting with a focus on finding the
optimal network structure dynamically.

## Instructions

To install the library use the command: 

    pip install expandingnet

The library provides 6 models in fuzzy systems, as follows:

To import the ExpandingNet, simply type the command:

    from expandingnet.NN import ExpandingNet

Hyperparameters:

    n_min_neurons : int, default=50
    Minimum number of neurons a hidden layer can have after its initial
    creation (layers start with 1 neuron and expand). This ensures a
    minimum complexity.

    n_max_neurons : int, default=300
    Maximum number of neurons a hidden layer can grow to. This sets an
    upper bound on the size of individual hidden layers.

    n_hidden_layers : int, default=5
    The target number of hidden layers the model will attempt to create.
    If `cross_validation` is True, this also defines the number of splits
    for the `TimeSeriesSplit` mechanism, dictating the number of layers
    built via cross-validation.

    cross_validation : bool, default=False
    Controls the strategy for adding new hidden layers:
    - If `True`, new layers are added using an expanding window
    cross-validation strategy via `sklearn.model_selection.TimeSeriesSplit`.
    Each new layer's training uses a progressively larger historical data window.
    - If `False`, new layers are added sequentially without explicit
    time series cross-validation splitting within the `fit` method;
    the model will simply grow layer by layer on the provided `X_train` and `X_val`.

    lr : float, default=0.01
    The initial learning rate used for the Adam optimizer when training
    each `Net` (sub-network) and during layer expansion.

    lr_decay_rate : float, default=0.99
    The factor by which the learning rate is multiplied (decayed) upon
    observing an improvement in the validation loss for the current layer
    being optimized. This helps fine-tune the model as it converges.

    max_patience : int, default=5
    The number of consecutive epochs or neuron expansions without a significant
    improvement (as defined by `tol`) in validation loss before the growth
    of the current hidden layer is halted. This is a form of early stopping
    to prevent overfitting during layer adaptation.

    tol : float, default=0
    Tolerance value for considering an improvement in validation loss.
    If `new_validation_loss - best_validation_loss < tol`, it is considered
    an improvement, and the patience counter is reset. A value of 0 means
    any reduction is considered an improvement.

    disp : bool, default=True
    If `True`, the model will print the current layer size and its
    corresponding validation loss during the training and expansion process,
    providing real-time feedback on the model's adaptation.

Example of ExpandingNet:

    from expandingnet.NN import ExpandingNet
    model = ExpandingNet()
    model.fit(X_train, y_train, X_val, y_val)
    y_pred = model.predict(X_test)

### Extra information

The fuzzy models are quite fast, but the genetic and ensembles are still a bit slow. If you think you can contribute to this project regarding the code, speed, etc., please, feel free to contact me and to do so.

Code of Conduct:

Please read the Code of Conduct for guidance.

Call for Contributions:

The project welcomes your expertise and enthusiasm!

Small improvements or fixes are always appreciated. If you are considering larger contributions to the source code, please contact by email first.