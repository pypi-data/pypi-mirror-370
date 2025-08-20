import numpy as np
import torch
from torchvision.transforms.functional import hflip, vflip

class SolitonPIEClassDataset(torch.utils.data.Dataset):
    '''
    A dataset class for the physics informed classifier.
    This will work through a list, or dictionary, of dictionaries and grab the image data. This image data is
    expected to be at key 'data'.
    It will also grab the positions at key 'positions'.
    
    Parameters
    ----------
    data : list or dict
        The data to build a dataset from.
    '''
    def __init__(self, data: list | dict):
        X = []
        y = []
        for data in data:
            if data['label'] == 1:
                if data['data'].shape[0] == data['data'].shape[1]:
                    raise ValueError("Loaded image data is square. 1D SolDet enforces rectangular data.")
                X.append(data['data'])
                y.append(data['positions'])
        
        self.img_data = X
        self.pos = y

    def __len__(self):
        '''
        Returns the length of the dataset.

        Returns
        -------
        length : int
        '''
        return len(self.img_data)
    
    def __getitem__(self, idx: int):
        '''
        Retrieves a sample at the specified index.

        Parameters
        ----------
        idx : int
            The sample index

        Returns
        -------
        image : ndarray
            The image data at the specified index
        pos : list of floats
            A list of positions at the specified index
        '''
        return self.img_data[idx], self.pos[idx]

class SolitonQEClassDataset(torch.utils.data.Dataset):
    '''
    A dataset class for the physics informed quality estimate.
    This will work through a list, or dictionary, of dictionaries and grab the image data. This image data is
    expected to be at key 'data'.
    It will also grab the positions at key 'positions'.
    
    Parameters
    ----------
    data : list or dict
        The data to build a dataset from.
    '''
    def __init__(self, data: list | dict):
        X = []
        y = []
        for sample in data:
            if 'excitation_PIE' in sample:
                if sample['label'] == 1 and sample['excitation_PIE'] == [0]:
                    if sample['data'].shape[0] == sample['data'].shape[1]:
                        raise ValueError("Loaded image data is square. 1D SolDet enforces rectangular data.")
            
                    X.append(sample['data'])
                    y.append(sample['positions'])
        
        self.img_data = X
        self.pos = y

    def __len__(self):
        '''
        Returns the length of the dataset.

        Returns
        -------
        length : int
        '''
        return len(self.img_data)
    
    def __getitem__(self, idx: int):
        '''
        Retrieves a sample at the specified index.

        Parameters
        ----------
        idx : int
            The sample index

        Returns
        -------
        image : ndarray
            The image data at the specified index
        pos : list of floats
            A list of positions at the specified index
        '''
        return self.img_data[idx], self.pos[idx]
    
class SolitonClassDataset(torch.utils.data.Dataset):
    '''
    A dataset class for the ML based classifier.
    This will work through a list, or dictionary, of dictionaries and grab the image data. This image data is
    expected to be at key 'data'.
    It will also grab the class label at key 'label'.
    
    Parameters
    ----------
    data : list or dict
        The data to build a dataset from.
    augment : bool
        If set to True the data is augmented with rotations.
        (default = True)
    '''
    def __init__(self, data: list, augment: bool = True):
        X = []
        y = []
        for entry in data:
            X.append(entry['data'])
            if entry['data'].shape[0] == entry['data'].shape[1]:
                raise ValueError("Loaded image data is square. 1D SolDet enforces rectangular data.")
            
            if 'label' not in entry:
                raise ValueError('Data must be labeled with class numbers.')
            y.append(entry['label'])
            
        X = np.array(X)
        X = np.reshape(X, (X.shape[0], 1, X.shape[1], X.shape[2]))
        y = np.array(y)
        
        if augment:
            X, y = augment_expand_as_mlst2021(X, y)
        
        self.imgs = torch.from_numpy(X).float()
        self.img_labels = torch.from_numpy(y)            
        
    def __len__(self):
        '''
        Returns the length of the dataset.

        Returns
        -------
        length : int
        '''
        return len(self.imgs)
    
    def __getitem__(self, idx: int):
        '''
        Retrieves a sample at the specified index.

        Parameters
        ----------
        idx : int
            The sample index

        Returns
        -------
        image : ndarray
            The image data at the specified index
        label : int
            The class label at the specified index
        '''
        image = self.imgs[idx]
        label = self.img_labels[idx]
        return image, label
    
