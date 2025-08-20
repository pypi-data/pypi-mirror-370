import numpy as np
from lmfit import Model, Parameters
import scipy.ndimage as snd
import configparser
from pathlib import Path
import h5py
from tqdm import tqdm
from numpy.typing import ArrayLike

def combine_data_probe_bg(raw_data: np.ndarray):
    '''
    A part of preprocessing. Combine 3 raw images (atom, probe, dark) into single atom image.

    Parameters
    ----------
    raw_data : ndarray
        Raw data with shape (3, H, W) [(atoms, probe, background)].

    Returns
    -------
    naive_OD : ndarray
        Optical depth of the image, the pixel values represent atom density.

    '''
    probedark = raw_data[1] - raw_data[2]
    probedark[probedark == 0] = 1e-8
    absorbed_fraction = (raw_data[0] - raw_data[2]) / probedark
    countMax = int(np.nanmax(raw_data[1]))
    darkVar = np.nanvar(raw_data[2])
    ODMAX_meaningful = -np.log(np.sqrt(darkVar + countMax) / countMax)

    absorbed_fraction[absorbed_fraction<=0] = 1e-3
    naive_OD = -np.log(absorbed_fraction)
    naive_OD[naive_OD<-1.0] = -1.0
    naive_OD[naive_OD>(ODMAX_meaningful+1)] = ODMAX_meaningful + 1
    
    return naive_OD

def get_cloud_fit(naive_OD: np.ndarray, angle: float, adjust_angle: bool = False):
    '''
    A part of preprocessing. Fits a 2D ThomasFermi envelope to the given atom cloud image.

    Parameters
    ----------
    naive_OD : ndarray
        Full atom density image.
    angle : int or float.
        The angle between camera and atom cloud elongated direction.
    adjust_angle : boolean.
        Determine whether angle should be fitted.
        (default = False)
    
    Returns
    -------
    cloud_fit : dict
        A dictionary containing the best results of the fit. This dictionary will contain the following parameters:

            - 'amp': Amplitude (peak density) of the 2D cloud.
            - 'cenx': x coordinate of the center position of the cloud.
            - 'ceny': y coordinate of the center position of the cloud.
            - 'rx': The cloud width in x direction.
            - 'ry': The cloud width in y direction.
            - 'offset': The offset value of the fitting.
            - 'theta': Same as the input angle, but in radian.

    '''
    fullimgsize = naive_OD.shape
    ylow = 0
    yhigh = fullimgsize[0]
    xlow = 0
    xhigh = fullimgsize[1]
    
    xROI = np.arange(xlow, xhigh)
    yROI = np.arange(ylow, yhigh)
    x, y = np.meshgrid(xROI, yROI)
    
    x1D_distribution = np.sum(naive_OD, 0)
    y1D_distribution = np.sum(naive_OD, 1)
    
    _, peaksposx = _pickpeak(x1D_distribution, 5)
    _, peaksposy = _pickpeak(y1D_distribution, 5)
    
    ThomasFermi2Drotmodel = Model(ThomasFermi2Drot)
    
    pars = Parameters()
    pars.add('amp', value = 2.0, vary = True)
    pars.add('cenx', value = np.mean(peaksposx) + xlow, vary = True)
    pars.add('ceny', value = np.mean(peaksposy) + ylow, vary = True)
    pars.add('rx', value = 66, vary = True)
    pars.add('ry', value = 56, vary = True)
    pars.add('offset', value = np.min(naive_OD), vary = True)
    pars.add('theta', value = np.radians(angle), vary = adjust_angle)

    fitTF2D = ThomasFermi2Drotmodel.fit(naive_OD.ravel(), params = pars, xy = (x,y))
    cloud_fit = fitTF2D.best_values
    
    return cloud_fit

def _pickpeak(x: ArrayLike, npicks: int = 20):
    '''
    Support function used during fitting. Picks npicks number of peaks from the distribution largest to smallest.

    Parameters
    ----------
    x : ArrayLike
        1D distribution of data.
    npicks : int
        The number of peaks to select from the data.
        (default = 20)
    
    Returns
    -------
    vals : ArrayLike
        The values of the selected peaks.
    idx : ArrayLike
        The indices of the peaks.  
    '''
    #sort array and take index
    idx = np.argsort(-x) # inverse of sort array--take the maximum value first
   
    idx = idx[0:npicks]
    vals = x[idx]
    
    return vals, idx

