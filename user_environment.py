import numpy as np
import math
H=[0.1,0.3];σ=0.5;B=1
class envr(object):
    def __init__(self):
        pass
    def reset(self):
        r1 =1 + H[0] * 0.5 / σ;r2= 1 + H[1] * 0.5 / σ
        #eh1=np.random.uniform(0,1)
        eh1=0.7
        return np.array([r1,r2,eh1])
    def step(self,s,a):
        a1=a[0];a2=a[1]
        if a1+a2<=s[2]:
            ratio=B*(math.log2(1+H[0] * a1/σ)+math.log2(1+H[1] * a2/σ))/1
            return np.array([1+H[0] * a1/σ,1+H[1] * a2/σ,np.random.uniform(0,1)]),ratio
            #return np.array([1 + H[0] * a1 / σ,1 + H[1] * a2 / σ,0.7]), ratio
        else:
            if a1<=s[2] and a2<=s[2]:
                ratio1 = B * (math.log2(1 + H[0] * a1 / σ) + math.log2(1 + H[1] * a2 / σ)) /(1+a2)
                ratio2 = B * (math.log2(1 + H[0] * a1 / σ) + math.log2(1 + H[1] * a2 / σ)) / (1+ a1)
                ratio_tol=[ratio1,ratio2]
                index=ratio_tol.index(max(ratio_tol))
                return np.array([1+H[0] * a1/σ,1+H[1] * a2/σ,np.random.uniform(0,1)]),ratio_tol[index]
                #return np.array([1 + H[0] * a1 / σ,1 + H[1] * a2 / σ,0.7]), ratio_tol[index]
            elif a1>=s[2] and a2<=s[2]:
                ratio = B * (math.log2(1 + H[0] * a1 / σ) + math.log2(1 + H[1] * a2 / σ)) / (1 + a1)
                return np.array([1 + H[0] * a1 / σ, 1 + H[1] * a2 / σ, np.random.uniform(0, 1)]), ratio
                #return np.array([1 + H[0] * a1 / σ,1 + H[1] * a2 / σ,0.7]), ratio
            elif a1<=s[2] and a2>=s[2]:
                ratio = B * (math.log2(1 + H[0] * a1 / σ) + math.log2(1 + H[1] * a2 / σ)) / (1+ a2)
                return np.array([1 + H[0] * a1 / σ, 1 + H[1] * a2 / σ, np.random.uniform(0, 1)]), ratio
                #return np.array([1 + H[0] * a1 / σ,1 + H[1] * a2 / σ,0.7]), ratio
            elif a1>=s[2] and a2>=s[2]:
                ratio = B * (math.log2(1 + H[0] * a1 / σ) + math.log2(1 + H[1] * a2 / σ)) / (1 + a2+a1)
                return np.array([1 + H[0] * a1 / σ, 1 + H[1] * a2 / σ, np.random.uniform(0, 1)]), ratio
                #return np.array([1 + H[0] * a1 / σ,1 + H[1] * a2 / σ,0.7]), ratio








