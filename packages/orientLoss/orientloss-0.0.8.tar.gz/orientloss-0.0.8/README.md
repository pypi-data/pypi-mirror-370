# orientLoss
orientLoss is a classification loss function. It less prone to overfitting compared to crossEntropy. Compatible with random vector/embeddings with direction-indicating categories、probabilistic、oneHot as target.

## 思路说明
很多时候网络需要输出的类别数远高于网络中使用的特征数/通道数,需要在最后一层加一个巨大的线性层将输出扩增才送入交叉熵损失.但本质上这一层并没有增加信息量,所以可以使用某些损失函数取代这一过程.再考虑到交叉熵由于其下降没有终点,容易引起过拟合.通过设计公式从形状上逼近和优化维度无限扩增后的交叉熵损失得到了这个损失函数.

## Install
```bash
pip install orientLoss
```

## Use
```python
from orientLoss import orientLoss
...
loss=orientLoss(input,target,dim=-1,meanOut=True,angleSmooth=1,normSmooth=1,dimScalingOrd=0,eps=1e-8)
```

target可以是由方向指示类别的随机向量/嵌入、概率、独热编码. 概率或独热编码输入时最好各类别独立进行标准化后再送入损失函数.
