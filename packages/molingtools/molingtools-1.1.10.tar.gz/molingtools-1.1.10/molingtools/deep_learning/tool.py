try:
    from sklearn.model_selection import train_test_split
    import numpy as np
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install numpy scikit-learn')
    

def get_train_test_sample(X:np.ndarray, Y:np.ndarray, test_rate: float=0.2, **sklearn_kwargs)-> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    """X_train, X_test, y_train, y_test"""
    return train_test_split(X, Y,   
                            test_size=test_rate,# 测试集占比
                            stratify=Y,         # 分层采样保持类别比例
                            **sklearn_kwargs
                            )