def ThomasFermi2Drot(xy: tuple, amp: float, cenx: float, ceny: float, rx: float, ry: float, offset: float, 
                     theta: float):
    '''
    ThomasFermi 2D fitting for use in preprocessing SolDet images.
    This function supports get_cloud_fit and does the actual fitting of the 2D Thomas Fermi envelope.

    Parameters
    ----------
    xy: tuple
        The positions from a meshgrid of points.
    amp: float
        Amplitude (peak density) of the 2D cloud.
    cenx: float
        x coordinate of the center position of the cloud.
    ceny: float
        y coordinate of the center position of the cloud.
    rx: float
        The cloud width in x direction.
    ry: float
        The cloud width in y direction.
    offset: float
        The offset value of the fitting.
    theta: float
        Same as the input angle, but in radian.
    
    Returns
    -------
    F(x, y) : ndarray
        The result of the function.
    '''
    
    x, y = xy
    xx = (x - cenx) * np.cos(theta) + (y - ceny) * np.sin(theta)
    yy = (y - ceny) * np.cos(theta) - (x - cenx) * np.sin(theta)
    
    b = 1 - (xx/rx)**2 - (yy/ry)**2
    b = np.maximum(b, 0)
    tf2d = amp*(b**(3/2)) + offset
    return tf2d.ravel()

def rotate_crop(naive_OD: np.ndarray, cloud_fit: dict):
    '''
    A part of preprocessing. Given an image and fit parameters, rotate and crop the image to emphasize the atom cloud.

    Parameters
    ----------
    naive_OD : ndarray
        Image to be processed. Pixel values represent atom density.
    cloud_fit : dict
        TF2D fitting parameters of the cloud. See get_cloud_fit function.

    Returns
    -------
    roi : ndarray
        The cropped and rotated atom cloud image.
    '''
    xdim = naive_OD.shape[1]
    ydim = naive_OD.shape[0]
    x_size = xdim // 2
    y_size = ydim // 2

    center = np.array([cloud_fit['cenx'], cloud_fit['ceny']])
    angle_rad = cloud_fit['theta']
    atoms_rot, pt_rot = rotate_img(naive_OD, center, angle_rad)
    
    if pt_rot[0] + x_size > (atoms_rot.shape[1]-1):
        right_length = (atoms_rot.shape[1]-1) - pt_rot[0]
        left_length = xdim - right_length
    
    elif pt_rot[0] - x_size < 0:
        left_length = pt_rot[0]
        right_length = xdim - left_length
    
    else:
        left_length = x_size
        right_length = x_size

    if pt_rot[1] + y_size > (atoms_rot.shape[0]-1):
        top_length = (atoms_rot.shape[0]-1) - pt_rot[1]
        bottom_length = ydim - top_length
    
    elif pt_rot[1] - y_size < 0:
        bottom_length = pt_rot[1]
        top_length = ydim - bottom_length
    
    else:
        top_length = y_size
        bottom_length = y_size

    xROI_crop = np.arange(pt_rot[0]-left_length, pt_rot[0]+right_length)
    yROI_crop = np.arange(pt_rot[1]-bottom_length, pt_rot[1]+top_length)

    roi = atoms_rot[yROI_crop,:]
    roi = roi[:,xROI_crop]
    
    return roi

def rotate_img(image: np.ndarray, point: int, angle_rad: float):
    '''
    Rotates an image (clockwise) and a selected point within the image by a given angle.

    Parameters
    ----------
    image : ndarray
        Image to be processed.
    point : int
        The point to rotate.
    angle_rad : float
        The angle to rotate through.

    Returns
    -------
    im_rot : ndarray
        The rotated image.
    new_point : int
        The new position of the point.
    '''
    # px, py = point
    im_rot = snd.rotate(image, np.degrees(angle_rad), reshape=True)
    org_center = (np.array(image.shape[:2][::-1])-1)/2
    rot_center = (np.array(im_rot.shape[:2][::-1])-1)/2
    
    R = np.array([[np.cos(angle_rad), np.sin(angle_rad)], 
                  [-np.sin(angle_rad), np.cos(angle_rad)]])
    new_point = R.reshape(2,2)@(point - org_center) + rot_center
    
    return im_rot, new_point.astype(int)

