# Created at 2020-02-06
# Filename:main.py
# Author:Wang Pan
# Purpose:
#
import pickle
from DataLoader import DataLoader
import torch
import torch.autograd
import torch.nn as nn
import torch.nn.functional as fn
import torch.optim as optim
import argparse
import yaml


def pickle_save(filename,object):
    with open(filename,'wb') as f:
        pickle.dump(object,f)

class MyModel(nn.Module):
    def __init__(self):
        super(MyModel,self).__init__()
        self.iuput_dim=2
        self.output_dim=1
        self.num_nodes=207
        self.batch_sz=64
        self.layer1=nn.Linear(self.iuput_dim*self.num_nodes*12,self.num_nodes*12)
    def forward(self,x):
        '''
        :param x: (batch_size,... other input dimensions)
        :return: y: (batch_size,... other output dimensions)
        '''
        x=x.reshape(self.batch_sz,self.iuput_dim*self.num_nodes*12)
        x=self.layer1(x)
        x=x.reshape(64,12,207,1)
        return x

class Process_Handler():
    def __init__(self,loader,dir_args,model_args,train_args):
        self.loader=loader
        self.save_dir=dir_args['save_dir']
        self.log_dir=dir_args['log_dir']
        self.batch_size=train_args['batch_size']
        self.lr=train_args['learning_rate']
        self.loss_fn=self.set_loss(train_args['loss_fn'])
        self.model=MyModel()
        if train_args['optimizer']=='Adam':
            self.optimizer=optim.SGD(self.model.parameters(),lr=self.lr)

    @staticmethod
    def set_loss(loss_name):
        if loss_name=='MSELoss':
            return nn.MSELoss()
        else:
            raise AttributeError('No Such Loss')

    def train(self):
        self.model.train()
        self.loader.set('train')
        for i,(x,y) in enumerate(self.loader.get(self.batch_size)):
            x=torch.from_numpy(x).float()
            y=torch.from_numpy(y).float()
            pred=self.model(x)
            loss=self.loss_fn(pred,y)
            loss.backward()
            self.optimizer.step()
        pass

    def val(self):
        pass

    def test(self):
        self.model.eval()

        pass

    def save(self,filename):
        torch.save({'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optmz.state_dict()},
                   filename)
        return filename

    def load(self,filename):
        ckp = torch.load(filename)
        self.model.load_state_dict(ckp['model_state_dict'])
        self.optmz.load_state_dict(ckp['optimizer_state_dict'])
        return filename

def main(args):
    dir_args=args['dir']
    data_args=args['data']
    model_args=args['model']
    train_args=args['train']
    loader=DataLoader(data_args)
    handler=Process_Handler(loader,dir_args,model_args,train_args)
    max_val=1000
    val_mae=1000
    for _ in range(train_args['epochs']):
        handler.train()
        val_mae=handler.val()
        if val_mae<max_val:
            handler.save()
    handler.load()
    test_table=handler.test()
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='./config.yaml')
    args = parser.parse_args()
    with open(args.config,'r') as f:
        args=yaml.load(f)
    main(args)