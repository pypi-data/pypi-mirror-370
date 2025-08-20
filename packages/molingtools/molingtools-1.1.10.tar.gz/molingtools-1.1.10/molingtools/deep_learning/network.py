from abc import abstractmethod, ABC
from typing import Literal
try:
    import numpy as np
    import torch
    from torch import Tensor, nn, tensor, float32, bfloat16, as_tensor
    from torch.utils.data import DataLoader, TensorDataset
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install numpy torch')
    
    
class RegressionNNer(ABC):
    """回归模型  
    bfloat16容易梯度消失
    """
    def __init__(self, model_name, 
                 device:Literal['cpu', 'cuda']='cpu', 
                 dtype:Literal['float32', 'bfloat16']='float32', 
                 loss_fn=None):
        self.model_name = model_name
        self.device=device
        self.dtype = float32 if dtype=='float32' else bfloat16
        self._ceils = self.get_ceils()
        self.model = nn.Sequential(*self._ceils).to(device, dtype=self.dtype)
        self.loss_fn = loss_fn or nn.MSELoss()
    
    @abstractmethod
    def get_ceils(self)->list:
        pass
    
    def save(self, filepath):
        torch.save(self.model.state_dict(), filepath)
    
    def load(self, filepath):
        self.model.load_state_dict(torch.load(filepath, map_location=self.device))
    
    def get_verify_loss(self, X:Tensor, Y:Tensor)-> float:
        pY:Tensor = self.predict(X, False)
        loss = self.loss_fn(pY, Y)
        return loss.item()

    def to_tensor(self, X:np.ndarray|list|Tensor):
        if isinstance(X, Tensor): 
            return X.to(dtype=self.dtype, device=self.device)
        else:
            return tensor(X, dtype=self.dtype, device=self.device)
    
    def epoch_event(self, epoch:int, loss:float, verify_loss:float, current_lr:float):
        """每批次结束额外调用的事件函数
        """
        pass
    
    def train(self, X, Y, verify_X, verify_Y, path:str, verify_num:int=50, loss_print=True, 
              learn_step=1e-2, train_num:int=500, max_norm:float=1.0,
              batch_size: int=100_000, num_workers:int=4):
        # 如果 X 是 NumPy 数组，as_tensor方法会尽量共享内存（不拷贝）
        # 更高效，适合大批量数据
        X, Y = tensor(X, dtype=self.dtype, device='cpu'), tensor(Y, dtype=self.dtype, device='cpu')
        verify_X, verify_Y = self.to_tensor(verify_X), self.to_tensor(verify_Y)
        dataloader = DataLoader(TensorDataset(X, Y), batch_size=batch_size, 
                                shuffle=True,           # 每个 epoch 都打乱顺序
                                num_workers=num_workers,# 多进程加载, 数据已在GPU中使用会报错
                                pin_memory=True)        # 锁页内存, 加速 CPU->GPU 传输, 但是初始数据已经在gpu上开启报错
        # 记录验证正确率和对应轮数
        best_verify_loss = 99999
        min_loss, loss_best_index = 99999, 0
        # 进入训练状态
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learn_step)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10)
        total_samples = X.shape[0]
        
        for epoch in range(train_num):
            total_loss = 0.0
            for X_batch, Y_batch in dataloader:
                X_batch, Y_batch = X_batch.to(self.device), Y_batch.to(self.device)
                Y0 = self.model(X_batch)
                # 更新参数
                loss = self.loss_fn(Y0, Y_batch)
                optimizer.zero_grad()
                loss.backward()
                # 防止梯度爆炸
                nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=max_norm)
                optimizer.step()
                total_loss+=loss.item()* X_batch.shape[0]
            loss_value = total_loss/total_samples
            scheduler.step(loss_value)
            
            if min_loss<=loss_value: 
                loss_best_index+=1
            else:
                loss_best_index=0
            min_loss = min(loss_value, min_loss)
            # 收敛提前跳出
            if epoch>100 and loss_best_index>50:
                print(f'模型已收敛, 提前结束训练 min_loss: {min_loss}')
                break
            current_lr = optimizer.param_groups[0]["lr"]
            if loss_print and epoch % 10 == 0: print(f'loss-{epoch}: {loss_value} current_lr: {current_lr}')
            if epoch % verify_num==0:
                verify_loss = self.get_verify_loss(verify_X, verify_Y)
                print(f'verify_loss-{epoch}: {verify_loss}')
                best_verify_loss = verify_loss if best_verify_loss is None else min(verify_loss, best_verify_loss)
                if best_verify_loss==verify_loss: self.save(f'{path}/{self.model_name}_best.pth')
                self.model.train()
            # 调用额外事件
            self.epoch_event(epoch, loss_value, verify_loss, current_lr)
                
        self.save(f'{path}/{self.model_name}_last.pth')
        verify_loss = self.get_verify_loss(verify_X, verify_Y)
        print(f'verify_loss-last: {verify_loss}')
        best_verify_loss = min(verify_loss, best_verify_loss)
        if best_verify_loss==verify_loss: self.save(f'{path}/{self.model_name}_best.pth')

    def predict(self, X, return_index=True)->Tensor|list:
        X = self.to_tensor(X)
        # 进入验证状态
        self.model.eval()
        # 仅验证不更新模型
        with torch.no_grad():
            # 转换为Tensor
            Y:Tensor = self.model(X)
            if return_index:
                return Y.argmax(dim=1).tolist()
            else:
                return Y
    
    def print_parameters(self):
        """打印梯度数据
        """
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                print(f"{name} grad mean: {param.grad.abs().mean().item()}")

