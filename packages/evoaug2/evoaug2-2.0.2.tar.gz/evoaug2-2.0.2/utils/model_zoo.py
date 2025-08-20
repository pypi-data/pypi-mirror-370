"""
Model definitions and PyTorch Lightning modules for EvoAug2.

This module provides the DeepSTARR model architecture and PyTorch Lightning
wrappers for training with EvoAug2 augmentations.
"""

import torch
import torch.nn as nn
import pytorch_lightning as pl
import numpy as np


class DeepSTARR(nn.Module):
    """
    DeepSTARR model from de Almeida et al., 2022.
    
    This is the original DeepSTARR model architecture as described in the paper.
    See https://www.nature.com/articles/s41588-022-01048-5 for details.
    
    Parameters
    ----------
    output_dim : int
        Number of output classes for prediction.
    d : int, optional
        Number of first-layer convolutional filters. Defaults to 256.
    conv1_filters : torch.Tensor, optional
        Initial filters for the first convolutional layer. If None, random filters are initialized.
    learn_conv1_filters : bool, optional
        Whether to learn the first convolutional filters. Defaults to True.
    conv2_filters : torch.Tensor, optional
        Initial filters for the second convolutional layer. If None, random filters are initialized.
    learn_conv2_filters : bool, optional
        Whether to learn the second convolutional filters. Defaults to True.
    conv3_filters : torch.Tensor, optional
        Initial filters for the third convolutional layer. If None, random filters are initialized.
    learn_conv3_filters : bool, optional
        Whether to learn the third convolutional filters. Defaults to True.
    conv4_filters : torch.Tensor, optional
        Initial filters for the fourth convolutional layer. If None, random filters are initialized.
    learn_conv4_filters : bool, optional
        Whether to learn the fourth convolutional filters. Defaults to True.
        
    Notes
    -----
    - The original DeepSTARR model uses 256 first-layer convolutional filters
    - Supports transfer learning by initializing with pre-trained filters
    - Uses batch normalization and max pooling throughout
    - Final layers use LazyLinear for automatic input size inference
    """
    
    def __init__(self, output_dim, d=256,
                 conv1_filters=None, learn_conv1_filters=True,
                 conv2_filters=None, learn_conv2_filters=True,
                 conv3_filters=None, learn_conv3_filters=True,
                 conv4_filters=None, learn_conv4_filters=True):
        super().__init__()

        if d != 256:
            print("NB: number of first-layer convolutional filters in original DeepSTARR model is 256; current number of first-layer convolutional filters is not set to 256")

        self.activation = nn.ReLU()
        self.dropout4 = nn.Dropout(0.4)
        self.flatten = nn.Flatten()

        self.init_conv1_filters = conv1_filters
        self.init_conv2_filters = conv2_filters
        self.init_conv3_filters = conv3_filters
        self.init_conv4_filters = conv4_filters

        assert (not (conv1_filters is None and not learn_conv1_filters)), "initial conv1_filters cannot be set to None while learn_conv1_filters is set to False"
        assert (not (conv2_filters is None and not learn_conv2_filters)), "initial conv2_filters cannot be set to None while learn_conv2_filters is set to False"
        assert (not (conv3_filters is None and not learn_conv3_filters)), "initial conv3_filters cannot be set to None while learn_conv3_filters is set to False"
        assert (not (conv4_filters is None and not learn_conv4_filters)), "initial conv4_filters cannot be set to None while learn_conv4_filters is set to False"

        # Layer 1 (convolutional), constituent parts
        if conv1_filters is not None:
            if learn_conv1_filters: # continue modifying existing conv1_filters through learning
                self.conv1_filters = nn.Parameter( torch.Tensor(conv1_filters) )
            else:
                self.register_buffer("conv1_filters", torch.Tensor(conv1_filters))
        else:
            self.conv1_filters = nn.Parameter(torch.zeros(d, 4, 7))
            nn.init.kaiming_normal_(self.conv1_filters)
        self.batchnorm1 = nn.BatchNorm1d(d)
        self.activation1 = nn.ReLU() # name the first-layer activation function for hook purposes
        self.maxpool1 = nn.MaxPool1d(2)

        # Layer 2 (convolutional), constituent parts
        if conv2_filters is not None:
            if learn_conv2_filters: # continue modifying existing conv2_filters through learning
                self.conv2_filters = nn.Parameter( torch.Tensor(conv2_filters) )
            else:
                self.register_buffer("conv2_filters", torch.Tensor(conv2_filters))
        else:
            self.conv2_filters = nn.Parameter(torch.zeros(60, d, 3))
            nn.init.kaiming_normal_(self.conv2_filters)
        self.batchnorm2 = nn.BatchNorm1d(60)
        self.maxpool2 = nn.MaxPool1d(2)

        # Layer 3 (convolutional), constituent parts
        if conv3_filters is not None:
            if learn_conv3_filters: # continue modifying existing conv3_filters through learning
                self.conv3_filters = nn.Parameter( torch.Tensor(conv3_filters) )
            else:
                self.register_buffer("conv3_filters", torch.Tensor(conv3_filters))
        else:
            self.conv3_filters = nn.Parameter(torch.zeros(60, 60, 5))
            nn.init.kaiming_normal_(self.conv3_filters)
        self.batchnorm3 = nn.BatchNorm1d(60)
        self.maxpool3 = nn.MaxPool1d(2)

        # Layer 4 (convolutional), constituent parts
        if conv4_filters is not None:
            if learn_conv4_filters: # continue modifying existing conv4_filters through learning
                self.conv4_filters = nn.Parameter( torch.Tensor(conv4_filters) )
            else:
                self.register_buffer("conv4_filters", torch.Tensor(conv4_filters))
        else:
            self.conv4_filters = nn.Parameter(torch.zeros(120, 60, 3))
            nn.init.kaiming_normal_(self.conv4_filters)
        self.batchnorm4 = nn.BatchNorm1d(120)
        self.maxpool4 = nn.MaxPool1d(2)

        # Layer 5 (fully connected), constituent parts
        self.fc5 = nn.LazyLinear(256, bias=True)
        self.batchnorm5 = nn.BatchNorm1d(256)

        # Layer 6 (fully connected), constituent parts
        self.fc6 = nn.Linear(256, 256, bias=True)
        self.batchnorm6 = nn.BatchNorm1d(256)

        # Output layer (fully connected), constituent parts
        self.fc7 = nn.Linear(256, output_dim)

    def get_which_conv_layers_transferred(self):
        """
        Get list of convolutional layers that were initialized with pre-trained filters.
        
        Returns
        -------
        list
            List of layer indices (1-4) that were initialized with pre-trained filters.
            
        Notes
        -----
        This method is useful for understanding which layers were transferred
        from a pre-trained model during initialization.
        """
        layers = []
        if self.init_conv1_filters is not None:
            layers.append(1)
        if self.init_conv2_filters is not None:
            layers.append(2)
        if self.init_conv3_filters is not None:
            layers.append(3)
        if self.init_conv4_filters is not None:
            layers.append(4)
        return layers

    def forward(self, x):
        """
        Forward pass through the DeepSTARR model.
        
        Parameters
        ----------
        x : torch.Tensor
            Input tensor with shape (batch_size, 4, sequence_length).
            
        Returns
        -------
        torch.Tensor
            Output predictions with shape (batch_size, output_dim).
            
        Notes
        -----
        The forward pass applies:
        1. Four sequential 1D convolutions with batch normalization and max pooling
        2. Flattening of convolutional features
        3. Two fully connected layers with batch normalization and dropout
        4. Final output layer for predictions
        """
        # Layer 1
        cnn = torch.conv1d(x, self.conv1_filters, stride=1, padding="same")
        cnn = self.batchnorm1(cnn)
        cnn = self.activation1(cnn)
        cnn = self.maxpool1(cnn)

        # Layer 2
        cnn = torch.conv1d(cnn, self.conv2_filters, stride=1, padding="same")
        cnn = self.batchnorm2(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool2(cnn)

        # Layer 3
        cnn = torch.conv1d(cnn, self.conv3_filters, stride=1, padding="same")
        cnn = self.batchnorm3(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool3(cnn)

        # Layer 4
        cnn = torch.conv1d(cnn, self.conv4_filters, stride=1, padding="same")
        cnn = self.batchnorm4(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool4(cnn)

        # Layer 5
        cnn = self.flatten(cnn)
        cnn = self.fc5(cnn)
        cnn = self.batchnorm5(cnn)
        cnn = self.activation(cnn)
        cnn = self.dropout4(cnn)

        # Layer 6
        cnn = self.fc6(cnn)
        cnn = self.batchnorm6(cnn)
        cnn = self.activation(cnn)
        cnn = self.dropout4(cnn)

        # Output layer
        y_pred = self.fc7(cnn)

        return y_pred


# Note: We'll use H5DataModule directly and create separate data modules for different purposes


class DeepSTARRModel(pl.LightningModule):
    """
    PyTorch Lightning module for DeepSTARR training.
    
    This class wraps the DeepSTARR model in a PyTorch Lightning module,
    providing training, validation, and testing functionality with
    automatic logging and checkpointing.
    
    Parameters
    ----------
    model : DeepSTARR
        The DeepSTARR model instance.
    learning_rate : float, optional
        Learning rate for training. Defaults to 0.001.
    weight_decay : float, optional
        Weight decay (L2 regularization). Defaults to 1e-6.
        
    Notes
    -----
    - Uses MSE loss for regression tasks
    - Adam optimizer with ReduceLROnPlateau scheduler
    - Automatic logging of training, validation, and test losses
    """
    
    def __init__(self, model, learning_rate=0.001, weight_decay=1e-6):
        super().__init__()
        self.model = model
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.criterion = nn.MSELoss()
        
    def forward(self, x):
        """
        Forward pass through the model.
        
        Parameters
        ----------
        x : torch.Tensor
            Input tensor.
            
        Returns
        -------
        torch.Tensor
            Model predictions.
        """
        return self.model(x)
    
    def training_step(self, batch, batch_idx):
        """
        Training step for a single batch.
        
        Parameters
        ----------
        batch : tuple
            Tuple of (x, y) where x is input and y is target.
        batch_idx : int
            Index of the current batch.
            
        Returns
        -------
        torch.Tensor
            Training loss for the batch.
        """
        x, y = batch
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        self.log('train_loss', loss, prog_bar=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        """
        Validation step for a single batch.
        
        Parameters
        ----------
        batch : tuple
            Tuple of (x, y) where x is input and y is target.
        batch_idx : int
            Index of the current batch.
            
        Returns
        -------
        torch.Tensor
            Validation loss for the batch.
        """
        x, y = batch
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        self.log('val_loss', loss, prog_bar=True)
        return loss
    
    def test_step(self, batch, batch_idx):
        """
        Test step for a single batch.
        
        Parameters
        ----------
        batch : tuple
            Tuple of (x, y) where x is input and y is target.
        batch_idx : int
            Index of the current batch.
            
        Returns
        -------
        torch.Tensor
            Test loss for the batch.
        """
        x, y = batch
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        self.log('test_loss', loss, prog_bar=True)
        return loss
    
    def configure_optimizers(self):
        """
        Configure optimizer and learning rate scheduler.
        
        Returns
        -------
        dict
            Dictionary with optimizer and scheduler configuration.
            
        Notes
        -----
        Uses Adam optimizer with ReduceLROnPlateau scheduler.
        The scheduler monitors validation loss and reduces learning rate
        when no improvement is seen for 5 epochs.
        """
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.1,
            patience=5,
            verbose=True
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss",
            },
        }


class Basset(nn.Module):
    """
    Basset model from Kelley et al., 2016.
    
    This is the Basset model architecture as described in the original paper.
    See https://genome.cshlp.org/content/early/2016/05/03/gr.200535.115.abstract
    and https://github.com/davek44/Basset/blob/master/data/models/pretrained_params.txt
    
    Parameters
    ----------
    output_dim : int
        Number of output classes for prediction.
    d : int, optional
        Number of first-layer convolutional filters. Defaults to 300.
    conv1_filters : torch.Tensor, optional
        Initial filters for the first convolutional layer. If None, random filters are initialized.
    learn_conv1_filters : bool, optional
        Whether to learn the first convolutional filters. Defaults to True.
    conv2_filters : torch.Tensor, optional
        Initial filters for the second convolutional layer. If None, random filters are initialized.
    learn_conv2_filters : bool, optional
        Whether to learn the second convolutional filters. Defaults to True.
    conv3_filters : torch.Tensor, optional
        Initial filters for the third convolutional layer. If None, random filters are initialized.
    learn_conv3_filters : bool, optional
        Whether to learn the third convolutional filters. Defaults to True.
        
    Notes
    -----
    - The original Basset model uses 300 first-layer convolutional filters
    - Supports transfer learning by initializing with pre-trained filters
    - Uses batch normalization and max pooling throughout
    - Final layers use LazyLinear for automatic input size inference
    - Output uses sigmoid activation for binary classification
    """
    
    def __init__(self, output_dim, d=300, 
                 conv1_filters=None, learn_conv1_filters=True,
                 conv2_filters=None, learn_conv2_filters=True,
                 conv3_filters=None, learn_conv3_filters=True):
        super().__init__()
        
        if d != 300:
            print("NB: number of first-layer convolutional filters in original Basset model is 300; current number of first-layer convolutional filters is not set to 300")
        
        self.activation = nn.ReLU()
        self.dropout3 = nn.Dropout(0.3)
        self.flatten = nn.Flatten()
        
        self.init_conv1_filters = conv1_filters
        self.init_conv2_filters = conv2_filters
        self.init_conv3_filters = conv3_filters
        
        assert (not (conv1_filters is None and not learn_conv1_filters)), "initial conv1_filters cannot be set to None while learn_conv1_filters is set to False"
        assert (not (conv2_filters is None and not learn_conv2_filters)), "initial conv2_filters cannot be set to None while learn_conv2_filters is set to False"
        assert (not (conv3_filters is None and not learn_conv3_filters)), "initial conv3_filters cannot be set to None while learn_conv3_filters is set to False"
        
        # Layer 1 (convolutional), constituent parts
        if conv1_filters is not None:
            if learn_conv1_filters: # continue modifying existing conv1_filters through learning
                self.conv1_filters = nn.Parameter( torch.Tensor(conv1_filters) )
            else:
                self.register_buffer("conv1_filters", torch.Tensor(conv1_filters))
        else:
            self.conv1_filters = nn.Parameter(torch.zeros(d, 4, 19))
            nn.init.kaiming_normal_(self.conv1_filters)
        self.batchnorm1 = nn.BatchNorm1d(d)
        self.activation1 = nn.ReLU() # name the first-layer activation function for hook purposes
        self.maxpool1 = nn.MaxPool1d(3)
        
        # Layer 2 (convolutional), constituent parts
        if conv2_filters is not None:
            if learn_conv2_filters: # continue modifying existing conv2_filters through learning
                self.conv2_filters = nn.Parameter( torch.Tensor(conv2_filters) )
            else:
                self.register_buffer("conv2_filters", torch.Tensor(conv2_filters))
        else:
            self.conv2_filters = nn.Parameter(torch.zeros(200, d, 11))
            nn.init.kaiming_normal_(self.conv2_filters)
        self.batchnorm2 = nn.BatchNorm1d(200)
        self.maxpool2 = nn.MaxPool1d(4)
        
        # Layer 3 (convolutional), constituent parts
        if conv3_filters is not None:
            if learn_conv3_filters: # continue modifying existing conv3_filters through learning
                self.conv3_filters = nn.Parameter( torch.Tensor(conv3_filters) )
            else:
                self.register_buffer("conv3_filters", torch.Tensor(conv3_filters))
        else:
            self.conv3_filters = nn.Parameter(torch.zeros(200, 200, 7))
            nn.init.kaiming_normal_(self.conv3_filters)
        self.batchnorm3 = nn.BatchNorm1d(200)
        self.maxpool3 = nn.MaxPool1d(4)
        
        # Layer 4 (fully connected), constituent parts
        self.fc4 = nn.LazyLinear(1000, bias=False)
        self.batchnorm4 = nn.BatchNorm1d(1000)
        
        # Layer 5 (fully connected), constituent parts
        self.fc5 = nn.Linear(1000, 1000, bias=False)
        self.batchnorm5 = nn.BatchNorm1d(1000)
        
        # Output layer (fully connected), constituent parts
        self.fc6 = nn.Linear(1000, output_dim)
        self.sigmoid = nn.Sigmoid()
    
    def get_which_conv_layers_transferred(self):
        """
        Get list of convolutional layers that were initialized with pre-trained filters.
        
        Returns
        -------
        list
            List of layer indices (1-3) that were initialized with pre-trained filters.
            
        Notes
        -----
        This method is useful for understanding which layers were transferred
        from a pre-trained model during initialization.
        """
        layers = []
        if self.init_conv1_filters is not None:
            layers.append(1)
        if self.init_conv2_filters is not None:
            layers.append(2)
        if self.init_conv3_filters is not None:
            layers.append(3)
        return layers
    
    def forward(self, x):
        """
        Forward pass through the Basset model.
        
        Parameters
        ----------
        x : torch.Tensor
            Input tensor with shape (batch_size, 4, sequence_length).
            
        Returns
        -------
        torch.Tensor
            Output predictions with shape (batch_size, output_dim).
            
        Notes
        -----
        The forward pass applies:
        1. Three sequential 1D convolutions with batch normalization and max pooling
        2. Flattening of convolutional features
        3. Two fully connected layers with batch normalization and dropout
        4. Final output layer with sigmoid activation
        """
        # Layer 1
        cnn = torch.conv1d(x, self.conv1_filters, stride=1, padding=(self.conv1_filters.shape[-1]//2))
        cnn = self.batchnorm1(cnn)
        cnn = self.activation1(cnn)
        cnn = self.maxpool1(cnn)
        
        # Layer 2
        cnn = torch.conv1d(cnn, self.conv2_filters, stride=1, padding=(self.conv2_filters.shape[-1]//2))
        cnn = self.batchnorm2(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool2(cnn)
        
        # Layer 3
        cnn = torch.conv1d(cnn, self.conv3_filters, stride=1, padding=(self.conv3_filters.shape[-1]//2))
        cnn = self.batchnorm3(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool3(cnn)
        
        # Layer 4
        cnn = self.flatten(cnn)
        cnn = self.fc4(cnn)
        cnn = self.batchnorm4(cnn)
        cnn = self.activation(cnn)
        cnn = self.dropout3(cnn)
        
        # Layer 5
        cnn = self.fc5(cnn)
        cnn = self.batchnorm5(cnn)
        cnn = self.activation(cnn)
        cnn = self.dropout3(cnn)
        
        # Output layer
        cnn = self.fc6(cnn) 
        y_pred = self.sigmoid(cnn)
        
        return y_pred


class CNN(nn.Module):
    """
    Generic CNN model for genomic sequence classification.
    
    This is a flexible CNN architecture that can be used for various
    genomic sequence classification tasks.
    
    Parameters
    ----------
    output_dim : int
        Number of output classes for prediction.
        
    Notes
    -----
    - Uses three convolutional layers with batch normalization and max pooling
    - Includes dropout for regularization
    - Final layers use LazyLinear for automatic input size inference
    - Output uses sigmoid activation for binary classification
    """
    
    def __init__(self, output_dim):
        super().__init__()
        
        self.activation1 = nn.ReLU()
        self.activation = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)
        self.dropout2 = nn.Dropout(0.2)
        self.dropout3 = nn.Dropout(0.2)
        self.dropout4 = nn.Dropout(0.5)
        self.flatten = nn.Flatten()
        self.output_activation = nn.Sigmoid()

        # Layer 1 (convolutional), constituent parts
        self.conv1_filters = torch.nn.Parameter(torch.zeros(64, 4, 7))
        torch.nn.init.kaiming_uniform_(self.conv1_filters)
        self.batchnorm1 = nn.BatchNorm1d(64)
        self.maxpool1 = nn.MaxPool1d(4)
        
        # Layer 3 (convolutional), constituent parts
        self.conv2_filters = torch.nn.Parameter(torch.zeros(96, 64, 5))
        torch.nn.init.kaiming_uniform_(self.conv2_filters)
        self.batchnorm2 = nn.BatchNorm1d(96)
        self.maxpool2 = nn.MaxPool1d(4)
        
        # Layer 4 (convolutional), constituent parts
        self.conv3_filters = torch.nn.Parameter(torch.zeros(128, 96, 5))
        torch.nn.init.kaiming_uniform_(self.conv3_filters)
        self.batchnorm3 = nn.BatchNorm1d(128)
        self.maxpool3 = nn.MaxPool1d(2)
        
        # Layer 5 (fully connected), constituent parts
        self.fc4 = nn.LazyLinear(256, bias=True)
        self.batchnorm4 = nn.BatchNorm1d(256)
        
        # Output layer (fully connected), constituent parts
        self.fc5 = nn.LazyLinear(output_dim, bias=True)
    
    def forward(self, x):
        """
        Forward pass through the CNN model.
        
        Parameters
        ----------
        x : torch.Tensor
            Input tensor with shape (batch_size, 4, sequence_length).
            
        Returns
        -------
        torch.Tensor
            Output predictions with shape (batch_size, output_dim).
            
        Notes
        -----
        The forward pass applies:
        1. Three sequential 1D convolutions with batch normalization and max pooling
        2. Dropout after each convolutional layer
        3. Flattening of convolutional features
        4. Fully connected layer with batch normalization and dropout
        5. Final output layer with sigmoid activation
        """
        # Layer 1
        cnn = torch.conv1d(x, self.conv1_filters, stride=1, padding="same")
        cnn = self.batchnorm1(cnn)
        cnn = self.activation1(cnn)
        cnn = self.maxpool1(cnn)
        cnn = self.dropout1(cnn)
        
        # Layer 2
        cnn = torch.conv1d(cnn, self.conv2_filters, stride=1, padding="same")
        cnn = self.batchnorm2(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool2(cnn)
        cnn = self.dropout2(cnn)
        
        # Layer 3
        cnn = torch.conv1d(cnn, self.conv3_filters, stride=1, padding="same")
        cnn = self.batchnorm3(cnn)
        cnn = self.activation(cnn)
        cnn = self.maxpool3(cnn)
        cnn = self.dropout3(cnn)
        
        # Layer 4
        cnn = self.flatten(cnn)
        cnn = self.fc4(cnn)
        cnn = self.batchnorm4(cnn)
        cnn = self.activation(cnn)
        cnn = self.dropout4(cnn)
        
        # Output layer
        logits = self.fc5(cnn) 
        y_pred = self.output_activation(logits)
        
        return y_pred