class SolitonODDataset(torch.utils.data.Dataset):
    '''
        A dataset class for the ML based object detector.
        This will work through a list, or dictionary, of dictionaries and grab the image data. This image data is
        expected to be at key 'data'.
        It will also grab the positions at key 'positions'.
        
        Parameters
        ----------
        data : list or dict
            The data to build a dataset from.
        augment : bool
            If set to True the data is augmented with rotations.
            (default = True)
        threshold : list
            A list of values that influence the conversion between real positions and cell positions.

                - Threshold[0] is the minimum value to consider a soliton is present.
                - Threshold[1] is the minimum distance two solitons can be considered separate. Any distances under this
                  value is considered the same excitation.
            
            (default = [0.5, 4])
        '''
    def __init__(self, data: list | dict, augment: bool = True, threshold: list = [0.5, 4]):
        
        self.threshold = threshold
        
        X = []
        y = []
        for entry in data:
            if entry['data'].shape[0] == entry['data'].shape[1]:
                raise ValueError("Loaded image data is square. 1D SolDet enforces rectangular data.")
            
            X.append(entry['data'])
            if 'positions' in entry.keys():
                y.append(entry['positions'])
            else:
                y.append([])
            
        X = np.array(X)
        X = np.reshape(X,(X.shape[0], 1, X.shape[1], X.shape[2]))
       
        if augment:
            X, y = augment_w_pos(X, y)
        else:
            X = torch.from_numpy(X).float()
            
        y = pos_41labels_conversion(y, threshold)
            
        self.imgs = X
        self.pos = torch.from_numpy(y).float()
            
    def __len__(self):
        '''
        Returns the length of the dataset.

        Returns
        -------
        length : int
        '''
        return len(self.imgs)
    
    def __getitem__(self, idx: int):
        '''
        Retrieves a sample at the specified index.

        Parameters
        ----------
        idx : int
            The sample index

        Returns
        -------
        image : ndarray
            The image data at the specified index
        pos : list of floats
            A list of positions at the specified index
        '''
        image = self.imgs[idx]
        pos = self.pos[idx]
        return image, pos 

    def labels_to_data(self, sample: np.ndarray):
        '''
        Converts the labels in cell space to positions in pixel space.

        Parameters
        ----------
        sample : ndarray
            An array of probability and fractional position values in cell space.

        Returns
        -------
        labels : list
            The positions in pixel space
            
        '''
        return pos_41labels_conversion(sample, threshold = self.threshold)   

def augment_w_pos(images: np.ndarray, positions: list):
    '''
    Augments the data by rotating the images three ways: horizontal flip, vertical flip, and a 180 degree rotation.

    Parameters
    ----------
    images : ndarray
        The array of image data to be augmented. Typically (N, H, W) where N is the number of images, W is the width
        of the image and H is the height.
    positions : list
        A list of positions for each image in the images array.

    Returns
    -------
    aug_x : ndarray
        The augmented image data
    aug_y : list
        The augmented position data
    '''
    x = torch.from_numpy(images).float()
    aug_x = x
    aug_y = []
    aug_y[:] = positions[:]
    xdim = x.shape[3]
    ydim = x.shape[2]
    
    #hflip
    aug_x = torch.cat((aug_x, hflip(x)), 0)
    for i, pos in enumerate(positions):
        if len(pos)==0:
            aug_y.append([])
        elif len(pos) == 1:
            tmp = [xdim - pos[0]]
            aug_y.append(tmp)
            
    #vflip
    aug_x = torch.cat((aug_x, vflip(x)), 0)
    for pos in positions:
        aug_y.append(pos)
    
    #180
    aug_x = torch.cat((aug_x, vflip(hflip(x))), 0)
    for pos in positions:
        if len(pos)==0:
            aug_y.append([])
        elif len(pos) == 1:
            tmp = [xdim - pos[0]]
            aug_y.append(tmp)
            
    return aug_x, aug_y
    
