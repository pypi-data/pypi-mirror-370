import torch
from torch import nn
import torch.nn.functional as F
device = 'cuda' if torch.cuda.is_available() else 'cpu'

class CNN_MLST2021_modern(nn.Module):
    """ Modern SolDet classifier
        This pytorch classifier model identifies the class a solitonic image belongs to.

        Parameters
        ----------
        num_classes : int
            The number of classes to identify. By default this value is three classes, which represents the presence of
            no excitations (0), a single excitation (1), or multiple excitations (2).
            (default = 3)
    """
    def __init__(self, num_classes: int = 3):
        super().__init__()

        filter_list = [8, 16, 32, 64, 128]
        self.stack_size = 3
        kernel_size = 8
        in_channels = 1
        block_in_channels=1

        self.dpth_conv_l=nn.ModuleList()
        self.pt_conv_l=nn.ModuleList()
        self.batch_norm_l=nn.ModuleList()
        self.res_conv_l=nn.ModuleList()
        for i,f in enumerate(filter_list):
            self.dpth_conv_l.append(nn.ModuleList())
            self.pt_conv_l.append(nn.ModuleList())
            self.batch_norm_l.append(nn.ModuleList())

            for j in range(self.stack_size):
                self.dpth_conv_l[i].append(
                    nn.Conv2d(
                        block_in_channels, f, kernel_size, padding='same',
                        groups=block_in_channels))
                self.pt_conv_l[i].append(nn.Conv2d(f, f, 1))
                self.batch_norm_l[i].append(nn.BatchNorm2d(f))
                
                if j==self.stack_size-1:
                    self.res_conv_l.append(nn.Conv2d(in_channels, f, 1))

                block_in_channels=f
            in_channels=f
    
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc1 = nn.Linear(128, num_classes)
        
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    def forward(self, x: torch.Tensor):
        """ 
        Take a tensor and make a class prediction.

        Parameters
        ----------
        x : tensor of shape (B, 1, H, W)
            The input tensor to make a prediction on. The expected shape is of shape (B, 1, H, W), where B is the batch
            size, H is the image height, and W is the image width.

        Returns
        -------
        x : tensor of shape (B, 3)
            The output tensor containing the probabilities for each class. The output is of shape (B, 3) where B is the
            batch size and the last dimension contains the probabilities for the number of classes specified in the 
            model initialization.
    """
        # Max pooling over 2,2, dropout with prob 50 %
        for i in range(len(self.dpth_conv_l)):
            res = x
            for j in range(self.stack_size):
                x = F.dropout(F.relu(self.pt_conv_l[i][j](self.dpth_conv_l[i][j](x))), 0.4)
                x = self.batch_norm_l[i][j](x)
                if j==self.stack_size-1:
                    x = F.max_pool2d(x, 2)

                    x += self.res_conv_l[i](F.max_pool2d(res, 2))
        
        x = self.adaptive_pool(x)
        x = torch.flatten(x, 1)
        # x = nn.LogSoftmax(dim=1)(self.fc1(x))
        x = nn.LogSoftmax(dim=1)(self.fc1(x))
        
        return x
    
class CNN_MLST2021(nn.Module):
    def __init__(self):
        super(CNN_MLST2021, self).__init__()

        # first arg.: input channels, second: out channels, third: kernel size
        self.conv1 = nn.Conv2d(1, 8, (5,5), padding='same')
        self.conv2 = nn.Conv2d(8, 16, (5,5), padding='same')
        self.conv3 = nn.Conv2d(16, 32, (5,5), padding='same')
        self.conv4 = nn.Conv2d(32, 64, (5,5), padding='same')
        self.conv5 = nn.Conv2d(64, 128, (5,5), padding='same')

        # first arg: input length, second: output length
        self.fc1 = nn.Linear(128 * 4 * 5, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 3)
        
    def forward(self, x: torch.Tensor):

        # Max pooling over 2,2, dropout with prob 50 %
        x = F.max_pool2d(F.relu(F.dropout(self.conv1(x), p=0.5)), (2,2),2)
        x = F.max_pool2d(F.relu(F.dropout(self.conv2(x), p=0.5)), (2,2),2)
        x = F.max_pool2d(F.relu(F.dropout(self.conv3(x), p=0.5)), (2,2),2)
        x = F.max_pool2d(F.relu(F.dropout(self.conv4(x), p=0.5)), (2,2),2)
        x = F.max_pool2d(F.relu(F.dropout(self.conv5(x), p=0.5)), (2,2),2)
        
        # x = F.max_pool2d(F.relu(F.dropout(self.conv1(x), p=0.5)), 2)
        # x = F.max_pool2d(F.relu(F.dropout(self.conv2(x), p=0.5)), 2)
        # x = F.max_pool2d(F.relu(F.dropout(self.conv3(x), p=0.5)), 2)
        # x = F.max_pool2d(F.relu(F.dropout(self.conv4(x), p=0.5)), 2)
        # x = F.max_pool2d(F.relu(F.dropout(self.conv5(x), p=0.5)), 2)
        
        x = x.view(-1, 128 * 4 * 5)
        x = F.relu(F.dropout(self.fc1(x), p=0.5))
        x = F.relu(F.dropout(self.fc2(x), p=0.5))
        x = F.relu(F.dropout(self.fc3(x), p=0.5))
        x = nn.LogSoftmax(dim=1)(F.dropout(self.fc4(x), p=0.5))
        
        return x