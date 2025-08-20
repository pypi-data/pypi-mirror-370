import h5py
from tqdm import tqdm
import numpy as np
from soldet.utilities import combine_data_probe_bg, get_cloud_fit, rotate_crop, apply_mask, config
import glob
import h5py
from tqdm import tqdm
import random
import numpy as np
from pathlib import Path
import requests
import zipfile

def get_raw_data(directory: str, target: str, atoms_name: str, bg_name: str, probe_name: str, 
                 return_files_names: bool = False, return_metadata: bool = False, 
                 meta_list: list = [], shuffle: bool = False):
    '''
    Given a directory of Labscript experimental h5 files, obtains the image data based on the supplied naming schemes.
    
    Parameters
    ----------
    directory : string
        The target directory of h5 files.
    target : string
        The directory name in the h5 file containing the cloud images.
    atoms_name : string
        The full or partial name for images containing the atoms, probe, and background.
    bg_name : string
        The full or partial name for images of only the background, no atoms or probe light.
    probe_name : string
        The full or partial name for images of only the probe light.
    return_files_names : boolean
        If True, appends the list of filenames to the returned list of data.
        (default = False) 
    return_metadata : boolean
        If True, appends the metadata list of the files to the returned list of data.
        (default = False) 
    meta_list : list
        An optional list of metadata attributes to retrieve from the globals folder of a labscript h5 file.
        These are appended to the data list as a separate list if return_metadata is True.
        (default = [])
    shuffle : boolean
        If True, shuffles the order of h5 files found in the supplied directory.
        (default = False)

    Returns
    -------
    res : list
        A list of tuples containing the image data for the three TOF files.
        By default the resulting shape of the return is a list of N entries of 3x164x132 for (atoms, probe, background).
    
        If return_metadata is True an additional sub list of N entries is added containing the specified labscript 
        globals.
        The resulting shape of the return is a list of sublists of N entries, with one containing the meta data.
        
        If return_files_names is True an additional sub list of N entries is added containing the filenames of found 
        entries.
        The resulting shape of the return is a list of sublists of N entries, with one containing the filenames.
    '''
    if type(shuffle) == int:
        if_shuffle = True
        seed = shuffle
    else:
        if shuffle:
            if_shuffle = True
            seed = None
        else:
            if_shuffle = False

    files = glob.glob(directory+"/*.h5")
    if if_shuffle:
        random.Random(seed).shuffle(files)
        
    datasize = len(files)

    raw_data_list = []
    if return_metadata:
        metadata_list = []
        
    for file in tqdm(files[:datasize], desc='Getting Raw Data..'):
        with h5py.File(file, 'r') as h5_file:
            g = h5_file['images/' + target]
            p_path = g.visit(lambda x: x if probe_name in x else None)
            b_path = g.visit(lambda x: x if bg_name in x else None)
            a_path = g.visit(lambda x: x if atoms_name in x else None)
            if (p_path is None) or (b_path is None) or (a_path is None):
                pass
            else:
                probe = g[p_path]
                atoms = g[a_path]
                background = g[b_path]
                img = (atoms, probe, background)
                img = np.float64(img)
                raw_data_list.append(img)
                if return_metadata:
                    sub_list = []
                    for meta in meta_list:
                        if meta in h5_file['globals']:
                            sub_list.append((meta, h5_file['globals'].attrs[meta]))
                        else:
                            pass
                    metadata_list.append(sub_list)

    res = [raw_data_list]
    if return_metadata:
        res.append(metadata_list)
    if return_files_names:
        res.append(files)

    if len(res)==1:
        return res[0]
    else:
        return res

