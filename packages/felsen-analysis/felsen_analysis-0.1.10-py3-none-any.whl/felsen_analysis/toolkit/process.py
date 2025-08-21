import h5py
import numpy as np
from felsen_analysis.backend.ephysinterface import Population


class AnalysisObject():
    """
    This class is used in the background of the toolkit modules. 
    It has helper properties to make the code more readable & writeable.
    """
    def __init__(self, h5file):
        self.hdf = h5file
        return
    
    def load(self, path):
        """
        This is a helper function for easily loading h5 files
        """
        obj = None
        with h5py.File(str(self.hdf), 'r') as file:
            try:
                obj = file[path]
                if type(obj) == h5py.Dataset:
                   return np.array(obj)
                elif type(obj) == h5py.Group:
                    return obj
            except KeyError:
                pass

    def save(self, path, value, overwrite=True):
        """
        Helper function for easily saving data into the h5file
        """
        #if self.hdf.exists() == False:
            #file = h5py.File(str(self.hdf), 'w')
        #else:
        file = h5py.File(str(self.hdf), 'a')
        #
        if path in file.keys():
            if overwrite:
                del file[path]
            else:
                raise Exception(f'{path} dataset already exists')
        #
        dataset = file.create_dataset(path, value.shape, value.dtype, data=value)
        #
        file.close()        
        return
    
    def hasDataset(self, path):
        """
        Looks for a group/dataset in the output file
        """

        with h5py.File(self.hdf, 'r') as file:
            try:
                dataset = file[path]
                return True
            except KeyError:
                return False
    
    def _population(self):
        """
        Creates instance of Population class & assigns the instance to an attribute called population
        """
        self.population = Population(self)
        return self.population
    
    def listAllDatasets(self):
        """
        Easy way to access all the info in the h5file
        """

        pathsInFile = list()
        with h5py.File(self.hdf, 'r') as file:
            file.visit(lambda name: pathsInFile.append(name))

        datasetsInFile = list()
        with h5py.File(self.hdf, 'r') as file:
            for path in pathsInFile:
                if type(file[path]) == h5py.Dataset:
                    datasetsInFile.append(path)

        #
        for path in datasetsInFile:
            print(path)

    
