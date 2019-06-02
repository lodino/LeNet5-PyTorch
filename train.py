from model import LeNet5
import torch
import torch.nn as nn
import numpy as np
from torchvision import datasets, transforms
import os


class Trainer():
    def __init__(self, epochs, batch_size=64, gpu=None):
        if gpu:
            self.device = gpu
        else:
            self.device = "cpu"
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = LeNet5().to(self.device)
        self.train_loader = None
        self.test_loader = None

    def load_data(self):
        train_dataset = datasets.MNIST('data/', download=True, train=True,
                                       transform=transforms.Compose([
                                           transforms.ToTensor(),
                                           transforms.Normalize((0.1307,), (0.3081,)),
                                       ]))
        test_dataset = datasets.MNIST('data/', download=True,
                                      transform=transforms.Compose([
                                          transforms.ToTensor(),
                                          transforms.Normalize((0.1307,), (0.3081,)),
                                      ]))
        self.train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        self.test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=self.batch_size, shuffle=True)

    def train(self):
        self.load_data()
        self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=0.002, betas=(0.5, 0.999))
        l2_loss_func = nn.MSELoss(reduce=True, size_average=False).to(self.device)

        for epoch in range(self.epochs):
            for ind, data in enumerate(self.train_loader, 1):
                self.optimizer.zero_grad()
                img, label = data[0].to(self.device), data[1].to(self.device)
                real_label = torch.zeros(size=(32, 10)).to(self.device)

                result = self.model.forward(img).to(self.device)
                for i in range(32):
                    real_label[i][label[i]] = 1
                loss = l2_loss_func(real_label, result)
                loss.backward()
                self.optimizer.step()

            test_loss = 0
            for ind, data in enumerate(self.test_loader, 1):
                img, label = data[0].to(self.device), data[1].to(self.device)
                real_label = torch.zeros(size=(32, 10)).to(self.device)

                result = self.model.forward(img).to(self.device)
                for i in range(32):
                    real_label[i][label[i]] = 1
                test_loss += l2_loss_func(real_label, result)
            test_loss /= ind

            print(f'====> epoch: {epoch}/{self.epochs}, loss on train set: {loss}')
            print(f'====> epoch: {epoch}/{self.epochs}, loss on test set: {test_loss}')

            # checkpoint
            if epoch % 5 == 0:
                if not os.path.exists("checkpoint"):
                    os.mkdir("checkpoint")

                model_out_path = f"checkpoint/LeNet5_epoch_{epoch}.pth"
                torch.save(self.model, model_out_path)
                print("Checkpoint saved to checkpoint/")


if __name__ == "__main__":
    trainer = Trainer(100, batch_size=32, gpu="cuda:0")
    trainer.train()
