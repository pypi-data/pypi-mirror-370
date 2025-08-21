import numpy as np
import h5py
import re

"""
AUTHOR: Xiaolong Du

Read the halo information from Galacticus outputs.

Default units:

Mass            Msun
Time            Gyr
Length          Mpc
Velocity        km/s

Available halo properties:

time            time since the big bang

posX            x position of a halo with respect to the host halo
posY            y position of a halo with respect to the host halo
posZ            z position of a halo with respect to the host halo
velX            x velocity of a halo with respect to the host halo
velY            y velocity of a halo with respect to the host halo
velZ            z velocity of a halo with respect to the host halo
Rorbit          Distance to the host center

Minfall         Mass at infall
Mbound          Bound mass
Rbound          Radius eonclosing the bound mass
Mvir            Virial mass defined with a specified virial density contrast definition
                (for subhalo this may be slightly different Mbound)
Vmax            Maximum circualr velocity
Rmax            Radius where the circular velocity reaches its maximum
Rtidal          Tidal radius
Rapo            Apocenter distance
Rperi           Pericenter distance

MHost           Virial mass of the host halo at each output
RHost           Virial radius of the host halo at each output
RsHost          Scale radius of the host halo at each output
RvirSat0        Virial radius of the subahlo at infall
RsSat0          Scale radius of the subahlo at infall
cSat0           Concentration of the subhalo at infall

## Density profile
densityHost(i)  Return the density profile of host halo at i-th snapshot. Note that i starts with 0
density    (i)  Return the density profile of subhalo at i-th snapshot. Note that i starts with 0
densityProj(i)  Return the projected density of subhalo at i-th snapshot. Note that i starts with 0

"""


class GalacticusDataSingle_Du(object):

    def __init__(self, fileName):
        """
        This class reads and stores information from a single galacitucs run
        :param fileName: the file path for the hdf5file output by galacticus
        """
        # Open the data file.
        self.fileRead = h5py.File(fileName, 'r')
        self.NOutput = len(self.fileRead["Outputs"].keys())
        self.fileName = fileName

        self.time = np.zeros(self.NOutput)
        self.posX = np.zeros(self.NOutput)
        self.posY = np.zeros(self.NOutput)
        self.posZ = np.zeros(self.NOutput)
        self.velX = np.zeros(self.NOutput)
        self.velY = np.zeros(self.NOutput)
        self.velZ = np.zeros(self.NOutput)
        self.Rorbit = np.zeros(self.NOutput)
        self.Minfall = np.zeros(self.NOutput)
        self.Mbound = np.zeros(self.NOutput)
        self.Rbound = np.zeros(self.NOutput)
        self.Mvir = np.zeros(self.NOutput)
        self.Vmax = np.zeros(self.NOutput)
        self.Rmax = np.zeros(self.NOutput)
        self.Rtidal = np.zeros(self.NOutput)
        self.Rapo = np.zeros(self.NOutput)
        self.Rperi = np.zeros(self.NOutput)
        self.MHost = np.zeros(self.NOutput)
        self.RHost = np.zeros(self.NOutput)
        self.RsHost = np.zeros(self.NOutput)

        for i in range(self.NOutput):
            basicMass = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/basicMass"][:]
            indexSat = np.argmin(basicMass)
            indexHost = np.argmax(basicMass)

            self.time[i] = self.fileRead["Outputs/Output" + str(i + 1)].attrs["outputTime"]
            self.posX[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/positionOrbitalX"][indexSat]
            self.posY[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/positionOrbitalY"][indexSat]
            self.posZ[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/positionOrbitalZ"][indexSat]
            self.velX[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/velocityOrbitalX"][indexSat]
            self.velY[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/velocityOrbitalY"][indexSat]
            self.velZ[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/velocityOrbitalZ"][indexSat]
            self.Minfall[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/massBasic"][indexSat]
            self.Mbound[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/massBound"][indexSat]
            self.Rbound[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/satelliteRadiusBoundMass"][
                indexSat]
            self.Mvir[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/massHaloEnclosedCurrent"][indexSat]
            self.Vmax[i] = \
            self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/darkMatterProfileDMOVelocityMaximum"][indexSat]
            self.Rmax[i] = \
            self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/darkMatterProfileDMORadiusVelocityMaximum"][
                indexSat]
            self.Rtidal[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/satelliteRadiusTidal"][indexSat]

            self.Rapo[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/satelliteApocenterRadius"][indexSat]
            self.Rperi[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/satellitePericenterRadius"][
                indexSat]
            self.MHost[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/massBasic"][indexHost]
            self.RHost[i] = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/darkMatterOnlyRadiusVirial"][
                indexHost]
            self.RsHost[i] = self.fileRead["Outputs/Output" + str(1) + "/nodeData/darkMatterProfileScale"][indexHost]

        self.Rorbit = np.sqrt(self.posX ** 2 + self.posY ** 2 + self.posZ ** 2)
        self.Vorbit = np.sqrt(self.velX ** 2 + self.velY ** 2 + self.velZ ** 2)
        self.Lz = self.posX * self.velY - self.posY * self.velX

        basicMass = self.fileRead["Outputs/Output" + str(1) + "/nodeData/basicMass"][:]
        indexSat = np.argmin(basicMass)
        self.RvirSat0 = self.fileRead["Outputs/Output" + str(1) + "/nodeData/darkMatterOnlyRadiusVirial"][indexSat]
        self.RsSat0 = self.fileRead["Outputs/Output" + str(1) + "/nodeData/darkMatterProfileScale"][indexSat]
        self.cSat0 = self.RvirSat0 / self.RsSat0

        radii = np.array([])
        radiiName = []
        radiiColumns = self.fileRead["Outputs/Output" + str(1) + "/nodeData/densityProfileColumns"][:]
        for dataName in radiiColumns:
            split = re.split(r":", dataName.decode())
            radii = np.append(radii, float(split[-1]))
            radiiName.append(split[-1])

        self.radiiRatio = radii
        self.radiiSat = radii * self.RvirSat0
        self.radiiName = radiiName
        self.NRadii = len(radii)

        self.fileRead.close()

    def __del__(self):
        self.fileRead.close()

    def densityHost(self, i):
        # Return the density profile of the host.
        self.fileRead = h5py.File(self.fileName, 'r')
        basicMass = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/basicMass"][:]
        indexHost = np.argmax(basicMass)

        densityProfileHost = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/densityProfile"][indexHost]

        self.fileRead.close()
        return densityProfileHost

    def density(self, i):
        # Return the density profile of the subhalo.
        self.fileRead = h5py.File(self.fileName, 'r')
        basicMass = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/basicMass"][:]
        indexSat = np.argmin(basicMass)

        densityProfile = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/densityProfile"][indexSat]

        self.fileRead.close()
        return densityProfile

    def densityProj(self, i):
        # Return the projected density of the subhalo.
        self.fileRead = h5py.File(self.fileName, 'r')
        basicMass = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/basicMass"][:]
        indexSat = np.argmin(basicMass)

        densityProfileProj = self.fileRead["Outputs/Output" + str(i + 1) + "/nodeData/projectedDensity"][indexSat]

        self.fileRead.close()
        return densityProfileProj