def expand_data_by_augment(images: np.ndarray, labels: np.ndarray, augments: list):
    '''
    Support function for augment_expand_as_mlst2021.
    This does a simple horizontal, vertical, and 180 degree rotation.

    Parameters
    ----------
    images : ndarray
        The array of image data to be augmented. Typically (N, H, W) where N is the number of images, W is the width
        of the image and H is the height.
    labels : ndarray
        An array of class lebels for each image in the images array.
    augments : list
        A list of augments to apply to the data. Choices are 'hflip' for horizontal flipping, 'vflip' for vertical
        flipping, and '180rot' for a 180 degree rotation.

    Returns
    -------
    aug_x : ndarray
        The augmented image data
    aug_y : ndarray
        The augmented class label data

    '''
    aug_x = [images]
    aug_y = [labels]
    if 'hflip' in augments:
        aug_x.append(images[:,:,::-1])
        aug_y.append(labels)
    
    if 'vflip' in augments:
        aug_x.append(images[:,::-1])
        aug_y.append(labels)

    if '180rot' in augments:
        aug_x.append(np.rot90(images, k=2, axes=(1,2)))
        aug_y.append(labels)

    return np.concatenate(aug_x), np.concatenate(aug_y)

def augment_expand_as_mlst2021(raw_x: np.ndarray, raw_y: np.ndarray, 
                               seed: int | np.typing.ArrayLike | np.random.SeedSequence | np.random.BitGenerator | 
                               np.random.Generator = None):
    '''
    Augments data suitable for classifiers in SolDet.
    This does a simple horizontal, vertical, and 180 degree rotation.

    Parameters
    ----------
    raw_x : ndarray
        The array of image data to be augmented. Typically (N, H, W) where N is the number of images, W is the width
        of the image and H is the height.
    raw_y : ndarray
        An array of class labels for each image in the images array.
    seed : int or array_like[ints] or SeedSequence or BitGenerator or Generator
        The seed to use to initialize the randomization generator
        (default = None)

    Returns
    -------
    augment_x : ndarray
        The augmented image data
    augment_y : ndarray
        The augmented class label data

    '''
    rng = np.random.default_rng(seed=seed)

    zero_aug_x, zero_aug_y = expand_data_by_augment(
        raw_x[(raw_y==0)|(raw_y==2)],raw_y[(raw_y==0)|(raw_y==2)], 
        augments=['hflip','vflip','180rot'])

    # select 1/3 each of one class to apply each transformation to. 
    # if the raw_x/y were shuffled then these will also be shuffled
    idx = rng.permutation([i for i in range(raw_y[raw_y==1].shape[0])])
    one_raw_x = raw_x[raw_y==1][idx]
    one_raw_y = raw_y[raw_y==1][idx]
    one_hflip_x, one_hflip_y = expand_data_by_augment(
        one_raw_x[::3], one_raw_y[::3], augments=['hflip'])
    one_vflip_x, one_vflip_y = expand_data_by_augment(
        one_raw_x[1::3], one_raw_y[1::3], augments=['vflip'])
    one_180_x, one_180_y = expand_data_by_augment(
        one_raw_x[2::3], one_raw_y[2::3], augments=['180rot'])

    augment_x = np.concatenate([zero_aug_x, one_hflip_x, one_vflip_x, one_180_x])
    augment_y = np.concatenate([zero_aug_y, one_hflip_y, one_vflip_y, one_180_y])
    return augment_x, augment_y

