import datetime
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
import soldet.soliton_datasets
from tqdm import tqdm
import warnings

# specify cpu or gpu device for training
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

class MetzLoss(torch.nn.Module):
    '''
    Implementation of the loss function defined in: https://arxiv.org/abs/2111.04881
    The first term is essentially the weighted cross entropy probability for the cell belonging to the 'soliton present'
    class.
    The second term is a mean-squared error for the fractional position within the cell.
    
    Parameters
    ----------
    param : float
        The weight value used when calculating the loss.
        (default = 5.7)
    
    '''
    def __init__(self, param: float = 5.7):
        super(MetzLoss, self).__init__()
        self.param = param
    
    def forward(self, pred, tars):
        eps = 1e-10
        loss = torch.sum(-self.param*tars[:,0,:,:]*torch.log(pred[:,0,:,:] + eps) 
                         - (1-tars[:,0,:,:])*torch.log(1-pred[:,0,:,:]+eps) 
                         + self.param*tars[:,0,:,:]*(tars[:,1,:,:]-pred[:,1,:,:])**2)
        loss = loss / pred.shape[0]
        return loss
    
class Object_Control():
    '''
    The Object Control class for the SolDet package.
    This class runs SolDet code for 1D solitons by default. However, its functionality can be modified with external
    modules by replacing them in the corresponding argument during class initialization.

    Parameters
    ----------
    model : pytorch Module
        The type of model to be used. If using a custom module the output of the model should be in the same shape as
        the target tensors used during training and validation.
    dataset_fn : pytorch Dataset
        The dataset function used to provide data to the models. If using a custom function this should accept the
        shape and type of data you are providing to the framework. It should have an argument named augment
        to indicate whether or not to augment the data if augment is not set to None.
    augment : bool or None
        A flag to indicate whether or not to augment the provided data in the dataset function.
        (default = True)
    device : int
        Which device to use. An integer provided here will specify which GPU to run the model on. If none is provided
        then either GPU 0 will be selected, or the CPU will be used if no CUDA compatible device is detected.
        This also influences the output of the GUI. Worker progress will be printed to the terminal on lines that
        correspond to the device. For GPU 0 updates will be printed to position 0, for GPU 1 updates will be printed to
        position 1, and so on.
        (default = None)
    kwargs : dict
        A dictionary of arguments to pass to the specified model.

    Example
    -------
    .. code-block:: python
    
        kwargs = {'label_shape' : (1, 41)}

        od_top = Object_Control(model = soldet.object_model.ObjectDetector, 
                                dataset_fn = soldet.soliton_datasets.SolitonODDataset,
                                augment = True, device = 0, **kwargs)

    '''
    def __init__(self, model: torch.nn.Module, 
                 dataset_fn: torch.utils.data.Dataset = soldet.soliton_datasets.SolitonODDataset, 
                 augment: bool | None = True, device: int = None, **kwargs):
        self.dataset_fn = dataset_fn
        self.augment = augment
        self.rank = device if device is not None else 0
        self.device = 'cuda:{}'.format(device) if device is not None else DEVICE
        self.model = model(**kwargs).float().to(self.device)

    def train_object(self, train_data: list, test_data: list, optimizer_fn: torch.optim.Optimizer, 
                     loss_fn: torch.nn.Module, model_path: str = None, batch_size = 32, patience: int = 30, 
                     epochs: int = 30, LR = 1e-4, return_res = False, save_weights = False):
        '''
        Training the object's OD model on the given data.

        It should be noted that regardless of the dataset functionality provided, the resulting output of the OD 
        model and its targets are expected to follow the convention that for dim 1, array entry 0 is the likelihood 
        for the object to be present, and array entries > 0 are everything else.

        Parameters
        ----------
        train_data : list
            The data to train the model off of. By default this expects a list of dictionaries containing the N samples.
            If a custom dataset has been specified, this data should be of the expected type and shape for that pytorch
            dataset function.
        test_data : list
            The data to test the model with. By default this expects a list of dictionaries containing the N samples.
            If a custom dataset has been specified, this data should be of the expected type and shape for that pytorch
            dataset function.
        optimizer_fn : pytorch Optimizer
            The optimizing function to use during training.
        loss_fn : pytorch loss Module
            The loss function to use during training.
        model_path : str
            The path to where weights should be saved to if save_weights = True.
            (default = None)
        save_weights : bool
            Whether to save the best weights or not.
            (default = False) 
        batch_size : int
            The batch size to use during training.
            (default = 32)
        patience : int 
            How many epochs to wait with no improvement before terminating.
            (default = 30)
        epochs : int
            The number of iterations to train and test over all batches in their respective sets. 
            (default = 30) 
        LR : float 
            The learning rate to use in the optimizer.
            (default = 1e-4)
        return_res : bool
            Whether to return the best loss and accuracy metrics.
            (default = False)

        Returns
        -------
        min_loss : float
            The minimum test loss found during training if return_res = True.
        accu : float
            The corresponding test accuracy if return_res = True. Here 'accuracy' is how many correct predictions 
            there were.
        '''
        if self.augment is not None:
            train_ds = self.dataset_fn(train_data, augment = self.augment)
            test_ds = self.dataset_fn(test_data, augment = self.augment)
        else:
            train_ds = self.dataset_fn(train_data)
            test_ds = self.dataset_fn(test_data)
        
        print('Training with {} samples and validating with {} samples.'.format(train_ds.__len__(), test_ds.__len__()))
        train_dataloader = DataLoader(train_ds, shuffle=True, batch_size = batch_size)
        test_dataloader = DataLoader(test_ds, shuffle=True, batch_size = batch_size)  
        
        model_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if save_weights:
            save_path = Path(model_path).joinpath('models', model_datetime+'_object.pt')

        optimizer = optimizer_fn(self.model.parameters(), lr = LR)
    
        patience_count = 0
        pbar = tqdm(range(epochs), 
                    desc='Device: {} | Epoch: 0/{} | Loss: #.###### | \
                          Avg. Test Loss: #.####### | Acc.: #.#######'.format(self.device, epochs), 
                    position=self.rank)
        for t in pbar:
            with warnings.catch_warnings(record=True) as w:
                ### TRAINING
                running_loss = torch.tensor(0, device=self.device, dtype=torch.float32) 
                self.model.train()
                
                for _, (data, target) in enumerate(train_dataloader):
                    data, target = data.to(self.device), target.to(self.device)
                    
                    #compute error
                    pred = self.model(data)
                    loss = loss_fn(pred, target)
                    
                    #backpropagation
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    running_loss += loss.detach()

                train_metrics = {'loss': running_loss / len(train_dataloader)}
                
                ### VALIDATION
                num_batches = len(test_dataloader)
                self.model.eval()
                test_loss = torch.tensor(0, device=self.device, dtype=torch.float32)
                correct = 0
                with torch.no_grad():
                    for _, (data, target) in enumerate(test_dataloader):
                        data, target = data.to(self.device), target.to(self.device)
                        output = self.model(data)
                        batch_correct = 0
                        for idx, prediction in enumerate(output):
                            if (target[idx, 0] > 0.5).any():
                                num_exc = (target[idx, 0] == torch.max(target[idx, 0])).nonzero().shape[0]
                                t_loc = target[idx, 0].flatten() > 0.5
                                p_loc = prediction[0].flatten() > 0.5
                                batch_correct += (torch.logical_and(t_loc, p_loc).nonzero().shape[0] / num_exc)
                            else:
                                if (prediction[0] < 0.5).all():
                                    batch_correct += 1
                        
                        test_loss += loss_fn(output, target).detach()      
                        correct += batch_correct / output.shape[0]

                test_loss /= num_batches
                correct /= num_batches
                
                test_metrics = {'loss': test_loss, 'accuracy': correct} 

                if len(w) > 0:
                    tqdm.write('Warning: ' + str(w[-1].message))
            
            checkpoint_dict = {
                'epoch': t, 
                'train_metrics': train_metrics, 'test_metrics':test_metrics,
                'model_state_dict': self.model.state_dict()}
            
            if t == 0:
                min_loss = test_metrics['loss']
                accu = test_metrics['accuracy']
                if save_weights:
                    torch.save(checkpoint_dict, save_path)
            
            elif test_metrics['loss'] < min_loss:
                patience_count = 0
                min_loss = test_metrics['loss']
                accu = test_metrics['accuracy']
                if save_weights:
                    torch.save(checkpoint_dict, save_path)
            
            else:
                patience_count += 1
            
            pbar.set_description('Device: {} | Epoch: {}/{} | Loss: {:>7f} | \
                                 Avg. Test Loss: {:>8f} | Acc.: {:>8f}'.format(self.device, t+1, epochs, 
                                                                               train_metrics['loss'], 
                                                                               test_metrics['loss'], 
                                                                               test_metrics['accuracy']))
        
            if patience_count > patience: 
                break
        tqdm.write("Done! Minimum Test Loss: {} with Accuracy: {}.\n".format(min_loss, accu))
        
        if return_res:
            return min_loss.detach().cpu().item(), accu
            
    def pos_predict(self, data: list | dict | np.ndarray, model_path: str, ):
        '''
        For the given data make predictions using the object's model.

        Parameters
        ----------
        data : list or dict or ndarray
            The data to make predictions on.
        model_path : str
            The path to the saved weights for the model.
        
        Returns
        -------
        pos : list
            A list of all positions found for each provided image.
        '''
        if type(data) is dict:
            if self.augment is not None:
                ds = self.dataset_fn([data], augment = False)
            else:
                ds = self.dataset_fn([data])
        elif type(data) is list:
            if self.augment is not None:
                ds = self.dataset_fn(data, augment = False)
            else:
                ds = self.dataset_fn(data)
        elif type(data) is np.ndarray:
            data_list = []
            if len(data.shape) == 3:
                for i in range(data.shape[0]):
                    data_list.append({'data': data[i, :, :]})
            elif len(data.shape) == 2:
                data_list.append({'data': data})
            else:
                raise ValueError('Input data incorrect shape. Expected 3D or 2D image data.')
            
            if self.augment is not None:
                ds = self.dataset_fn(data_list, augment = False)
            else:
                ds = self.dataset_fn(data_list)
        else:
            raise TypeError('Input data is invalid type. Epected list, dictionary, or numpy.ndarray')

        with warnings.catch_warnings(record=True) as w:
            target = []
            for idx in range(ds.__len__()):
                img, _ = ds.__getitem__(idx)
                img = img.to(self.device)
                target.append(img)
            
            checkpoint_dict = torch.load(model_path, map_location = torch.device(self.device), weights_only=True)
            self.model.load_state_dict(checkpoint_dict['model_state_dict'])
            self.model.eval()
            print('Object Detector model loaded.')
            pos = []
            with torch.no_grad():
                print('Running model, please wait..')
                pbar = tqdm(range(len(target)), desc='Running..')
                for sample in target:
                    pred = self.model(sample.unsqueeze(0)).detach().cpu().numpy()
                    pos.append(ds.labels_to_data(pred[0]))
                    if len(w) > 0:
                        tqdm.write(str(w[0].message))
                        del w[0]
                    pbar.update(1)
                pbar.close()
        print('Finished.')
        return pos 

    def pos_counter(self, data: dict | np.ndarray, model_path: str):
        '''
        For the given data count the number of objects.

        Parameters
        ----------
        data : list or dict or ndarray
            The data to make predictions on.
        model_path : str
            The path to the saved weights for the model.
        
        Returns
        -------
        count_list : list
            A list of counts for each provided image.
        '''
        res = self.pos_predict(data, model_path)

        count_list = []

        for item in res:
            count_list.append(len(item))
        
        return count_list