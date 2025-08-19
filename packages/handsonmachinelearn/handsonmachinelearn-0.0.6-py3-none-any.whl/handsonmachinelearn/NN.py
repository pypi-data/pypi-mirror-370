# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:19:04 2025

@author: Kaike Sa Teles Rocha Alves
@email_1: kaikerochaalves@outlook.com
@email_2: kaike.alves@estudante.ufjf.br

As a Data Science Manager at PGE-PR and a Ph.D. in Computational Modeling
at the Federal University of Juiz de Fora (UFJF), I specialize in artificial
intelligence, focusing on the study, development, and application of machine
learning models. My academic journey includes a scholarship that allowed me
to pursue a year of my Ph.D. at the University of Nottingham/UK, where I was
a member of the LUCID (Laboratory for Uncertainty in Data and Decision Making)
under the supervision of Professor Christian Wagner. My background in Industrial
Engineering provides me with a holistic view of organizational processes,
enabling me to propose efficient solutions and reduce waste.
"""

# Libraries
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from copy import deepcopy
import torch.nn.functional as F

# Import the library to perform expanding window cross validation
from sklearn.model_selection import TimeSeriesSplit

# Net is a base class to create a new Net model with a input size, one single
# hidden layer with the number of neurons specified by the user, and one
# output size
class Net(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, X, get_hidden=False):
        hidden = F.relu(self.fc1(X))
        output = self.fc2(hidden)
        if get_hidden:
            return output, hidden
        else:
            return output

# Class used to create an adaptive Net
class ExpandingNet():

    """
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
        
        
    Attributes:
        
        n_min_neurons (int): Minimum number of neurons a hidden layer can have
                             after its initial creation (starts with 1 and expands).
        n_max_neurons (int): Maximum number of neurons a hidden layer can grow to.
        n_hidden_layers (int): The target number of hidden layers to create if
                               `cross_validation` is False, or the number of splits
                               for TimeSeriesSplit if `cross_validation` is True,
                               which dictates the number of layers.
        cross_validation (bool): If True, uses TimeSeriesSplit for creating
                                 training/validation sets when adding new layers.
        lr (float): Initial learning rate for the Adam optimizer.
        original_lr (float): Stores the initial learning rate for resets.
        lr_decay_rate (float): Factor by which the learning rate is multiplied
                               upon improvement.
        tol (float): Tolerance for improvement. If `val_loss - best_loss < tol`,
                     it's considered an improvement.
        patience (int): Current patience counter for early stopping.
        max_patience (int): Number of epochs/expansions with no improvement
                            before stopping the growth of a layer.
        hidden_size (int): Current number of neurons in the hidden layer being expanded.
        input_size (int): Number of features in the input data.
        current_input_size (int): Input size for the current Net being trained
                                  (can change if inputs are concatenated from
                                  previous layers).
        output_size (int): Number of output neurons (typically 1 for regression).
        best_model (torch.nn.Module): The Net configuration with the best
                                      validation loss found so far for the current
                                      layer being optimized.
        best_loss (float): The best validation loss achieved for the current
                           layer being optimized.
        best_global_loss (float): The best validation loss achieved across all
                                  layers and expansions.
        criterion (torch.nn.MSELoss): The loss function used for training (Mean
                                      Squared Error).
        nets (torch.nn.ModuleList): A list to store the individual Net
                                    (sub-)networks that form the layers of the
                                    adaptive Net.
        optimizer (torch.optim.Optimizer): The optimizer used for training.
        expand (bool): A flag to control the layer expansion loop.
    """

    # Init the model
    def __init__(self, n_min_neurons=50, n_max_neurons=300, n_hidden_layers=5, cross_validation=False, lr=0.01, lr_decay_rate=0.99, max_patience=5, tol=0, disp=True):
        
        r"""ExpandingNet is a neural network specially designed for Time Series Forecasting.

        This model dynamically builds and optimizes its neural network architecture
        for regression tasks, specifically designed with time series cross-validation
        capabilities. It aims to find an optimal network structure by incrementally
        expanding hidden layers (adding neurons) and deepening the network (adding
        new hidden layers). Each new layer integrates the original inputs along with
        the outputs and hidden activations from preceding layers, creating a robust
        information flow similar to residual connections.
    
        The growth process is guided by validation performance, incorporating early
        stopping and learning rate decay to prevent overfitting and ensure efficient
        adaptation.
    
        Parameters
        ----------
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
        """
        
        # Hyperparameters
        self.n_min_neurons = n_min_neurons
        self.n_max_neurons = n_max_neurons
        self.n_hidden_layers = n_hidden_layers
        self.cross_validation = cross_validation
        self.lr = lr
        self.original_lr = lr
        self.lr_decay_rate = lr_decay_rate
        self.tol = tol
        self.patience = 0
        self.max_patience = max_patience
        self.hidden_size = 1
        self.disp = disp
        # Parameters
        self.input_size = None
        self.current_input_size = None
        self.output_size = None
        self.best_model = None
        self.best_loss = None
        self.best_global_loss = None
        # MSE loss
        self.criterion = nn.MSELoss()
        # Store the networks
        self.nets = nn.ModuleList()

    # Call the function fit to train the model
    def fit(self, X_train, y_train, X_val, y_val, epochs=1):
        
        # Shape of X and y
        X_train_shape, X_val_shape = X_train.shape, X_val.shape
        y_train_shape, y_val_shape = y_train.shape, y_val.shape
        
        # # Check wheather y is 1d
        # if (len(y_train_shape) > 1 and y_train_shape[1] > 1) or (len(y_val_shape) > 1 and y_val_shape[1] > 1):
        #     raise TypeError(
        #         "This algorithm does not support multiple outputs. "
        #         "Please, give only single outputs instead."
        #     )
        
        # if len(y_shape) > 1:
            
        #     # 1d
        #     y = y.ravel()
            
        #     # Get new shape of y
        #     y_shape = y.shape
        
        # Check wheather y is 1d
        if (X_train_shape[0] != y_train_shape[0]) or (X_val_shape[0] != y_val_shape[0]):
            raise TypeError(
                "The number of samples of X are not compatible with the number of samples in y. "
            )
            
        # Check if the inputs contain valid numbers
        if (not self.is_numeric_and_finite(X_train)) or (not self.is_numeric_and_finite(X_val)):
            raise ValueError(
                "X contains incompatible values."
                " Check X for non-numeric or infinity values"
            )
            
        # Check if the inputs contain valid numbers
        if (not self.is_numeric_and_finite(y_train)) or (not self.is_numeric_and_finite(y_val)):
            raise ValueError(
                "y contains incompatible values."
                " Check y for non-numeric or infinity values"
            )
        
        # Apply the conditional conversion
        X_train = self.to_tensor_if_needed(X_train)
        y_train = self.to_tensor_if_needed(y_train)
        X_val = self.to_tensor_if_needed(X_val)
        y_val = self.to_tensor_if_needed(y_val)
        
        if len(y_train.shape) == 1:
            y_train = y_train.unsqueeze(1)
            
        if len(y_val.shape) == 1:
            y_val = y_val.unsqueeze(1)

        # Gets the number of features in your training data, which will be the input size for the neural network
        self.input_size = X_train.shape[1]
        # The number of inputs for the current Net
        # It will increase after the first expansion
        self.current_input_size = self.input_size
        # This sets the number of output neurons to 1
        self.output_size = 1

        # An initial Net is created. At this point, it has an input layer, an output layer, and one hidden layer with one neuron
        self.Net = Net(self.input_size, self.hidden_size, self.output_size)
        # Store the models in a list
        self.nets.append(self.Net)
        # The current self.model is trained for the same number of epochs as number of neurons in the hidden size
        self.nets[-1] = self.train(self.nets[-1], X_train, y_train, epochs=self.hidden_size)
        # Save the initial Net for current state
        self.best_model = deepcopy(self.nets[-1])
        # The trained model is evaluated on the validation set, and the validation loss is stored
        self.val_loss = self.evaluate(self.nets[-1], X_val, y_val)
        # Initialize the best loss and best global loss
        self.best_loss = self.val_loss
        self.best_global_loss = self.val_loss
        # Print loss if self.disp is True
        if self.disp == True:
            print(f"Layer sizes: {self.hidden_size}, Validation Loss: {self.val_loss:.4f}")

        # Keep expanding the hidden layer with expanding is True
        self.expand = True

        while self.expand:

            # Expand last layer
            self.nets[-1] = self.expand_layer(self.nets[-1])
            # Train the current expanded model
            self.nets[-1] = self.train(self.nets[-1], X_train, y_train, epochs=self.hidden_size)
            # The trained model is evaluated on the validation set and the validation loss is stored.
            self.val_loss = self.evaluate(self.nets[-1], X_val, y_val)
            # Print loss if disp is True
            if self.disp == True:
                print(f"Layer sizes: {self.hidden_size}, Validation Loss: {self.val_loss:.4f}")

            # Evaluate the performance of the current model
            if (self.val_loss - self.best_loss) < self.tol:
                # If the new model have reduced loss, reset self.patience
                self.patience = 0
                # Update the new best loss
                self.best_loss = self.val_loss
                # Check if the current loss is the best loss among all steps
                if self.val_loss - self.best_global_loss < self.tol:
                    self.best_global_loss = self.val_loss
                # Update the best model with the current model
                self.best_model = deepcopy(self.nets[-1])
                # Reduce the learning rate
                self.lr *= self.lr_decay_rate

            else:
                # If the new trained model has increased loss, increment
                # self.patience
                if self.hidden_size > self.n_min_neurons:
                    self.patience += 1
                    # If the patience is greater than the maximum patience,
                    # stop expanding the current layer
                    if self.patience >= self.max_patience:
                        self.expand = False
                        # Restore the best model to the network
                        self.nets[-1] = deepcopy(self.best_model)
                        # Update the number of neurons in the current layer
                        self.hidden_size = self.nets[-1].fc1.out_features
                        break

            # Check if achieved the maximum number of neurons
            if self.hidden_size >= self.n_max_neurons:
                self.expand = False
                break

        # Check if it is to use expanding window
        if self.cross_validation:

            # Use expanding window cross validation to train the Net
            expanding_window = TimeSeriesSplit(n_splits=self.n_hidden_layers-1)

            # Loop to expand the Net layers
            for train, test in expanding_window.split(X_train):

                # Split the given dataset into train and test
                X_train1, y_train1 = X_train[train], y_train[train]
                X_val1, y_val1 = X_train[test], y_train[test]

                # Compute the new inputs for the current hidden layer
                self.current_input_size = self.input_size+self.nets[-1].fc1.out_features+self.output_size
                # Update the hidden size for the new network
                self.hidden_size = 1
                # Increment a new Net with one neuron in the hidden layer
                self.Net = Net(input_size=self.current_input_size, hidden_size=self.hidden_size, output_size=self.output_size)
                # Reset the lr to the original value
                self.lr = self.original_lr
                # Store the models in the list
                self.nets.append(self.Net)
                # Initialize the output and hidden output of the previous layer
                out_train, hid_train = None, None
                out_val, hid_val = None, None

                # Go over all created layers to compute the current inputs
                for i in range(len(self.nets)):

                    # Train
                    if out_train is not None and hid_train is not None:
                        New_X_train = torch.cat((X_train1, out_train, hid_train), dim=1)
                    else:
                        New_X_train = X_train1

                    # Validation
                    if out_val is not None and hid_val is not None:
                        New_X_val = torch.cat((X_val1, out_val, hid_val), dim=1)
                    else:
                        New_X_val = X_val1

                    # Outputs and hidden layers for training
                    with torch.no_grad():
                        out_train, hid_train = self.nets[i](New_X_train, get_hidden=True)

                    # Outputs and hidden layers for validation
                    with torch.no_grad():
                        out_val, hid_val = self.nets[i](New_X_val, get_hidden=True)

                # Train the current structure
                self.nets[-1] = self.train(candidate_model=self.nets[-1], X_train=New_X_train, y_train=y_train1, epochs=self.hidden_size)
                # Evaluate the model's performance
                self.val_loss = self.evaluate(candidate_model=self.nets[-1], X_val=New_X_val, y_val=y_val1)
                # Update the best loss
                self.best_loss = self.val_loss
                # Update global loss if necessary
                if self.val_loss - self.best_global_loss < self.tol:
                    self.best_global_loss = self.val_loss
                # Save the initial Net for current state
                self.best_model = deepcopy(self.nets[-1])

                # Control if it is to expand or not the network
                self.expand = True

                # Increment the current hidden layers until the stop criterion is met
                while self.expand:

                    # Expand the layer
                    self.nets[-1] = self.expand_layer(self.nets[-1])
                    # Train the current model
                    self.nets[-1] = self.train(candidate_model=self.nets[-1], X_train=New_X_train, y_train=y_train1, epochs=self.hidden_size)

                    # The trained model is evaluated on the validation set, and the validation loss is stored.
                    self.val_loss = self.evaluate(candidate_model=self.nets[-1], X_val=New_X_val, y_val=y_val1)
                    # Print loss
                    if self.disp == True:
                        print(f"Layer sizes: {self.hidden_size}, Validation Loss: {self.val_loss:.4f}")

                    # Evaluate the performance of the current model
                    if (self.val_loss - self.best_loss) < self.tol:
                        # If the new model have reduced loss, reset self.patience
                        self.patience = 0
                        # Update the new best loss
                        self.best_loss = self.val_loss
                        # Check if the current loss is the best loss among all steps
                        if self.val_loss - self.best_global_loss < self.tol:
                            self.best_global_loss = self.val_loss
                        # Update the best model with the current model
                        self.best_model = deepcopy(self.nets[-1])
                        # Reduce the learning rate
                        self.lr *= self.lr_decay_rate

                    else:
                        # If the new trained model has increased loss, increment
                        # self.patience
                        if self.hidden_size > self.n_min_neurons:
                            self.patience += 1
                            # If the patience is greater than the maximum patience,
                            # stop expanding the current layer
                            if self.patience >= self.max_patience:
                                self.expand = False
                                # Restore the best model to the network
                                self.nets[-1] = deepcopy(self.best_model)
                                # Update the number of neurons in the current layer
                                self.hidden_size = self.nets[-1].fc1.out_features
                                break

                    # Check if achieved the maximum number of neurons
                    if self.hidden_size >= self.n_max_neurons:
                        self.expand = False
                        break

        else:

            # Run if cross validation is False

            for _ in range(self.n_hidden_layers-1):

                # Combine the inputs for the new layer
                self.current_input_size = self.input_size+self.nets[-1].fc1.out_features+self.output_size
                # Update the hidden size for the new network
                self.hidden_size = 1
                # Initialize a new Net
                self.Net = Net(input_size=self.current_input_size, hidden_size=self.hidden_size, output_size=self.output_size)
                # Reset the lr to the original value
                self.lr = self.original_lr
                # Append the created Net to the list of Nets
                self.nets.append(self.Net)
                # Initialize the output and hidden output of the previous layer
                out_train, hid_train = None, None
                out_val, hid_val = None, None

                for i in range(len(self.nets)):

                    # Prepare train set
                    if out_train is not None and hid_train is not None:
                        New_X_train = torch.cat((X_train, out_train, hid_train), dim=1)
                    else:
                        New_X_train = X_train

                    # Prepare validation set
                    if out_val is not None and hid_val is not None:
                        New_X_val = torch.cat((X_val, out_val, hid_val), dim=1)
                    else:
                        New_X_val = X_val

                    # Perform predictions for train
                    with torch.no_grad():
                        out_train, hid_train = self.nets[i](New_X_train, get_hidden=True)

                    # Perform predictions for validation
                    with torch.no_grad():
                        out_val, hid_val = self.nets[i](New_X_val, get_hidden=True)


                # Train the model
                self.nets[-1] = self.train(candidate_model=self.nets[-1], X_train=New_X_train, y_train=y_train, epochs=self.hidden_size)
                # Evaluate the model
                self.val_loss = self.evaluate(candidate_model=self.nets[-1], X_val=New_X_val, y_val=y_val)
                # Update the best loss of the current layer
                self.best_loss = self.val_loss
                # Update global loss
                if self.val_loss - self.best_global_loss < self.tol:
                    self.best_global_loss = self.val_loss
                # Save the best model
                self.best_model = deepcopy(self.nets[-1])

                # Control if it is to expand or not the network
                self.expand = True

                while self.expand:

                    # Expand the last layer
                    self.nets[-1] = self.expand_layer(self.nets[-1])
                    # The current self.model is trained.
                    self.nets[-1] = self.train(candidate_model=self.nets[-1], X_train=New_X_train, y_train=y_train, epochs=self.hidden_size)

                    # The trained model is evaluated on the validation set, and the validation loss is stored.
                    self.val_loss = self.evaluate(candidate_model=self.nets[-1], X_val=New_X_val, y_val=y_val)
                    # Print loss
                    if self.disp == True:
                        print(f"Layer sizes: {self.hidden_size}, Validation Loss: {self.val_loss:.4f}")

                    # Evaluate the performance of the current model
                    if self.val_loss - self.best_loss < self.tol:
                        # If the new model have reduced loss, reset self.patience
                        self.patience = 0
                        # Update the new best loss
                        self.best_loss = self.val_loss
                        # Check if the current loss is the best loss among all steps
                        if self.val_loss - self.best_global_loss < self.tol:
                            self.best_global_loss = self.val_loss
                        # Update the best model with the current model
                        self.best_model = deepcopy(self.nets[-1])
                        # Reduce the learning rate
                        self.lr *= self.lr_decay_rate

                    else:
                        # If the new trained model has increased loss, increment
                        # self.patience
                        if self.hidden_size > self.n_min_neurons:
                            self.patience += 1
                            # If the patience is greater than the maximum patience,
                            # stop expanding the current layer
                            if self.patience >= self.max_patience:
                                self.expand = False
                                # Restore the best model to the network
                                self.nets[-1] = deepcopy(self.best_model)
                                # Update the number of neurons in the current layer
                                self.hidden_size = self.nets[-1].fc1.out_features
                                break

                    # Check if achieved the maximum number of neurons
                    if self.hidden_size >= self.n_max_neurons:
                        self.expand = False
                        break

    # Training function
    def train(self, candidate_model, X_train, y_train, epochs=1):

        # Initialize the optimizer with learning decay
        self.optimizer = optim.Adam(filter(lambda p: p.requires_grad, candidate_model.parameters()), lr=self.lr)

        # Standard PyTorch training loop
        for epoch in range(epochs):
            # Sets the model to training mode (e.g., enables dropout, batchnorm updates)
            candidate_model.train()
            # Clears old gradients from the last step
            self.optimizer.zero_grad()
            # Forward pass: compute predicted outputs by passing inputs to the model
            output = candidate_model(X_train)
            # Calculate loss
            # self.criterion is the loss function (e.g., MSELoss, CrossEntropyLoss), defined elsewhere in the class
            loss = self.criterion(output, y_train)
            # Backward pass: compute gradient of the loss with respect to model parameters
            loss.backward()
            # Perform a single optimization step (parameter update)
            self.optimizer.step()

        # Return the trained model
        return candidate_model

    # Evaluate the performance of the Net
    def evaluate(self, candidate_model, X_val, y_val):
        # Evaluate validation loss
        candidate_model.eval()
        # torch.no_grad() deactivates autograd engine, reducing memory usage and speeding up computations.
        # It's crucial for evaluation as we don't need to track gradients.
        with torch.no_grad():
            # Get model predictions on validation data
            predictions = candidate_model(X_val)
            # Calculates Mean Squared Error loss directly.
            # This could also use self.criterion if the evaluation metric is the same as the training loss.
            loss = nn.MSELoss()(predictions, y_val)

        # Returns the scalar value of the loss
        return loss.item()

    # Predict function
    def predict(self, X_pred):
            
        # Check if the inputs contain valid numbers
        if (not self.is_numeric_and_finite(X_pred)):
            raise ValueError(
                "X contains incompatible values."
                " Check X for non-numeric or infinity values"
            )
        
        # Apply the conditional conversion
        X_pred = self.to_tensor_if_needed(X_pred)

        # Initialize the output and hidden output of the previous layer
        y_pred, hid_pred = None, None
        # Store all predictions in a list
        predictions = []

        # Run the model through the layers
        for i in range(len(self.nets)):
            # Check if the current layer is not the first one
            if y_pred is not None and hid_pred is not None:
                New_X_pred = torch.cat((X_pred, y_pred, hid_pred), dim=1)
            else:
                New_X_pred = X_pred
            # Perform predictions
            with torch.no_grad():
                y_pred, hid_pred = self.nets[i](New_X_pred, get_hidden=True)

            # Store the predictions
            predictions.append(y_pred)
            
        # Assuming y_pred might be a 2D array (like from a model's .predict output)
        if y_pred.shape[1] == 1:
            y_pred = y_pred.ravel()  # or use y_pred.reshape(-1)
        
        # Ensure it's a NumPy array (in case it was a pandas Series or other type)
        y_pred = np.array(y_pred)

        # Return the predictions
        return y_pred

    # Expand layer
    def expand_layer(self, candidate_model):

        # Increase hidden size
        self.hidden_size += 1
        # Create a new Net with expanded layer
        new_model = Net(self.current_input_size, self.hidden_size, self.output_size)

        # Copy the weights and biases to the new network
        with torch.no_grad():

            # Store the size of previous model
            old_hidden_size = self.hidden_size - 1

            # Copy fc1 weights and biases
            new_model.fc1.weight[:old_hidden_size] = candidate_model.fc1.weight
            new_model.fc1.bias[:old_hidden_size] = candidate_model.fc1.bias

            # Initialize the new neuron (the last one)
            new_model.fc1.weight[old_hidden_size] = torch.randn_like(new_model.fc1.weight[old_hidden_size]) * 0.01
            new_model.fc1.bias[old_hidden_size] = torch.tensor(0.0)

            # Copy fc2 weights and bias
            new_model.fc2.weight[0, :old_hidden_size] = candidate_model.fc2.weight[0]
            new_model.fc2.bias.data.copy_(candidate_model.fc2.bias.data)

            # Initialize the new weight from the new hidden neuron to output
            new_model.fc2.weight[0, old_hidden_size] = torch.randn(1).item() * 0.01

        # Return the expanded model
        return new_model
    
    def is_numeric_and_finite(self, array):
        return np.isfinite(array).all() and np.issubdtype(np.array(array).dtype, np.number)
    
    def to_tensor_if_needed(self, data):
        """
        Converts data to a PyTorch tensor if it is a NumPy array.
        If it's already a tensor, it returns the data unchanged.
        """
        if not torch.is_tensor(data):
            # Assumes data is a NumPy array
            return torch.from_numpy(data).float()
        return data