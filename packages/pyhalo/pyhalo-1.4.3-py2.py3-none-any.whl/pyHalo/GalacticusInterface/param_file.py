import numpy as np
from scipy import optimize
import re
import os, sys

# Set infall redshift.
zInfall = 3.0

# Set halo and subhalo properties
zHost = 0.5
MHost = 1.0e13
cHost = 8.0

MSub = 1.0e8
cSubMean = 20.0
cSubScatter = 0.000001  # (in dex)
# Set a lower limit on the halo concentration
cSubMinimum = 2.0

# Set the number of realizations
Ntree = 10

# Set ramdom seed.
randomSeed = 369

# Set cosmoligical parameters
HubbleConstant = 67.36
OmegaMatter = 0.3153
OmegaDarkEnergy = 0.6847

# Astronomical and physical constants (in units of kg, m, s)
G = 6.673e-11
Mpc = 3.08567758135e22
Msun = 1.98892e30
Gyr = 3.15581498e16
kilo = 1.0e3

# Critical density at the present day (in units of Msun/Mpc**3)
rhoCritical0 = 3.0 * (HubbleConstant * kilo / Mpc) ** 2 / (8.0 * np.pi * G) / (Msun / Mpc ** 3)


# Critical density at z (in units of Msun/Mpc**3)
def rhoCriticalZ(z):
    return rhoCritical0 * (OmegaDarkEnergy + OmegaMatter * (1.0 + z) ** 3)


# Convert redshift to time in Gyr
def t_z(z):
    return 2.0 / 3.0 / np.sqrt(OmegaDarkEnergy) \
           * np.arctanh(1.0 / np.sqrt(1.0 + OmegaMatter / OmegaDarkEnergy * (1.0 + z) ** 3)) \
           / (HubbleConstant * kilo / Mpc) \
           / Gyr


# Find the host mass when the subhalo infall assuming the host density profile
# does not change with time. (Note that the vriail radius, thus the halo mass,
# is redshift-dependent since the critical density of the Universe change with
# redshifts)
#
# Mass definition conversion.
def Mass_Definition_Conversion(M0, R0, c0, delta, z):
    def gc(x):
        return np.log(1.0 + x) - x / (1.0 + x)

    def Mean_Enclosed_Density(r):
        rs = R0 / c0
        Menclosed = M0 * gc(r / rs) / gc(c0)

        return Menclosed / (4.0 / 3.0 * np.pi * r ** 3)

    def rootFun(r):
        return Mean_Enclosed_Density(r) - delta * rhoCriticalZ(z)

    RNew = optimize.brentq(rootFun, 0.001 * R0, 10.0 * R0)
    cNew = RNew / R0 * c0
    MNew = M0 * gc(cNew) / gc(c0)

    return RNew, MNew, cNew


densityContrast = 200.0
RHost = (MHost / (4.0 / 3.0 * np.pi * densityContrast * rhoCriticalZ(zHost))) ** (1.0 / 3.0)
RsHost = RHost / cHost

# Sample the subhalo concentration.
cSub = np.zeros(Ntree)
if (cSubScatter > 0.0):
    cSub = cSubMean * 10.0 ** (cSubScatter * np.random.normal(0.0, 1.0, Ntree))
else:
    cSub = cSubMean

cSub = np.where(cSub > cSubMinimum, cSub, cSubMinimum)

RSubInfall = (MSub / (4.0 / 3.0 * np.pi * densityContrast * rhoCriticalZ(zInfall))) ** (1.0 / 3.0)
RsSubInfall = RSubInfall / cSub

RHostInfall, MHostInfall, cHostInfall = Mass_Definition_Conversion(MHost, RHost, cHost, 200.0, zInfall)

# Infall and current time.
tInfall = t_z(zInfall)
tCurrent = t_z(zHost)

# Generate parameter file.
folder = "Output_zInfall_" + str(zInfall) + "/cHost_" + str(cHost) + "/cSubhaloMean_" + str(cSubMean)

# Creat the folder containing the parameter file and output data.
os.makedirs(folder, exist_ok=True)

file_input = open("parameter_base.xml")
file_output = open(folder + "/parameter.xml", 'w')

line = file_input.readline()
while line:
    line = re.sub(r'randomSeed', str(randomSeed), line)

    line = re.sub(r'hubble', str(HubbleConstant), line)
    line = re.sub(r'Omega_M', str(OmegaMatter), line)
    line = re.sub(r'Omega_L', str(OmegaDarkEnergy), line)

    line = re.sub(r'redshiftInfall', str(zInfall), line)
    line = re.sub(r'hostConcentration', str(cHost), line)
    line = re.sub(r'subhaloConcentration', str(cSubMean), line)
    line = re.sub(r'timeInfall', str(tInfall), line)
    line = re.sub(r'timeCurrent', str(tCurrent), line)

    file_output.write(line, )
    line = file_input.readline()

file_input.close()
file_output.close()

# Generate tree file.
file_input = open("tree_base.xml")
file_output = open(folder + "/tree.xml", 'w')

# Write the headers.
for i in range(2):
    line = file_input.readline()
    file_output.write(line, )

line = '<trees>\n'
file_output.write(line, )

for i in range(Ntree):
    line = file_input.readline()
    while line:
        line = re.sub(r'timeInfall', str(tInfall), line)
        line = re.sub(r'timeCurrent', str(tCurrent), line)
        line = re.sub(r'MHostInfall', str(MHostInfall), line)
        line = re.sub(r'MHostCurrent', str(MHost), line)
        line = re.sub(r'RsHost', str(RsHost), line)

        line = re.sub(r'MSub', str(MSub), line)
        line = re.sub(r'RsSubInfall', str(RsSubInfall[i]), line)

        file_output.write(line, )
        line = file_input.readline()

    file_input.seek(0)
    for i in range(2):
        line = file_input.readline()

line = '</trees>'
file_output.write(line, )

file_input.close()
file_output.close()