class ClassificationNNer(RegressionNNer):
    """分类模型  
    最后的激活函数不需要添加softmax层  
    CrossEntropyLoss损失函数input会被softmax处理  
    训练入参-Y为概率分布  
    """
    def __init__(self, model_name, device:Literal['cpu', 'cuda']='cpu', dtype:Literal['float32', 'bfloat16']='float32', loss_fn=None):
        super().__init__(model_name, device, dtype, loss_fn=loss_fn or nn.CrossEntropyLoss())
        assert isinstance(self._ceils[-1], nn.Linear), '分类模型最后一层只能为nn.Linear, 不用加激活层'
    
    def get_verify_loss(self, X:Tensor, Y:Tensor)-> float:
        pY:Tensor = super().predict(X, False)
        loss = self.loss_fn(pY, Y)
        return loss.item()
    
    def predict(self, X, return_index=True)->Tensor|list:
        Y = super().predict(X,return_index=return_index)
        if return_index: 
            return Y
        else:
            return Y.softmax(dim=1, dtype=self.dtype)
    
    def accuracy(self, X, Y, is_absolute=True)-> float:
        """计算正确率  
        (默认)is_absolute=True:  最大概率序列与Y值校验, 仅适用于单分类情况  
        is_absolute=False: loss的值(v)=-log(p) ==> p=e**-v ; p为正确率  
        """
        X, Y = self.to_tensor(X), self.to_tensor(Y)
        if is_absolute:
            pys = self.predict(X)
            ys = Y.argmax(dim=1).tolist()
            return len([1 for y,py in zip(ys,pys) if y==py])/len(ys)
        else:
            lossv = self.get_verify_loss(X, Y)
            return np.e**-lossv
    
    def index_to_arr(self, indexs:list[int])->np.ndarray[int]:
        out_dim = self._ceils[-1].out_features
        arr = np.zeros((len(indexs), out_dim))
        for index, row in zip(indexs, arr):
            row[index] = 1
        return arr
    
    def y_to_index(self, Y:np.ndarray|Tensor)->np.ndarray[int]:
        Y:np.ndarray = Y.numpy() if isinstance(Y, Tensor) else Y
        return Y.argmax(Y, axis=1)
    