def apply_mask(crop_rotated_data: np.ndarray, cloud_fit: dict, orig_size: tuple):
    '''
    Apply elliptical mask to data to remove background.
    
    Parameters
    ----------
    crop_rotated_data : ndarray
        Atom cloud density image.
    cloud_fit : dict
        TF2D fitting parameters of the cloud. See get_cloud_fit function.
    orig_size: tuple
        The original shape of the image data.

    Returns
    -------
    masked_data : ndarray
        Atom cloud density image with mask.
    '''
    #extract image size
    imgsize = crop_rotated_data.shape
    #extract rotation angle
    angle_rad = cloud_fit['theta']
    
    #extract three points defining the ellipse
    x0, y0 = cloud_fit['cenx'], cloud_fit['ceny']
    xx, yx = point_pos(x0, y0, d=cloud_fit['rx'], angle_rad=angle_rad)
    xy, yy = point_pos(x0, y0, d=cloud_fit['ry'], angle_rad=angle_rad+np.deg2rad(90))

    points = [(x0,y0),(xx,yx),(xy,yy)]
    
    #rotate the ellipse
    rot_array = snd.rotate(np.zeros(orig_size), np.deg2rad(angle_rad), reshape=True)
    rot_pts = rotate_mask(points, angle_rad, orig_size, rot_array.shape)

    #overlay the ellipse on the rotated empty array (array of zeros)
    mask_rot = in_ellipse(rot_array, rot_pts)

    if int(rot_pts[0][1])-int(imgsize[0]/2) < 0:
        bot_idx = 0 
        top_idx = int(rot_pts[0][1])+int(imgsize[0]/2) + np.abs(int(rot_pts[0][1])-int(imgsize[0]/2))
    
    elif int(rot_pts[0][1])+int(imgsize[0]/2) > mask_rot.shape[0]:
        bot_idx = int(rot_pts[0][1])-int(imgsize[0]/2) - ((int(rot_pts[0][1])+int(imgsize[0]/2)) - mask_rot.shape[0])
        top_idx = mask_rot.shape[0]
    
    else:
        bot_idx = int(rot_pts[0][1])-int(imgsize[0]/2)
        top_idx = int(rot_pts[0][1])+int(imgsize[0]/2)
    
    if int(rot_pts[0][0])-int(imgsize[1]/2) < 0:
        left_idx = 0
        right_idx = int(rot_pts[0][0])+int(imgsize[1]/2) + np.abs(int(rot_pts[0][0])-int(imgsize[1]/2))
        
    elif int(rot_pts[0][0])+int(imgsize[1]/2) > mask_rot.shape[1]:
        left_idx = int(rot_pts[0][0])-int(imgsize[1]/2) - ((int(rot_pts[0][0])+int(imgsize[1]/2)) - mask_rot.shape[1])
        right_idx = mask_rot.shape[1]
        
    else:
        left_idx = int(rot_pts[0][0])-int(imgsize[1]/2)
        right_idx = int(rot_pts[0][0])+int(imgsize[1]/2)

    mask_final = mask_rot[bot_idx:top_idx,left_idx:right_idx]
    
    return crop_rotated_data * mask_final

def rotate_mask(points: list, angle_rad: float, mask_shape: tuple, mask_rot_shape: tuple):
    '''
    Rotate (clockwise) a list of points within an image by a given angle.

    Parameters
    ----------
    points: list
        A list of points to rotate.
    angle_rad: float
        The angle to rotate through.
    mask_shape: tuple
        The original shape of the applied mask.
    mask_rot_shape: tuple
        The shape of the rotated data.

    Returns
    -------
    points_rot : ndarray
        Rotated image with mask.
    '''
    org_center = (np.array(mask_shape[:2][::-1])-1)/2
    rot_center = (np.array(mask_rot_shape[:2][::-1])-1)/2

    R = np.array([[np.cos(angle_rad), np.sin(angle_rad)],
                  [-np.sin(angle_rad), np.cos(angle_rad)]])
    points_rot = [(R.reshape(2,2)@(point-org_center)+rot_center).astype(int)
                  for point in points]

    return points_rot