def process_data(path: str, target: str, atoms_name: str, bg_name: str, probe_name: str, label: int = 9, 
                 camera_angle: float = 0, return_metadata: bool = False, 
                 meta_list: list = [], return_files_names: bool = True):
    '''
    Given a directory of labscript experimental h5 files, obtains image data, meta data, and filenames and then
    pre-processes it for use in SolDet.
    From the images a basic OD is calculated and used for a 2D ThomasFermi fit. 
    The cloud is then cropped and masked.
    For each OD image all data is saved as a dictionary.
    
    Parameters
    ----------
    path : string
        The target directory of h5 files.
    target : string
        The directory name in the h5 file containing the cloud images.
    atoms_name : string
        The full or partial name for images containing the atoms, probe, and background.
    bg_name : string
        The full or partial name for images of only the background, no atoms or probe light.
    probe_name : string
        The full or partial name for images of only the probe light.
    label : int
        The class label for the image.
        (default = 9)
    camera_angle : float
        The angle between the camera and the elongated axis of the atom cloud.
    return_files_names: boolean
        If True, appends the list of filenames to the returned list of data.
        (default = True) 
    return_metadata: boolean
        If True, appends the metadata list of the files to the returned list of data.
        (default = False) 
    meta_list : list
        An optional list of metadata attributes to retrieve from the globals folder of a labscript h5 file.
        These are appended to the data list as a separate list if return_metadata is True.
        (default = [])

    Returns
    -------
    data_samples : list
        A list of dictionaries containing the collected pre-processed data.
        Each dictionary contains, at minimum:
        
            - The masked and unmasked image data of shape (132, 164).
            - The class label.
            - The class directory.
            - The 2D TF fit parameters.
            - The rotation angle.
            - The original image size.
            - The original file name.

        Any optional meta data is also saved if return_metadata is True.
    '''
    if not Path(path).is_dir():
        raise FileNotFoundError('Invalid path provided.')
    
    #(atoms, probe, background)
    raw_data = get_raw_data(path, target, atoms_name, bg_name, probe_name, return_metadata = return_metadata, 
                            meta_list = meta_list, return_files_names = return_files_names, shuffle = False)
    
    if return_metadata or return_files_names:
        data_list = raw_data[0]
    else:
        data_list = raw_data

    data_samples = []
    for i in tqdm(range(len(data_list)), desc='Processing Raw Data..'):
        sample = {}
        img = data_list[i]
        if return_metadata and not return_files_names:
            for item in raw_data[1][i]:
                sample[item[0]] = item[1]
        elif return_files_names and not return_metadata:
            for item in raw_data[1][i]:
                sample['filename'] = item
        elif return_metadata and return_files_names:
            for item in raw_data[1][i]:
                sample[item[0]] = item[1]
            for item in raw_data[2][i]:
                sample['filename'] = item
            
        sample['Original Data Size'] = img[0].shape
        naive_OD = combine_data_probe_bg(img)
        full_image_fit = get_cloud_fit(naive_OD, camera_angle, adjust_angle=False)
        sample['rot_angle'] = full_image_fit['theta']
        sample['fitted_parameters'] = full_image_fit
        cloud_data = rotate_crop(naive_OD, full_image_fit)
        sample['cloud_data'] = cloud_data
        sample['masked_data'] = apply_mask(cloud_data, full_image_fit, img[0].shape)
        sample['label'] = label
        sample['class_dir'] = 'class-{}'.format(label)
        data_samples += [sample]
    
    return data_samples

