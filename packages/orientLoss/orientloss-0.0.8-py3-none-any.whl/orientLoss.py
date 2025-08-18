import torch
import math


def orientLoss(input,target,dim=1,meanOut=True,angleSmooth=1,normSmooth=1,dimScalingOrd=1,flat=1,eps=1e-8,simple=True):
    m=angleSmooth/2
    n=normSmooth-m
    diff=input-target #注意这里顺序不要写反
    numel=diff.numel()
    diffNorm=torch.linalg.norm(diff,ord=2,dim=dim,keepdim=False)
    numel/=diffNorm.numel()
    t=target.broadcast_to(diff.size())
    targetNorm=torch.linalg.norm(t,ord=2,dim=dim,keepdim=False)
    dot=(diff*t).sum(dim=dim,keepdim=False)
    loss1=(diffNorm+eps)**(2*n)
    loss2=(diffNorm-dot/(targetNorm+eps)+eps)**(2*m)
    sqrtNumel=math.sqrt(numel)
    if simple:
        k=1/((4**m)*(numel**(m+n)))
    else:
        k=1/(((eps+sqrtNumel)**(2*n))*((eps+sqrtNumel+numel/(sqrtNumel+eps))**(2*m)))
    loss=(loss1*loss2)*k
    if simple:
        b=targetNorm*flat/sqrtNumel
        a=b.square()
    else:
        a=(targetNorm*flat).square()/numel
        b=(a+((eps**(2*(m+n)))*k+eps)).sqrt()
    loss=(loss+a+eps).sqrt()-b
    loss=loss*(targetNorm/((((eps+1)+a).sqrt()-b)*(numel**(dimScalingOrd-0.5))))
    #loss[~torch.isfinite(loss)]=0
    
    if meanOut:
        return loss.mean()
    else:
        return loss
       