def point_pos(x0: float, y0: float, d: float, angle_rad: float):
    '''
    Find coordinates of a point d distance away from (x0,y0) at an angle.

    Parameters
    ----------
    x0: float
        Reference point in x.
    y0: float
        Reference point in x.
    d: float
        The distance from the points.
    angle_rad: float
        The angle to find the distance from.

    Returns
    -------
    x0 : float
        The new coordinate in x.
    y0 : float
        The new coordinate in y.
    '''

    return int(x0 + d*np.cos(angle_rad)), int(y0 + d*np.sin(angle_rad))

def in_ellipse(arr: np.ndarray, pts: list):
    '''
    Check which point within an array lay inside a defined ellipse.

    Parameters
    ----------
    arr: ndarray
        The array of data to be checked.
    pts: list
        The parameters that define the ellipse in the form [ellipsis_center, vertex, co-vertex].

    Returns
    -------
    arr : ndarray
        A boolean array indicating which points are within the ellipse.
    '''
    rx = pts[1][0]-pts[0][0] 
    ry = pts[2][1]-pts[0][1]
    
    return np.array([(x-pts[0][0])**2/rx**2+(y-pts[0][1])**2/ry**2 <= 1 
                     for y in range(arr.shape[0]) 
                        for x in range(arr.shape[1])]).reshape(arr.shape)

#TODO: Add ability to reset CONFIG file
def config():
    '''
    Sets up the configuration file to be used by the SolDet library if not found, creates the folder structure needed
    for SolDet to function if not found, and returns the current experiment path and name.

    Returns
    -------
    EXP_PATH : Path
        A pathlib object pointing to where the experimental folders for SolDet are located.
    EXP_NAME : str
        The name of the currently set experiment.
    '''
    soldet_path = Path(__file__).parent
    user_path = soldet_path.joinpath('CONFIG.ini')

    if not user_path.is_file():
        print('Warning: No configuration file found. Creating.')
        home_dir = Path.home()
        configfile = configparser.ConfigParser()
        configfile['PATHS'] = {'data_path': str(home_dir.joinpath('soldet')), 'def_exp_name': 'soldet_ds'}
        configfile.write(open(user_path, 'w'))

    try:
        configfile = configparser.ConfigParser()
        configfile.read(user_path)
        DATA_PATH = configfile['PATHS']['data_path']
        EXP_NAME = configfile['PATHS']['def_exp_name']
        EXP_PATH = Path(DATA_PATH)
        EXP_PATH = EXP_PATH.joinpath(EXP_NAME)

        if not EXP_PATH.is_dir():
            print('User path not found, creating.')
            EXP_PATH.mkdir(parents=True)
        
        if not EXP_PATH.joinpath('data').is_dir():
            EXP_PATH.joinpath('data').mkdir(parents=True)
        
        if not EXP_PATH.joinpath('models').is_dir():
            EXP_PATH.joinpath('models').mkdir(parents=True)
        
        top_dir = ['data_files', 'data_info']

        for dir in top_dir:
            if not EXP_PATH.joinpath('data', dir).is_dir():
                EXP_PATH.joinpath('data', dir).mkdir(parents=True)
    except Exception as e:
        raise Exception(str(e)) from None
    
    return EXP_PATH, EXP_NAME

def change_exp(value: str):
    '''
    Changes the current experiment folder in SolDet.

    Parameters
    ----------
    value: str
        The name of the experiment to switch to.
    '''
    soldet_path = Path(__file__).parent
    user_path = soldet_path.joinpath('CONFIG.ini')
    if not user_path.is_file():
        raise FileNotFoundError('No configuration file found.')
    else:
        try:
            configfile = configparser.ConfigParser()
            configfile.read(user_path)
            configfile['PATHS']['def_exp_name'] = value
            with open(user_path, 'w') as file:
                configfile.write(file)
        
        except Exception as e:
            raise Exception(str(e)) from None
        
def change_path(value: str):
    '''
    Changes the path to where the experimental folders for SolDet are kept.

    Parameters
    ----------
    value: str
        The path of the destination folder.
    '''
    soldet_path = Path(__file__).parent
    user_path = soldet_path.joinpath('CONFIG.ini')
    if not user_path.is_file():
        raise FileNotFoundError('No configuration file found.')
    else:
        try:
            configfile = configparser.ConfigParser()
            configfile.read(user_path)
            configfile['PATHS']['data_path'] = value
            with open(user_path, 'w') as file:
                configfile.write(file)
        
        except Exception as e:
            raise Exception(str(e)) from None
        
