from soldet.io import load_data, process_data
from soldet.soliton_datasets import SolitonPIEClassDataset, SolitonQEClassDataset, SolitonODDataset, SolitonClassDataset
from soldet.run_classifier import Classifier_Control
from soldet.run_OD import Object_Control, MetzLoss
from soldet.object_model import ObjectDetector
from soldet.classifier_nn import CNN_MLST2021_modern
from soldet.mhat_metric import find_soliton, preprocess_mhat_params, build_metric, apply_metric
from soldet.utilities import config, soldet_to_h5
import datetime
import numpy as np
from tqdm import tqdm
import pickle
from pathlib import Path
import h5py
import requests
import zipfile
from torch.optim import Adam
from torch.nn import NLLLoss, Module
from torch.utils.data import Dataset
from time import sleep
from typing import Callable
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd

class SolitonDetector():
    '''
    The main interface to the usage of the SolDet library.

    On import, or when creating the SolitonDetector object, SolDet will check to confirm if a configuration file, 
    CONFIG.ini, exists in its package path. If not this is created with default values.

    These set up the target directories for the required folder structure to run SolDet. The data_path points to the 
    directory all experimental data folders will reside in. An experiment can be specified with def_exp_name, which will
    set the target directory for where SolDet's class data will be saved to.

    .. code-block::

        data_path
        |- def_exp_name
            |- data
                |- data_files
                    |- class-0
                    |- class-1
                    |- ...
                    |- class-9
                |- data_info
                    |- data_roster.csv
                    |- data_roster.h5
            |- models
        |- ...

    Multiple experiment folders can reside in the data path, and any SolDet detector objects created will reference the 
    current def_exp_name. Changing to a different experiment folder requires creating another SolitonDetector object.

    Additionally, aspects of SolDet can be replaced by replacing the function calls in the initialization process. These
    will override the default behavior of the library to enable usage on data outside the scope of the original SolDet
    dataset. Note: performance can not be guaranteed if overwriting the default behavior of SolDet.

    For more detailed usage please see the provided readme.

    Parameters
    ----------
    process_fn : Callable Function
        The function to be called when processing new data. By default this is the code suited for SolDet's dataset.
        This is called when invoking import_data to add new data to an experimental folder.
        (default = soldet.io.process_data)
    od_model : pytorch Module
        The ML model to use for object detection in SolDet. By default this is suited for identification of 1D 
        excitations in data similar to the Solitons in SolDet's original dataset. For more information see the 
        documentation on Object_Control.
        (default = soldet.object_model.ObjectDetector)
    od_dataset_fn : pytorch Dataset
        The pytorch dataset class to use when handling data for the object detector. By default this is suited for the
        data found in SolDet's dataset. This should meet the requirements for use in a pytorch dataloader. For more
        information see the documentation on Object_Control.
        (default = soldet.soliton_datasets.SolitonODDataset)
    od_loss_fn : pytorch Module
        The loss function to use during training of the object detector. This loss should be able to handle the target
        data and the output of the model. This is further constrained by the requirements of use_model. For more
        information see the documentation on Object_Control.
        (default = soldet.run_OD.MetzLoss)
    cl_model : pytorch Module
        The ML model to use for classification in SolDet. By default this is suited for classification of 1D 
        excitations in data similar to the Solitons in SolDet's original dataset. For more information see the 
        documentation on Classifier_Control.
        (default = soldet.classifier_nn.CNN_MLST2021_modern)
    cl_dataset_fn : pytorch Dataset
        The pytorch dataset class to use when handling data for the classifier. By default this is suited for the
        data found in SolDet's dataset. This should meet the requirements for use in a pytorch dataloader. For more
        information see the documentation on Classifier_Control.
        (default = soldet.soliton_datasets.SolitonClassDataset)
    cl_loss_fn : pytorch Module
        The loss function to use during training of the classifier. This loss should be able to handle the target
        data and the output of the model. This is further constrained by the requirements of use_model. For more
        information see the documentation on Classifier_Control.
        (default = torch.nn.NLLLoss)
    augment : bool or None
        A flag to indicate whether or not to augment the provided data in the dataset function when training ML models.
        If this value is set to True or False it is expected the specified dataset class or function call has an
        augment argument.
        (default = True)
    od_kwargs : dict
        A dictionary containing any extra function arguments needed to be passed to the object detector model
    cl_kwargs : dict
        A dictionary containing any extra function arguments needed to be passed to the classifier model
        (default = {'num_classes': 3})

    Example
    -------
    .. code-block:: python

        soldet.change_exp('soldet_ds')
        soldet.download_ds()
        soldet.soldet_to_h5(soldet.config()[0])
        sd = soldet.SolitonDetector()
        sd.load_data(labels = [0, 1], masked = True)
        sd.train_ML(['classifier'])
        sd.use_models(model_list = ['classifier'], model_paths = ['classifier.pt'])

    '''
    def __init__(self, process_fn: Callable = process_data, od_model: Module = ObjectDetector, 
                 od_dataset_fn: Dataset = SolitonODDataset, od_loss_fn: Module = MetzLoss, 
                 cl_model: Module = CNN_MLST2021_modern, cl_dataset_fn: Dataset = SolitonClassDataset, 
                 cl_loss_fn:  Module = NLLLoss, augment: bool | None = True, od_kwargs: dict = {}, 
                 cl_kwargs: dict = {'num_classes': 3}):
        self.data = []
        self.class_top = Classifier_Control(model = cl_model, dataset_fn = cl_dataset_fn, augment = augment,
                                            **cl_kwargs)
        self.od_top = Object_Control(model = od_model, dataset_fn = od_dataset_fn, augment = augment, **od_kwargs)
        self.exp_path, self.exp_name = config()
        self.process_fn = process_fn
        self.cl_loss_fn = cl_loss_fn()
        self.od_loss_fn = od_loss_fn()
    
    def demo_pipeline(self):
        '''
        Demonstrates some of the basic functionality of SolDet.

        This will create a demo experiment and automatically download the SolDet dataset to run off of if not found
        already. This will also be converted to the new format if needed.
        '''
        print('Running demo of Soldet.')
        data_path = self.exp_path.parent

        if not data_path.joinpath('soldet_demo').is_dir():
            print('Soldet demo directory not found, creating.')
            data_path.joinpath('soldet_demo').mkdir()
        
        data_path = data_path.joinpath('soldet_demo')
        
        if not data_path.joinpath('data').is_dir():
            data_path.joinpath('data').mkdir()
        
        top_dir = ['data_files', 'data_info']
        class_dir = ['class-0','class-1','class-2','class-8','class-9',]

        for dir in top_dir:
            if not data_path.joinpath('data', dir).is_dir():
                data_path.joinpath('data', dir).mkdir(parents=True)
        for dir in class_dir:
            if not data_path.joinpath('data', top_dir[0], dir).is_dir():
                data_path.joinpath('data', top_dir[0], dir).mkdir(parents=True)
        
        roster = data_path.joinpath('data', 'data_info', 'data_roster.npy')

        if not roster.is_file() and not data_path.joinpath('data', 'data_info', 'data_roster.h5').is_file():
            print('Downloading SolDet data. This may take a while. Please wait..')
            
            urls = ["https://data.nist.gov/od/ds/mds2-2363/data_info.zip",
                    "https://data.nist.gov/od/ds/ark:/88434/mds2-2363/data_files.zip"]
            files = ["data_info.zip", 'data_files.zip']
            subdir = data_path.joinpath('data')
            for url, file in zip(urls, files):
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    response.raise_for_status() 
                    raise RuntimeError('{} returned status code {}.'.format(url, response.status_code))
                file_size = int(response.headers.get('Content-Length', 0))
                with subdir.joinpath(file).open("wb") as f:
                    with tqdm.wrapattr(response.raw, 'read', total=file_size, 
                                       desc='Downloading {}.'.format(file)) as raw:
                        chunk = raw.read(1024)
                        if chunk:
                            f.write(chunk)
                        while chunk:
                            chunk = raw.read(1024)
                            if chunk:
                                f.write(chunk)
                print('Extracting data. Please wait..')
                with zipfile.ZipFile(subdir.joinpath(file), 'r') as z:
                    z.extractall(subdir)
                subdir.joinpath(file).unlink()
                sleep(10)  
        
        if not data_path.joinpath('data', 'data_info', 'data_roster.h5').is_file() and roster.is_file():
            print('Converting to modern data format. Now using \'soldet_to_h5()\'.')
            soldet_to_h5(data_path, delete_old=True)
        
        print('Loading in data. Now using \'load_data()\' to load in Class-1.')
        self.data = load_data(self.exp_path.parent.joinpath('soldet_demo'), [1], True, [-1, 3])
        print('Begin use of all models. Now using \'use_models()\'.')
        self.use_models(model_list = ['classifier', 'object detector', 'pie classifier', 'quality estimator'])
        
        print('Demo complete.')
        print('Access ML Classifier labels with key \'soldet_CL\' in data samples.')
        print('Access ML Object Detector positions with key \'soldet_OD\' in data samples.')
        print('Access Physics Informed Classifier types with key \'soldet_PIE\' in data samples.')
        print('Access Physics Informed Quality Estimator values with key \'soldet_QE\' in data samples.')
        self.train = 0.9
        self.test = 0.1

    def load_data(self, labels: list = [0, 1, 2, 8, 9], masked: bool = True, data_frac: float = 0.9, 
                  minmax: list = [-1, 3], scale: bool = True, keep: bool = True):
        '''
        Loads the data corresponding to the given labels in the data roster to the SolitonDetector.

        Parameters
        ----------
        labels : list
            The classes to load. Labels specified here will load all files in the corresponding class folder.
            These labels should match the ones listed in the data.
            (default = [0, 1, 2, 8, 9])
        masked : bool
            Whether to load the masked or unmasked image data.
            (default = True)
        data_frac : float
            The fraction of the data to use for training.
            (default = 0.9)
        scale : boolean
            If True the data will be scaled so it is bounded between 0 and 1.
            (default = True)
        minmax : list
            If scale is set to True the data will be scaled given the minimum and maximum values specified in minmax.
            This expects [MIN, MAX].
            (default = [-1, 3])
        keep : bool
            If True this will keep existing data loaded into the SolitonDetector object, otherwise it will be
            overwritten.
        '''
        if keep:
            self.data += load_data(self.exp_path, labels, masked, minmax = minmax, scale = scale)
        else:
            self.data = load_data(self.exp_path, labels, masked, minmax= minmax, scale = scale)
        self.train = data_frac
        self.test = 1 - data_frac

        if self.test > 1 or self.test < 0:
            raise ValueError('Invalid validation dataset size.')
        if self.train > 1 or self.train < 0:
            raise ValueError('Invalid training dataset size.')

        return
    
    def import_data(self, path: str, **kwargs):
        '''
        Imports new data into the class folders of the current experiment.

        This function will call whatever processing function has been set to preprocess the data and make it suitable
        for use in SolDet. If using a custom processing function to import new data it should return a list of 
        dictionaries, or a dictionary of dictionaries, with at minimum the following keys for each entry:

            - 'label' : The intended class labels
            - 'filename' : Original filename of the unprocessed data
            - 'cloud_data' : Image data cropped to (132, 164)
            - 'masked_data' : Masked image data of cropped image
            - 'class_dir' : The directory a sample of a specific class should reside in.
            - 'positions' : The position of any excitations, if applicable

        Additional metadata keys in the dictionary will be saved. 
        
        The keys 'label', 'original_file', and 'path' will be saved to the roster file. These will also be saved as 
        attributes to the data sample's HDF5 file. The 'masked_data' and 'cloud_data' will be saved as separate data 
        sets in the sample's HDF5 file. Any other keys, including 'positions' will be saved as attributes to the HDF5
        file. If these happen to be a dictionary these will be saved as an empty dataset whose attributes are the 
        dictionary items.

        Parameters
        ----------
        path : string
            The path to the folder containing the new data.
        kwargs : dictionary
            Additional arguments that can be passed to the processing function.

        Example
        -------
        .. code-block:: python

            args = {'target': 'xy', 'atoms_name': 'atoms', 'bg_name': 'background', 'probe_name': 'probe', 'label': 9}
            sd.import_data(path='../BEC_data_2023_0613/0001', **args)
            sd.load_data(labels= [9], masked = True, data_frac = 0.9, minmax = [-1, 3])

        '''

        data = self.process_fn(path, **kwargs)
        
        roster_path = self.exp_path.joinpath('data/data_info')
        if not roster_path.is_dir():
            raise FileNotFoundError('{} is an invalid data_roster path.'.format(roster_path))
        roster_path = roster_path.joinpath('data_roster.h5')
        if roster_path.is_file():
            mode = 'a'
            with h5py.File(roster_path, mode) as h5_file:
                i = len(h5_file.keys())
        else:
            mode = 'w'
            i = 0

        for sample in tqdm(data, desc='Writing data files..'):
            sample_name = self.exp_name + '_{}'.format(i)
            with h5py.File(roster_path, mode) as h5_file:
                ds = h5_file.create_dataset(sample_name, data=h5py.Empty("f"), dtype="f", shape=None)
                ds.attrs['label'] = sample['label']
                ds.attrs['original_file'] = sample['filename']
                ds.attrs['path'] = str(Path(sample['class_dir']).joinpath(sample_name + '.h5'))
                
            data_path = self.exp_path.joinpath('data/data_files/', sample['class_dir'])
            if not data_path.is_dir():
                data_path.mkdir(parents=True)
            
            with h5py.File(data_path.joinpath('{}.h5'.format(sample_name)), 'w') as h5_file:
                
                ds = h5_file.create_dataset('cloud_data', data=sample['cloud_data'], compression="gzip", 
                                            compression_opts=6)
                ds = h5_file.create_dataset('masked_data', data=sample['masked_data'], compression="gzip", 
                                            compression_opts=6)

                for key in sample.keys():
                    if str(key) == 'masked_data' or str(key) == 'cloud_data':
                        pass
                    else:
                        if isinstance(sample[key], dict):
                            ds = h5_file.create_dataset(str(key), data=h5py.Empty("f"), dtype="f", shape=None)
                            for subkey in sample[key].keys():
                                ds.attrs[str(subkey)] = sample[key][subkey]
                        else:
                            h5_file.attrs[str(key)] = sample[key]

            i += 1
            if mode == 'w':
                mode = 'a'
        return
    
    def train_ML(self, model_list: list = ['classifier'], patience: int = 30, epochs: int = 30, 
                 data: list | dict = None):
        '''
        This will train the specified models. The resulting weights of the trained models are saved to the models 
        folder of the current experiment.
        For more control use Object_Control or Classifier_Control directly.

        Parameters
        ----------
        model_list : list
            A list of models to train with the choice of 'object detector' and 'classifier'.
            (default = 'classifier)
        patience : int 
            How many epochs to wait with no improvement before terminating.
            (default = 30)
        epochs : int
            The number of iterations to train and test over all batches in their respective sets. 
            (default = 30)
        data : list or dict
            The target data to train off of. By default this will be the data loaded into the detector object. It is 
            split into a training and testing subset based on the value of the detector's data_frac attribute.
            (default = None) 
        '''

        if data is None:
            target_data = self.data
        else:
            target_data = data

        tr_set, te_set = train_test_split(target_data, test_size=self.test, train_size=self.train)
        if 'classifier' in model_list:
            self.class_top.train_class(train_data = tr_set, test_data = te_set, optimizer_fn = Adam, 
                                       loss_fn = self.cl_loss_fn, model_path=self.exp_path, batch_size = 32, 
                                       patience=patience, epochs=epochs, LR = 1e-4, return_res = False, 
                                       save_weights = True)
                
        if 'object detector' in model_list:        
            self.od_top.train_object(train_data = tr_set, test_data = te_set, optimizer_fn = Adam, 
                                     loss_fn = self.od_loss_fn, model_path=self.exp_path, batch_size = 32, 
                                     patience=patience, epochs=epochs, LR = 1e-4, return_res = False, 
                                     save_weights = True)
            
        return
    
    def use_models(self, model_list: list = ['classifier', 'object detector', 'pie classifier', 'quality estimator'], 
                   model_paths: list = []):
        '''
        Use all models available in SolDet.
        Specifying any of the options 'classifier', 'object detector', 'pie classifier', or 'quality estimator' in the
        argument model_list will make the function use those features. The argument model_paths can be used to dictate
        the trained model files in the models folder of the experiment path. If no paths are provided then the library
        will attempt to use provided model files. Results are saved in the dictionary for each sample.

        Parameters
        ----------
        model_list : list
            The models to run. You can choose from the following:

                - 'classifier': Run the ML classifier model on the object's data. 
                  This will determine which class the image belongs to. For SolDet this is 0 (No solitons),
                  1 (Single Soliton), 2 (Multiple Solitons).
                
                - 'object detector': Run the ML object detector on the object's data. This will determine the location
                  of any excitations found.
                
                - 'pie classifier': Run the physics informed classifier on the object's data. This will further 
                  classify the Solitons found by the ML models into Longitudinal, Canted, Counterclockwise Vortex, 
                  Clockwise Vortex, Top Partial, and Bottom Partial.    
                
                - 'quality estimator': Run the physics informed quality estimator. For a given soliton this will 
                  estimate how much it resembles a longitudinal soliton.

            (default = ['classifier', 'object detector', 'pie classifier', 'quality estimator'])    
        '''
        weights = self.exp_path.joinpath('models')
        soldet_path = Path(__file__).parent
        c_path = soldet_path.joinpath('models', 'classifier.pt')
        o_path = soldet_path.joinpath('models', 'object.pt')
        pie_path = soldet_path.joinpath('models', 'PIE_classifier.pkl')
        qe_path = soldet_path.joinpath('models', 'QE.pkl')

        for f in model_paths:
            if f[-13:]=='classifier.pt':
                c_path = weights.joinpath(f)
                print('Loaded {}.'.format(c_path))  
            if f[-9:]=='object.pt':
                o_path = weights.joinpath(f)
                print('Loaded {}.'.format(o_path))
            if f[-18:] == 'PIE_classifier.pkl':
                pie_path = weights.joinpath(f)
                print('Loaded {}.'.format(pie_path))   
            if f[-6:] == 'QE.pkl':
                qe_path = weights.joinpath(f)
                print('Loaded {}.'.format(qe_path))

        if self.data == {}:
            print('No data loaded.')
        else:
            if 'classifier' in model_list:
                print('Starting ML Classifier.')

                labels = self.class_top.class_predict(self.data, c_path)
                for idx, item in enumerate(self.data):
                    item['soldet_CL'] = labels[idx]

            if 'object detector' in model_list:
                print('Starting ML Object Detector.')
                pos = self.od_top.pos_predict(self.data, o_path)
                for idx, item in enumerate(self.data):
                    item['soldet_OD'] = pos[idx]
            
            if 'pie classifier' in model_list:
                print('Starting Physics Informed Classifier.')
                if not 'PIE_means' in self.__dict__.keys():
                    with open(pie_path, 'rb') as f:
                        file = pickle.load(f)
                        self.PIE_means = file['means']
                        self.PIE_cov = file['cov']
                        self.PIE_pt = file['pt']
                        self.PIE_dim = file['dim']
                        self.par0_cutoff = file['par0_cutoff']
                        self.invpar0_cutoff = file['invpar0_cutoff']
                        self.par4_hardL_cutoff = file['par4_hardL_cutoff']
                        self.par4_hardG_cutoff = file['par4_hardG_cutoff']
                        self.par4_softL_cutoff = file['par4_softL_cutoff']
                        self.par4_softG_cutoff = file['par4_softG_cutoff']
                        self.par1_L_cutoff = file['par1_L_cutoff']
                        self.par1_R_cutoff = file['par1_R_cutoff']
                pbar = tqdm(range(len(self.data)), desc='PIE Classifier running..')
                warned = False
                for idx, item in enumerate(self.data):
                    if 'positions' in item.keys():
                            item['soldet_PIE'] = self.apply_PIE_classifier(item['data'], positions=item['positions'])
                    else:
                        if 'soldet_CL' in item.keys() and 'soldet_OD' in item.keys():
                            if item['soldet_CL'] > 0 and len(item['soldet_OD']) > 0:
                                item['soldet_PIE'] = self.apply_PIE_classifier(item['data'], 
                                                                               positions=item['soldet_OD'])
                            else:
                                pass
                        else:
                            if not warned:
                                tqdm.write('Warning: ML or position labels not found in entry. Did you run the ML \
                                           models on this data or supply position labels?')
                                warned = True
                            else:
                                pass    
                    pbar.update(1)
                pbar.close()

            if 'quality estimator' in model_list:
                print('Starting Physics Informed Quality Estimator.')
                if not 'QE_means' in self.__dict__.keys():
                    with open(qe_path, 'rb') as f:
                        file = pickle.load(f)
                        self.QE_means = file['means']
                        self.QE_cov = file['cov']
                        self.QE_pt = file['pt']
                        self.QE_dim = file['dim']
                pbar = tqdm(range(len(self.data)), desc='Quality Estimate running..')
                warned = False
                for idx, item in enumerate(self.data):
                    if 'positions' in item.keys():
                            item['soldet_QE'] = self.apply_quality_estimate(item['data'], 
                                                                            positions=item['positions']).tolist()
                    else:
                        if 'soldet_CL' in item.keys() and 'soldet_OD' in item.keys():
                            if item['soldet_CL'] > 0 and len(item['soldet_OD']) > 0:
                                item['soldet_QE'] = self.apply_quality_estimate(item['data'], 
                                                                                positions=item['soldet_OD']).tolist()
                            else:
                                pass
                        else:
                            if not warned:
                                tqdm.write('Warning: ML or position labels not found in entry. Did you run the ML \
                                           models on this data or supply position labels?')
                                warned = True
                            else:
                                pass
                    pbar.update(1)
                pbar.close()

    def define_PIE_classifier(self,
                              par0_cutoff: float = np.log(1.57), invpar0_cutoff: float = -np.log(1.57), 
                              par4_hardL_cutoff: float = -0.53, par4_hardG_cutoff: float = 0.75, 
                              par4_softL_cutoff: float = -0.41, par4_softG_cutoff: float = 0.61, 
                              par1_L_cutoff: float = -3.0, par1_R_cutoff: float = 1.14,
                              cutoff_only: bool = False, save: bool = False, func: str = 'modern'):
        '''
        Creates a new metric on the object's data for the physics informed classifier. 
        
        This metric and the specified cut values will be used to categorize the data when applying the classifier.

        Parameters
        ----------
        par0_cutoff : float 
            The "top partial" cutoff value for the ratio of the amplitude fitting parameter from the top and bottom
            image cuts.
            (default = np.log(1.57)) 
        invpar0_cutoff : float
            The "bottom partial" cutoff value for the inverse ratio of the amplitude fitting parameter of the top and 
            bottom image cuts.
            (default = -np.log(1.57)) 
        par4_hardL_cutoff : float
            The "clockwise solitonic vortex" cutoff value for the asymmetric shoulder height fitting parameter
            differences from the top and bottom image cuts.
            (default = -0.53) 
        par4_hardG_cutoff : float 
            The "counter clockwise solitonic vortex" cutoff value for the asymmetric shoulder height fitting parameter
            differences from the top and bottom image cuts.
            (default = 0.75)  
        par4_softL_cutoff : float
            Involved with the 'weaker' categorization cut for the asymmetric shoulder height fitting parameter. This 
            combined with par1_R_cutoff serves as the cut off values for "clockwise solitonic vortex" categorization if
            an earlier cut did not.
            (default = -0.41)
        par4_softG_cutoff : float
            Involved with the 'weaker' categorization cut for the asymmetric shoulder height fitting parameter. This 
            combined with par1_L_cutoff serves as the cut off values for "counter clockwise solitonic vortex" 
            categorization if an earlier cut did not.
            (default = 0.61)
        par1_L_cutoff : float
            Involved with the 'weaker' categorization cut for the center of the excitation fitting parameter. This 
            combined with par4_softL_cutoff serves as the cut off values for "counter clockwise solitonic vortex" 
            categorization if an earlier cut did not.
            (default = -3.0) 
        par1_R_cutoff : float
            Involved with the 'weaker' categorization cut for the center of the excitation fitting parameter. This 
            combined with par4_softL_cutoff serves as the cut off values for "clockwise solitonic vortex" categorization
            if an earlier cut did not.
            (default = 1.14)

        Further information can be found in the SolDet paper https://arxiv.org/abs/2111.04881

        cutoff_only : bool
            If set to true this will not build the metric and only initialize the cuts.
            (default = False) 
        save : bool
            If true this saves the metric and cuts.
            (default = False)
        func : string
            The fitting function to be used. Can be 'gaussian1D', 'original' (SOLDET 1.0), or 'modern' (SOLDET 2.0).
            (default = 'modern')
        '''
        self.par0_cutoff = par0_cutoff
        self.invpar0_cutoff = invpar0_cutoff
        self.par4_hardL_cutoff = par4_hardL_cutoff
        self.par4_hardG_cutoff = par4_hardG_cutoff
        self.par4_softL_cutoff = par4_softL_cutoff
        self.par4_softG_cutoff = par4_softG_cutoff
        self.par1_L_cutoff = par1_L_cutoff
        self.par1_R_cutoff = par1_R_cutoff
        
        if not cutoff_only:
            ds = SolitonPIEClassDataset(self.data)
        
            one_data = []
            one_pos = []
            for idx in range(ds.__len__()):
                one_data.append(ds.__getitem__(idx)[0])
                one_pos.append(ds.__getitem__(idx)[1])

            print('Building PIE metric.')
            one_soliton_params = find_soliton(one_data, positions=one_pos, func=func, return_list=True)
            one_soliton_params = [item for sublist in one_soliton_params for item in sublist]
            PIE_fit_params = preprocess_mhat_params(one_soliton_params)
            
            self.PIE_means, self.PIE_cov, self.PIE_pt = build_metric(PIE_fit_params)
            self.PIE_dim = len(self.PIE_means)

            if save:
                model_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = Path(self.exp_path).joinpath('models', model_datetime+'_PIE_classifier.pkl')
                
                with open(save_path, 'wb') as f:
                    pickle.dump({'means':self.PIE_means, 'cov':self.PIE_cov, 'dim':self.PIE_dim, 'pt':self.PIE_pt, 
                                 'par0_cutoff': self.par0_cutoff, 'invpar0_cutoff': self.invpar0_cutoff, 
                                 'par4_hardL_cutoff': self.par4_hardL_cutoff, 
                                 'par4_hardG_cutoff': self.par4_hardG_cutoff, 
                                 'par4_softL_cutoff': self.par4_softL_cutoff, 
                                 'par4_softG_cutoff': self.par4_softG_cutoff, 
                                 'par1_L_cutoff': self.par1_L_cutoff, 'par1_R_cutoff': self.par1_R_cutoff}, 
                                 f, pickle.HIGHEST_PROTOCOL)
    
    def apply_PIE_classifier(self, img_data: np.ndarray, positions: list | int = None, func: str = 'modern'):
        '''
        Applies a previously built metric and defined cuts to determine the sub class of a solitonic excitation
        identified by the classifier and object detector ML models.

        Images are split into a top half and bottom half. Excitations are located and the metric is applied. From these
        parameters various cuts are done to classify the soliton into the following sub classes:

            - 0: Longitudinal soliton
            - 1: Top partial soliton
            - 2: Bottom partial soliton
            - 3: Clockwise solitonic vortex
            - 4: Counterclockwise solitonic vortex
            - 5: Canted

        These are determined by defining A, the amplitude fitting parameter ratio; db, the shoulder height difference;
        and dic, the center position difference and comparing them to various cuts. These cuts are defined as:
        
            - par0_cutoff: The "top partial" cutoff value for the ratio of the amplitude fitting parameter from the top 
              and bottom image cuts.
            - invpar0_cutoff: The "bottom partial" cutoff value for the inverse ratio of the amplitude fitting 
              parameter of the top and bottom image cuts.
            - par4_hardL_cutoff: The "clockwise solitonic vortex" cutoff value for the asymmetric shoulder height 
              fitting parameter differences from the top and bottom image cuts.
            - par4_hardG_cutoff: The "counter clockwise solitonic vortex" cutoff value for the asymmetric shoulder 
              height fitting parameter differences from the top and bottom image cuts. 
            - par4_softL_cutoff: Involved with the 'weaker' categorization cut for the asymmetric shoulder height 
              fitting parameter. This combined with par1_R_cutoff serves as the cut off values for "clockwise solitonic 
              vortex" categorization if an earlier cut did not.
            - par4_softG_cutoff: Involved with the 'weaker' categorization cut for the asymmetric shoulder height 
              fitting parameter. This combined with par1_L_cutoff serves as the cut off values for "counter clockwise 
              solitonic vortex" categorization if an earlier cut did not.
            - par1_L_cutoff: Involved with the 'weaker' categorization cut for the center of the excitation fitting 
              parameter. This combined with par4_softG_cutoff serves as the cut off values for "counter clockwise 
              solitonic vortex" categorization if an earlier cut did not.
            - par1_R_cutoff: Involved with the 'weaker' categorization cut for the center of the excitation fitting 
              parameter. This combined with par4_softL_cutoff serves as the cut off values for "clockwise solitonic 
              vortex" categorization if an earlier cut did not.

        Further information can be found in the SolDet paper https://arxiv.org/abs/2111.04881

        Parameters
        ----------
        img_data : ndarray
            A numpy array of image data, of shape (H, W) or (N, H, W).
        positions : list or int
            The positions of the solitons for each image in img_data.
            (default = None)
        func : string
            The fitting function to be used. Can be 'gaussian1D', 'original' (SOLDET 1.0), or 'modern' (SOLDET 2.0).
            (default = 'modern')

        Returns
        -------
        class_return : list
            A list of the identified sub classes for all found excitations.
        '''

        bottom_mask=np.zeros_like(img_data)
        bottom_mask[:int(bottom_mask.shape[0]/2),:]=1
        top_mask=np.zeros_like(img_data)
        top_mask[int(top_mask.shape[0]/2):,:]=1

        top_prod = np.multiply(img_data, top_mask)
        bottom_prod = np.multiply(img_data, bottom_mask)
        top_metrics = find_soliton(top_prod, positions=positions, func=func, return_list=True)
        bottom_metrics = find_soliton(bottom_prod, positions=positions, func=func, return_list=True)

        work_list = [top_metrics, bottom_metrics]
        dim = np.squeeze(img_data).shape

        for i, soliton_params in enumerate(work_list):
            if dim == (132, 164):
                if soliton_params == []:
                    pred = []
                    process_params = []
                else:
                    process_params = preprocess_mhat_params(soliton_params, use_minimum_as_center=False)
                    pred = apply_metric(process_params, pt=self.PIE_pt, sigma=self.PIE_cov, mu=self.PIE_means, 
                                        return_dist=True)
            elif dim[1:] == (132, 164):
                pred = []
                process_params = []
                for params_per_image in soliton_params:
                    if params_per_image == []:
                        pred.append([])
                        process_params.append([])
                    else:
                        process_params_per_image = preprocess_mhat_params(params_per_image, use_minimum_as_center=False)
                        pred.append(apply_metric(process_params_per_image, pt=self.PIE_pt, sigma=self.PIE_cov, 
                                                 mu=self.PIE_means, return_dist=True))
                        process_params.append(process_params_per_image)
            
            work_list[i] = [pred, process_params]

        top_metrics = work_list[0]
        bottom_metrics = work_list[1]

        if len(top_metrics[1].shape) > 1 and len(bottom_metrics[1].shape) > 1:
            class_return = []
            for id in range(top_metrics[1].shape[0]):

                diff0=top_metrics[1][id][0] - bottom_metrics[1][id][0]
                diff1=top_metrics[1][id][1] - bottom_metrics[1][id][1] 
                diff4=top_metrics[1][id][4]/top_metrics[1][id][2] - bottom_metrics[1][id][4]/bottom_metrics[1][id][2]
            
                class_return.append(0)
                pathString = "" 
                if diff0 > self.par0_cutoff:
                    pathString += "A"
                    pathString += "1"
                    class_return[-1] = 1
                elif diff0 < self.invpar0_cutoff:
                    pathString += "A"
                    pathString += "2"
                    class_return[-1] = 2
                #passed amplitude check
                else:
                    pathString += "_"
                    #strong assym check
                    if diff4 < self.par4_hardL_cutoff:
                        pathString += "b"
                        pathString += "3"
                        class_return[-1] = 3
                    elif diff4 > self.par4_hardG_cutoff:
                        pathString += "b"
                        pathString += "4"
                        class_return[-1] = 4
                    else:
                        pathString += "_"
                        #pos check
                        if diff1 < self.par1_L_cutoff:
                            #weak assym check
                            pathString += "icL"
                            if diff4 > self.par4_softG_cutoff:
                                pathString += "wb"
                                pathString += "4"
                                class_return[-1] = 4
                            else:
                                pathString += "wbF"
                                pathString += "5"
                                class_return[-1] = 5
                        elif diff1 > self.par1_R_cutoff: 
                            pathString += "icR"
                            #weak assym check
                            if diff4 < self.par4_softL_cutoff:
                                pathString += "wb"
                                pathString += "3"
                                class_return[-1] = 3
                            else:
                                pathString += "wbF"
                                pathString += "5"
                                class_return[-1] = 5
        else:
            diff0=top_metrics[1][0] - bottom_metrics[1][0]
            diff1=top_metrics[1][1] - bottom_metrics[1][1] 
            diff4=top_metrics[1][4]/top_metrics[1][2] - bottom_metrics[1][4]/bottom_metrics[1][2]
        
            class_return = 0
            pathString = "" #mjd: What are they using this for? debugging?
            if diff0 > self.par0_cutoff:
                pathString += "A"
                pathString += "1"
                class_return = 1
            elif diff0 < self.invpar0_cutoff:
                pathString += "A"
                pathString += "2"
                class_return = 2
            #passed amplitude check
            else:
                pathString += "_"
                #strong assym check
                if diff4 < self.par4_hardL_cutoff:
                    pathString += "b"
                    pathString += "3"
                    class_return = 3
                elif diff4 > self.par4_hardG_cutoff:
                    pathString += "b"
                    pathString += "4"
                    class_return = 4
                else:
                    pathString += "_"
                    #pos check
                    if diff1 < self.par1_L_cutoff:
                        #weak assym check
                        pathString += "icL"
                        if diff4 > self.par4_softG_cutoff:
                            pathString += "wb"
                            pathString += "4"
                            class_return = 4
                        else:
                            pathString += "wbF"
                            pathString += "5"
                            class_return = 5
                    elif diff1 > self.par1_R_cutoff: 
                        pathString += "icR"
                        #weak assym check
                        if diff4 < self.par4_softL_cutoff:
                            pathString += "wb"
                            pathString += "3"
                            class_return = 3
                        else:
                            pathString += "wbF"
                            pathString += "5"
                            class_return = 5
        return class_return
    
    def define_quality_estimate(self, save: bool = False, func: str = 'modern'):
        '''
        Creates a new metric on the object's data for the physics informed quality estimator. 
        
        This metric will be used to determine how likely a soliton is a longitudinal soliton when applying the 
        quality estimator. The metric is based on all existing single longitudinal solitons in the current dataset.

        Parameters
        ----------
        save : bool
            If true this saves the metric parameters.
            (default = False) 
        func : string
            The fitting function to be used. Can be 'gaussian1D', 'original' (SOLDET 1.0), or 'modern' (SOLDET 2.0).
            (default = 'modern')
        '''
        ds = SolitonQEClassDataset(self.data)
        
        one_data = []
        one_pos = []
        for idx in range(ds.__len__()):
            one_data.append(ds.__getitem__(idx)[0])
            one_pos.append(ds.__getitem__(idx)[1])

        print('Building QE metric.')
        one_soliton_params = find_soliton(one_data, positions=one_pos, func=func, return_list=True)
        one_soliton_params = [item for sublist in one_soliton_params for item in sublist]
        QE_fit_params = preprocess_mhat_params(one_soliton_params)
        
        self.QE_means, self.QE_cov, self.QE_pt = build_metric(QE_fit_params)
        self.QE_dim = len(self.QE_means)

        if save:
            model_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = Path(self.exp_path).joinpath('models', model_datetime+'_QE.pkl')
            
            with open(save_path, 'wb') as f:
                pickle.dump({'means':self.QE_means, 'cov':self.QE_cov, 'dim':self.QE_dim, 'pt':self.QE_pt}, 
                            f, pickle.HIGHEST_PROTOCOL)

    def apply_quality_estimate(self, data: np.ndarray | list, positions: list | int = None, func: str = 'modern', 
                               return_dist: bool = False):
        '''
        Applies a previously built metric to determine the probability that a soliton identified by the classifier and 
        object detector ML models is longitudinal.

        The score is calculated by taking the metric, transforming the input data, and calculating the mahalanobis
        distance between the metric and the transformed data. The chi squared is applied to this to calculate a score.

        Parameters
        ----------
        data : ndarray or list
            A numpy array or list of image data, of shape (H, W) or (N, H, W).
        positions : list or int
            The positions of the solitons for each image in img_data.
            (default = None)
        func: string
            The fitting function to be used. Can be 'gaussian1D', 'original' (SOLDET 1.0), or 'modern' (SOLDET 2.0).
            (default = 'modern')
        return_dist : bool
            If true this will return the mahalanobis distance instead of the quality score.

        Returns
        -------
        pred : list
            A list of the quality scores for all found excitations.
        '''
        soliton_params = find_soliton(data, positions=positions, func=func, return_list=True)
        dim = np.squeeze(data).shape

        if dim == (132, 164):
            if soliton_params == []:
                pred = []
                process_params = []
            else:
                process_params = preprocess_mhat_params(soliton_params, use_minimum_as_center=False)
                pred = apply_metric(process_params, pt=self.QE_pt, sigma=self.QE_cov, mu=self.QE_means, 
                                    return_dist=return_dist)
        elif dim[1:] == (132, 164):
            pred = []
            process_params = []
            for params_per_image in soliton_params:
                if params_per_image == []:
                    pred.append([])
                    process_params.append([])
                else:
                    process_params_per_image = preprocess_mhat_params(params_per_image, use_minimum_as_center=False)
                    pred.append(apply_metric(process_params_per_image, pt=self.QE_pt, sigma=self.QE_cov, 
                                             mu=self.QE_means, return_dist=return_dist))
                    process_params.append(process_params_per_image)
        
        return pred
    
    def plot_metrics(self, types: list = ['classifier', 'object detector', 'pie classifier', 'quality estimator'], 
                     style: str = None, save: bool = False, data: list | dict = None):
        '''
        Run various plotting routines and display the results. The types of plots shown depend on the entries in the 
        list argument.

        Parameters
        ----------
        types : list
            Choosing a model type here will show appropriate plots for the data you'd typically expect from them.
            (default = ['classifier', 'object detector', 'pie classifier', 'quality estimator'])
        style : str
            An optional argument to specify a matplotlib style file and change the overall look of the plots.
            (default = None)
        save : bool
            An optional argument that will save the output rather than display it. This is useful if running SolDet in
            a terminal.
            (default = False)
        data : list or dict
            The data to generate plots from. By default this is the data loaded into the detector object. If using a 
            different target the function expects a similar structure to that of SolDet.
            (default = None)
        '''

        if style is not None:
            plt.style.use(style)
        if data is None:
            target = self.data
        else:
            target = data

        cl_ground = []
        cl_pred = []
        od_ground = []
        od_pred = []
        qe_ground = []
        qe_pred = []
        pie_ground = []
        pie_pred = []

        for item in target:
            if 'classifier' in types:
                if 'label' in item:
                    cl_ground.append(item['label'])
                    cl_pred.append(item['soldet_CL'])
            if 'object detector' in types:
                if 'positions' in item:
                    for i in range(np.min([len(item['positions']), len(item['soldet_OD'])])):
                        od_ground.append(item['positions'][i])
                        od_pred.append(item['soldet_OD'][i])
            if 'pie classifier' in types:
                if 'excitation_PIE' in item:
                    for i in range(np.min([len(item['excitation_PIE']), len(item['soldet_PIE'])])):
                        pie_ground.append(item['excitation_PIE'][i])
                        pie_pred.append(item['soldet_PIE'][i])
            if 'quality estimator' in types:
                if 'excitation_quality' in item:
                    for i in range(np.min([len(item['excitation_quality']), len(item['soldet_QE'])])):
                        qe_ground.append(item['excitation_quality'][i])
                        qe_pred.append(item['soldet_QE'][i])

        if 'classifier' in types:
            classes = np.unique(cl_ground).tolist()
            gmatrix = np.zeros((len(classes), len(classes)), dtype=int)
            for ground, pred in zip(cl_ground, cl_pred):
                gmatrix[int(ground), int(pred)] += 1
                

            fig, ax = plt.subplots()
            _ = ax.imshow(gmatrix)

            ax.set_xticks(classes)
            ax.set_yticks(classes)

            for i in range(len(classes)):
                for j in range(len(classes)):
                    _ = ax.text(j, i, gmatrix[i, j], ha="center", va="center", color="w")
            
            ax.set_title('Dataset Labels Vs. Classifier Predictions')
            ax.set_xlabel('Classifier Labels')
            ax.set_ylabel('Dataset Labels')
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('cl_truthTable.png'))

        if 'object detector' in types:
            fig, ax = plt.subplots()
            _ = ax.hist(od_ground, bins=20, edgecolor="black", label='Dataset Positions')
            _ = ax.hist(od_pred, bins=20, edgecolor="black", label='Predicted Positions', alpha=0.5)

            ax.set_title('Position Histogram')
            ax.set_ylabel('Counts')
            ax.set_xlabel('Position')
            ax.tick_params(axis='both', which='major')
            ax.legend()
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('od_hist.png'))

            fig, ax = plt.subplots()
            m, b = np.polyfit(od_ground, od_pred, 1)
            x = np.array(od_ground)
            y = m*x + b
            ax.set_title('Position Scatter Plot')
            ax.scatter(od_ground, od_pred, label='(Dataset Position, Predicted Position) Values', alpha=0.5)
            ax.plot(x, y, color='red', label='Fitted Line\nm = {}\nb = {}'.format(m, b))
            ax.set_ylabel('Predicted Position')
            ax.set_xlabel('Dataset Position')
            ax.legend()
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('od_scatter.png'))

        if 'pie classifier' in types:
            classes = np.unique(pie_ground).tolist()
            gmatrix = np.zeros((len(classes), len(classes)), dtype=int)
            for ground, pred in zip(pie_ground, pie_pred):
                gmatrix[int(ground), int(pred)] += 1
                

            fig, ax = plt.subplots()
            _ = ax.imshow(gmatrix)

            ax.set_xticks(classes)
            ax.set_yticks(classes)

            for i in range(len(classes)):
                for j in range(len(classes)):
                    _ = ax.text(j, i, gmatrix[i, j], ha="center", va="center", color="w")
            
            ax.set_title('Dataset PIE Labels Vs. PIE Predictions')
            ax.set_xlabel('PIE Labels')
            ax.set_ylabel('Dataset Labels')
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('pie_truthTable.png'))
        
        if 'quality estimator' in types:
            fig, ax = plt.subplots()
            _ = ax.hist(qe_ground, bins=20, edgecolor="black", label='Dataset Quality Score')
            _ = ax.hist(qe_pred, bins=20, edgecolor="black", label='Predicted Quality Score', alpha=0.5)

            ax.set_title('Quality Estimate Histogram')
            ax.set_ylabel('Counts')
            ax.set_xlabel('Score')
            ax.tick_params(axis='both', which='major')
            ax.legend()
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('qe_hist.png'))

            fig, ax = plt.subplots()
            m, b = np.polyfit(qe_ground, qe_pred, 1)
            x = np.array(qe_ground)
            y = m*x + b
            ax.set_title('Quality Estimate Scatter Plot')
            ax.scatter(qe_ground, qe_pred, label='(Dataset QE, Predicted QE) Values', alpha=0.5)
            ax.plot(x, y, color='red', label='Fitted Line\nm = {}\nb = {}'.format(m, b))
            ax.set_ylabel('Predicted Quality Score')
            ax.set_xlabel('Dataset Quality Score')
            ax.legend()
            plt.tight_layout()

            if save:
                fig.savefig(self.exp_path.joinpath('qe_scatter.png'))

    def export(self, type: str = 'csv', keys: list = None):
        '''
        Export the ground (if available) and predicted (if available) labels in the currently loaded dataset.
        Additional meta information can be saved by providing the relevant keys.

        Parameters
        ----------
        type : str
            Choosing a model type here will show appropriate plots for the data you'd typically expect from them. You 
            can choose from the following options:

                - 'csv': The output will be saved in table form to a csv file.
                - 'hdf': The output will be saved to a HDF format. This will allow the export of additional data types
                  such as dictionaries and arrays. Each sample will be saved to a group with its labels saved as 
                  attributes. Any keys referencing dictionaries will be saved as an empty dataset in the group whose 
                  entries will become attributes to the dataset. Any keys referencing arrays will be saved as datasets 
                  in the group. 
                - 'html': The output will be saved in table form to a html file.
                - 'pkl': The output will be pickled as a pandas dataframe object.
                - 'numpy': The output will be converted to a numpy record array and saved as a npy file. 

            (default = csv)
        keys : list
            Additional keys to pull from each sample's dictionary in the dataset. This could potentially cause errors
            when attempting to export datatypes that are incompatible with the chosen output format.
            (default = None)
        '''

        export = {}
        dir = self.exp_path

        print('Exporting data..')
        for idx, sample in enumerate(self.data):
            export[idx] = {}
            export[idx]['File'] = sample['path']
            if 'label' in sample.keys():
                export[idx]['Class Label'] = sample['label']
            if 'positions' in sample.keys():
                export[idx]['Position'] = sample['positions']
            if 'soldet_CL' in sample.keys():
                export[idx]['CL Prediction'] = sample['soldet_CL']
            if 'soldet_OD' in sample.keys():
                export[idx]['OD Prediction'] = sample['soldet_OD']
            if 'soldet_PIE' in sample.keys():
                export[idx]['PIE Prediction'] = sample['soldet_PIE']
            if 'soldet_QE' in sample.keys():
                export[idx]['CL Prediction'] = sample['soldet_QE']
            
            if keys is not None:
                for key in keys:
                    if key in sample.keys():
                        export[idx][key] = sample[key]

        df = pd.DataFrame.from_dict(export, 'index')
                                                        
        if type == 'csv':
            file_path = dir.joinpath('export_{}.csv'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            df.to_csv(file_path, index=False)
        elif type == 'hdf':
            file_path = dir.joinpath('export_{}.h5'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            with h5py.File(file_path, 'w') as h5_file:
                for idx in export:
                    g = h5_file.create_group(str(idx))
                    for key in export[idx].keys():
                        if isinstance(export[idx][key], dict):
                            ds = g.create_dataset(str(key), data=h5py.Empty("f"), dtype="f", shape=None)
                            for subkey in export[idx][key].keys():
                                ds.attrs[str(subkey)] = export[idx][key][subkey]
                        elif isinstance(export[idx][key], np.ndarray):
                            ds = g.create_dataset(str(key), data=export[idx][key], compression="gzip", 
                                                  compression_opts=6)
                        else:
                            g.attrs[str(key)] = export[idx][key]
        elif type == 'html':
            file_path = dir.joinpath('export_{}.html'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            df.to_html(file_path, index=False)
        elif type == 'pkl':
            file_path = dir.joinpath('export_{}.pkl'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            df.to_pickle(file_path)
        elif type == 'numpy':
            file_path = dir.joinpath('export_{}.npy'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            rec = df.to_records(index=False)
            np.save(file_path, rec)
        else:
            raise ValueError('Invalid value passed to type.')
        
        print('Done!')
        return 