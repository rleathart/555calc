from math import log
from engineering_notation import EngNumber

def MaxCurrent(Vs,Vc,R6,R7):
    I1 = Vs/R7                 # Current through R7
    I2 = Vc/R6                 # Current through R6/VR2
    I3 = I1 + I2               # Current into pin 7
    return I3

class ChargeTime:
    def __init__(self,R,C,VR,rTol,cTol,logDes,logLow,logHigh):
        self.minLow    = -log(logLow)*(R)*(1 + rTol)*(C)*(1 + cTol)
        self.minHigh   = -log(logHigh)*(R)*(1 - rTol)*(C)*(1 - cTol)
        self.maxLow    = -log(logLow)*(R+VR)*(1 + rTol)*(C)*(1 + cTol)
        self.maxHigh   = -log(logHigh)*(R+VR)*(1 - rTol)*(C)*(1 - cTol)
        self.minDesign = -log(logDes)*(R)*(C)
        self.maxDesign = -log(logDes)*(R+VR)*(C)

R = []
C = []

VR2=[500,1000,2000,5000,10000,20000,50000,100000]

rValues = [1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
rValuesLarge=[1,1.5]

cValues = [10,15,22,33,47,68]

for n in range(0,6):
    for r in rValues:
        R.append(round(r*10**n,1))
for r in rValuesLarge:
    R.append(round(r*10**6,1))

for n in range(-12,-7):
    for c in cValues:
        C.append(float('{:.3g}'.format(c*10**n)))

# Could maybe impletment these into the log arguments for
# the ChargeTime class but it's a lot of typing

Vs     = 5
Vth    = 3.3
VthMin = 2.4
VthMax = 4.2
Vtr    = 1.67
VtrMin = 1.1
VtrMax = 2.2

rTol = 0.01
cTol = 0.1

fDiff = 50000

tDiff = 0.06

solList = []

fTarget = 38000
tMin    = 600e-9
iMax    = 10e-3

for vr2 in VR2:
    for R7 in R:
        for R6 in R:
            for x in C:
                # log values pre calculated
                t3 = ChargeTime(R7+R6,x,vr2,rTol,cTol,(170/333),(2/7),(2/3))
                t4 = ChargeTime(R6,x,vr2,rTol,cTol,(167/330),(11/21),(11/24))

                fmaxDesign = 1/(t3.minDesign + t4.minDesign)
                fminDesign = 1/(t3.maxDesign + t4.maxDesign)

                fmaxHigh = 1/(t3.minHigh + t4.minHigh)
                fminHigh = 1/(t3.maxHigh + t4.maxHigh)

                fmaxLow = 1/(t3.minLow + t4.minLow)
                fminLow = 1/(t3.maxLow + t4.maxLow)

                DischMaxDesign = MaxCurrent(Vs,Vth,R6,R7)
                DischMaxLow    = MaxCurrent(Vs,VthMax,R6,R7)
                DischMaxHigh   = MaxCurrent(Vs,VthMin,R6,R7)

                vr2Estim = (((1/(fTarget*x))-(R7*log((5-Vtr)\
                        /(5-Vth))))/log((5-Vtr)*Vth/((5-Vth)*Vtr)))-R6
                t3Estim = -(R7 + R6 + vr2Estim)*x*log((Vth-5)/(Vtr-5))
                t4Estim = -(R6 + vr2Estim)*x*log(Vtr/Vth)

                if     fminDesign <= fTarget \
                   and fmaxDesign >= fTarget \
                   and fminLow    <= fTarget \
                   and fminHigh   <= fTarget \
                   and fmaxLow    >= fTarget \
                   and fmaxHigh   >= fTarget \
                   \
                   and fmaxDesign - fminDesign <= fDiff\
                   \
                   and t3.minHigh   > tMin \
                   and t3.minLow    > tMin \
                   and t3.maxHigh   > tMin \
                   and t3.maxLow    > tMin \
                   and t3.minDesign > tMin \
                   and t3.minDesign > tMin \
                   and t4.minHigh   > tMin \
                   and t4.minLow    > tMin \
                   and t4.maxHigh   > tMin \
                   and t4.maxLow    > tMin \
                   and t4.minDesign > tMin \
                   and t4.minDesign > tMin \
                   \
                   and DischMaxDesign <= iMax \
                   and DischMaxLow    <= iMax \
                   and DischMaxHigh   <= iMax \
                   \
                   and t3Estim >= (1.7-tDiff)*t4Estim\
                   and t3Estim <= (1.7+tDiff)*t4Estim\
                   :
                       solList.append([\
                               EngNumber(R7),\
                               EngNumber(vr2),\
                               EngNumber(R6),\
                               EngNumber(x),\
                               EngNumber(fmaxDesign-fminDesign),\
                               EngNumber(fmaxDesign),\
                               EngNumber(fminDesign),\
                               EngNumber(DischMaxDesign),\
                               EngNumber(DischMaxLow),\
                               abs(round(t3Estim/t4Estim-1.7,3))
                               ])
diffMin=[]
for i in range(0,len(solList)):
    diffMin.append(solList[i][9])    # Choose parameter to minimise
print(solList[diffMin.index(min(diffMin))])
fSol=solList[diffMin.index(min(diffMin))]

print("R7 = %-*s VR2 = %-*s R6 = %-*s C5 = %-*s" % \
    (5,fSol[0],5,fSol[1],5,fSol[2],5,fSol[3]))