def soldet_to_h5(path, delete_old = True):
    '''
    Converts the original SolDet dataset into the new h5 version.

    Parameters
    ----------
    path: str
        The path to the destination folder. This should contain the data and data_info folders of SolDet.
    delete_old : bool
        If true this will delete the old files when creating the new ones.
        (default = True)
    '''
    target = Path(path)
    data_roster_dir = target.joinpath('data', 'data_info')
    if not data_roster_dir.is_dir():
        raise FileNotFoundError('{} is an invalid data_roster path.'.format(data_roster_dir))
    
    data_roster = {}
    try:
        roster_O = np.load(data_roster_dir.joinpath('data_roster.npy'), allow_pickle = True).item()
    except:
        if data_roster_dir.joinpath('data_roster.h5').is_file():
            print('Roster file data_roster.npy not found, but data_roster.h5 was found. Did you already convert?')
            return
        else:
            raise FileNotFoundError('Roster file data_roster.npy  not found.')
    data_roster = {**data_roster, **roster_O}
    if delete_old:
        data_roster_dir.joinpath('data_roster.npy').unlink()

    roster_path = data_roster_dir.joinpath('data_roster.h5')
    if roster_path.is_file():
        mode = 'a'
        with h5py.File(roster_path, mode) as h5_file:
            i = len(h5_file.keys())
    else:
        mode = 'w'
        i = 0

    for sample in tqdm(data_roster, desc='Converting data..'):
        sample_name = target.name + '_{}'.format(i)
        data_dir = target.joinpath('data', 'data_files')
        numpy_file = Path(sample).name
        if 'label_v3' in data_roster[sample].keys():
            label = data_roster[sample]['label_v3']
        elif 'label_v2' in data_roster[sample].keys():
            label = data_roster[sample]['label_v2']
        elif 'label_v1' in data_roster[sample].keys():
            label = data_roster[sample]['label_v1']
        class_dir = Path('class-{}'.format(label))
        soldet_h5 = data_dir.joinpath(class_dir, sample_name + '.h5')

        with h5py.File(roster_path, mode, meta_block_size=8000) as h5_file:
            ds = h5_file.create_dataset(sample_name, data=h5py.Empty("f"), dtype="f", shape=None)
            ds.attrs['label'] = label
            ds.attrs['original_file'] = sample
            ds.attrs['path'] = str(class_dir.joinpath(sample_name + '.h5'))
        
        data_loaded = np.load(data_dir.joinpath(class_dir, numpy_file), allow_pickle = True).item()
        if delete_old:
            data_dir.joinpath(class_dir, numpy_file).unlink()
        
        with h5py.File(soldet_h5, 'w') as h5_file:
            h5_file.attrs['label'] = label
            h5_file.attrs['original_file'] = Path(sample).name
            for item in data_roster[sample].keys():
                if 'file_name' in item:
                    pass
                else:
                    h5_file.attrs.create(item, data_roster[sample][item])
            ds = h5_file.create_dataset('cloud_data', data=data_loaded['cloud_data'], compression="gzip", 
                                        compression_opts=6)
            ds = h5_file.create_dataset('masked_data', data=data_loaded['masked_data'], compression="gzip", 
                                        compression_opts=6)

            for key in data_loaded.keys():
                if str(key) == 'masked_data' or str(key) == 'cloud_data':
                    pass
                else:
                    if isinstance(data_loaded[key], dict):
                        ds = h5_file.create_dataset(str(key), data=h5py.Empty("f"), dtype="f", shape=None)
                        for subkey in data_loaded[key].keys():
                            ds.attrs[str(subkey)] = data_loaded[key][subkey]
                    elif isinstance(data_loaded[key], np.ndarray):
                        ds = h5_file.create_dataset(str(key), data=data_loaded[key], compression="gzip", 
                                                    compression_opts=6)
                    else:
                        h5_file.attrs[str(key)] = data_loaded[key]
        i += 1
        if mode == 'w':
            mode = 'a'
    return