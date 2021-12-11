import numpy as np
import math
vals=[20,20,15,28,26,17,26,40,33,18,25,30,45,20]
mean=sum(vals)/len(vals)
print(mean)
num_var=np.var(vals)
std=np.std(vals)
print(std)

vals1=[20,40,33,45]
std1=np.std(vals1)
vals2=[20,26,26,25,30]
std2=np.std(vals2)
vals3=[15,20]
std3=np.std(vals3)
vals4=[28,17,18]
std4=np.std(vals4)
print(std1)
print(std2)
print(std3)
print(std4)
print("--------avg")
print(np.average(vals1))
print(np.average(vals2))
print(np.average(vals3))
print(np.average(vals4))
s=(4/14) * 9.39+(5/14) * 3.2 + (2/14) * 2.5+ (3/14) * 4.96
print(s)
print("--------------")
val=[20]
st=np.std(val)
print(st)
val2=[20,15,28,26,17,26,40,33,18,25,30,45,20]
print(np.std(val2))

print(0.0 * (1/14) + (13/14) * 8.60)
print("----------")
test3=[20,28,17,33,18,25,20]
print(np.std(test3))
test4=[20,15,26,26,40,30,45]
print(np.std(test4))
print((7/14) * 5.45 + (7/14) * 9.8)
print("--------Reset")
print(np.std([20,40,45]))
print(9.39-(10.8 * (3/4)+ 0.0 *  (1/4)))
print("----Math")
print(np.std([26,26,30]))
print(3.2- ( (2/5)* 2.5+ (3/5) * 1.88))