def load_data(path: str, labels: list = [0, 1, 2, 8, 9], masked: bool = True, minmax: list = [None, None], 
              scale: bool = True):
    '''
    This loads data from the class directories listed in the roster file of the currently set experimental folder.
    
    Parameters
    ----------
    path : string
        The path to the experimental folder.
    labels : list
        The classes to load. Labels specified here will load all files in the corresponding class folder.
        (default = [0, 1, 2, 8, 9])
    masked : bool
        Whether to load the masked or unmasked image data.
        (default = True)
    scale : boolean
        If True the data will be scaled so it is bounded between 0 and 1.
        (default = True)
    minmax : list
        If scale is set to True the data will be scaled given the minimum and maximum values specified in minmax.
        This expects [MIN, MAX].
        (default = [None, None])

    Returns
    -------
    data_roster : list
        A list of dictionaries containing the loaded data.
    '''
    if minmax[0] is not None:
        min_val = minmax[0]
    else:
        min_val = np.inf

    if minmax[1] is not None:
        max_val = minmax[1]
    else:
        max_val = -np.inf

    roster_path = Path(path).joinpath('data/data_info')
    data_path = Path(path).joinpath('data/data_files')
    if not roster_path.is_dir():
        raise FileNotFoundError('{} is an invalid data_roster path.'.format(roster_path))
    roster_path = roster_path.joinpath('data_roster.h5')

    data_roster = []
    targets = []
    with h5py.File(roster_path, 'r') as h5_file:
        for sample in h5_file:
            if h5_file[sample].attrs['label'] in labels:
                targets.append(sample)

        for sample in tqdm(targets, desc='Loading processed data..'):
            with h5py.File(data_path.joinpath(h5_file[sample].attrs['path']), 'r') as sample_file:
                data_sample = {}
                attr_keys = list(sample_file.attrs.keys())
                sample_keys = list(sample_file.keys())
                try:
                    if masked:
                        data_sample['data'] = sample_file['masked_data'][()]
                        sample_keys.remove('masked_data') 
                    else:
                        data_sample['data'] = sample_file['cloud_data'][()]
                        sample_keys.remove('cloud_data')
                    
                    if minmax[0] is None:
                        if np.min(data_sample['data']) < min_val:
                            min_val = np.min(data_sample['data'])
                    if minmax[1] is None:
                        if np.max(data_sample['data']) > max_val:
                            max_val = np.max(data_sample['data'])

                    data_sample['label'] = sample_file.attrs['label']
                    attr_keys.remove('label')
                    
                    if 'excitation_position' in sample_file.attrs.keys():
                        data_sample['positions'] = sample_file.attrs['excitation_position'].tolist()
                        attr_keys.remove('excitation_position')
                    elif 'position' in sample_file.attrs.keys():
                        data_sample['positions'] = sample_file.attrs['position'].tolist()
                        attr_keys.remove('position')
                    elif 'positions' in sample_file.attrs.keys():
                        data_sample['positions'] = sample_file.attrs['positions'].tolist()
                        attr_keys.remove('positions')
                    
                    for attr in attr_keys:
                        data_sample[str(attr)] = sample_file.attrs[attr]
                    
                    for attr in sample_keys:
                        if sample_file[attr][()].shape == None:
                            #Dictionary
                            data_sample[str(attr)] = {}
                            for item in sample_file[attr].attrs.keys():
                                data_sample[str(attr)][item] = sample_file[attr].attrs[item]
                        else:
                            #Array
                            data_sample[str(attr)] = sample_file[attr][()]
                    data_sample['path'] = h5_file[sample].attrs['path']
                    
                    data_roster.append(data_sample)
                except Exception as e:
                    tqdm.write('Error. Skipping entry because: ' + str(e))
    
    if minmax[0] is None:
        min_val = np.floor(min_val)
    if minmax[1] is None:
        max_val = np.ceil(max_val)
    
    if scale:
        for sample in tqdm(data_roster, desc='Normalizing Data..'):
            sample['data'] = (sample['data'] - min_val) / (max_val - min_val)
    
    return data_roster

def download_ds():
    '''
    A convenience function that will download the public SolDet data set.
    This will expand the compressed files into the currently set experimental folder. 
    '''
    data_path, _ = config()

    roster_npy_exists = data_path.joinpath('data', 'data_info', 'data_roster.npy').is_file()
    roster_h5_exists = data_path.joinpath('data', 'data_info', 'data_roster.h5').is_file()
    if not roster_npy_exists and not roster_h5_exists:
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
                with tqdm.wrapattr(response.raw, 'read', total=file_size, desc='Downloading {}.'.format(file)) as raw:
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
    else:
        print('Data already exists. Skipping...')