def pos_41labels_conversion(label_in: list | np.ndarray, threshold: list = [0.5, 4]):
    '''
    Convert between soliton positions in pixel space and cell space. This new space is a compressed representation of
    the positions in pixel space and the probability of them being present in a cell. The new space is a (2, 1, 41)
    array of values with the first 41 entries representing the probability of an excitation being located in a cell,
    and the second 41 entries representing the fractional position of the excitation in that cell.
    Each cell represents 4 pixels in length, so each cell essentially represents a window of 132 x 4 pixels (H x W).
    
    The behavior of this function depends on the data type of label_in.
    
    Parameters
    ----------
    label_in : list or ndarray
        If the data type is a list then it is assumed that this is a list of positions in pixel space. Valid input can
        be a list of a single value for single image input, or a list of sub lists of positions for multiple images.
        The output will be an array of (2, 1, 41).

        If the data type is an array then it is assumed this input is an array of values in cell space. For each cell
        whose probability is above the threshold will have a position calculated. This position will be based on the
        fractional position in the cell. If multiple excitations exists next to each other and fall below the threshold
        the average positions will be calculated between the two.
    threshold : list
        A list of values that influence the conversion between real positions and cell positions.
        Threshold[0] is the minimum value to consider that an excitation is present.
        Threshold[1] is the minimum distance two excitations can be considered separate. Any distances under this
        value is considered the same excitation.
        (default = [0.5, 4)])
    
    Returns
    -------
    label_out : list or ndarray
        If label_in was a list then the output is an array of (2, 1, 41) values in cell space.
        If label_in was an array then the output is a list of positions in pixel space.

    '''
    label_out = []
    if type(label_in) == list: # if input is soliton positions
        if label_in == []:
            label_out = np.zeros((2,1,41))
        elif type(label_in[0]) in [float, np.float64]: # Postions on Single image 
            label_out = np.zeros((2,1,41))
            for l in label_in:
                if l < 164 and l > 0:
                    label_out[0, 0, int(l // 4)] = 1
                    label_out[1, 0, int(l // 4)] = (l % 4)/4
                else:
                    print('soliton position beyond [0, 164].')
                    
        elif type(label_in[0]) == list: # A list of postions on many images
            label_out = np.zeros((len(label_in),2,1,41))
            for i, pos in enumerate(label_in):
                for l in pos:
                    if l < 164 and l > 0:
                        label_out[i, 0, 0, int(l // 4)] = 1
                        label_out[i, 1, 0, int(l // 4)] = (l % 4)/4
                    else:
                        print('soliton position beyond [0, 164].')
                
    elif type(label_in) == np.ndarray: # if input is 41 labels
        if label_in.shape == (2, 1, 41): # Single 41 label
            for i in range(41):
                if label_in[0, 0, i] > threshold[0]:
                    label_out.append(4 * i + 4 * label_in[1, 0, i])
            if len(label_out)>1:
                i = 0
                while (i+1)<len(label_out):
                    if (label_out[i+1] - label_out[i]) < threshold[1]:
                        label_out[i] = (label_out[i+1] + label_out[i])/2
                        del label_out[i+1]
                    else:
                        i +=1

        elif label_in.shape[1:] == (2, 1, 41):# Array of 41 labels
            for label in label_in:
                l_out = []
                for i in range(41):
                    if label[0, i, 0] > threshold[0]:
                        l_out.append(4 * i + 4 * label[1, 0, i])
                if len(l_out)>1:
                    i = 0
                    while (i+1)<len(l_out):
                        if (l_out[i+1] - l_out[i]) < threshold[1]:
                            l_out[i] = (l_out[i+1] + l_out[i])/2
                            del l_out[i+1]
                        else:
                            i +=1
                label_out.append(l_out)
        else:
            raise ValueError('Invalid input shape.')
    else:
        raise TypeError('Invalid input type for label_in.')
    
    return label_out