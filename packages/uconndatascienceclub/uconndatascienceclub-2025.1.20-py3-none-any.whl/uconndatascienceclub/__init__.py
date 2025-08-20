import os
import pandas as pd
import numpy as np
import random

#various forms of contact; ex. calling ucdsc.uconntact will print the given link
uconntact = 'https://uconntact.uconn.edu/organization/datascience'
instagram = '@uconndatascience'
email = 'uconndatascience@gmail.com'
discord = 'https://discord.gg/Yb7dBYn4jS'

socials = {'UConntact': uconntact,
           'Instagram': instagram,
           'Email': email,
           'Discord': discord}

def test_function():
    return 'Test works'

def leon_intro():
    return 'this works'

def welcome():
        '''Get a welcome message to ensure package is working properly.
        
        Returns
        -------
        str
            A welcome string.
        '''
        return 'Welcome to UConn Data Science Club!'

#unfinished
def schedule(year: int=2025, semester: str='spring') -> dict:
        '''
        Get the schedule for the specified year and semester.

        Parameters
        ----------
        year : int, optional
            The academic year. Must be one of {2024, 2025}. Default is 2025 (current year).
        semester : str, optional
            The academic semester. Must be one of {'spring', 'fall'}. Default is 'spring'.

        Returns
        -------
        dict
            A dictionary representing the schedule for the given year and semester.
        '''
        # implementation
        print('Coming soon!')
        pass

#unfinished
class Courses():
    pass

#The core data class that handles dataset imports. There is one optional parameter 'dataset' that takes in the
#name of a dataset using a string. To see the available strings that are recognized, call Data().list_datasets()
class Data():
    
    def __init__(self, dataset=None):
        if dataset:
            self.dataset = dataset.lower()
        else:
            self.dataset = None

        #This dictionary holds all available datasets. If you add a dataset, it is essential that you add it
        #to this dictionary. Create any key you want, then use the name of the dataset file as the corresponding
        #value. Make sure to have the dataset in the 'datasets' folder.
        self.available_datasets = {
            #'boston': 'housing.csv',
            None: None,
            'forbes': 'Forbes_Global_2000.csv',
            'mall': 'Mall_Customers.csv',
            'fires': 'forestfires.csv',
            'population': '',
            'temperatures': 'https://raw.githubusercontent.com/datasets/global-temp/master/data/monthly.csv',
            'automobile': 'Automobile_data.csv'
        }

        #error handling
        if self.dataset not in self.available_datasets:
            raise ValueError(
                f"Dataset '{self.dataset}' is not available. "
                f"Choose from {self.list_datasets()}."
            )
    
    #this function returns the pandas dataframe of the dataset specified by self.data. If self.data is None, an
    #error will be triggered
    def dataframe(self) -> pd.DataFrame:

        if not self.dataset:
            self.no_data()

        dataset_path = os.path.join(os.path.dirname(__file__), 'datasets', self.available_datasets[self.dataset])

        #sometimes pandas needs different encodings when reading the csv files; if that's the case, just add
        #exception handling here
        if self.dataset == 'forbes':
            return pd.read_csv(dataset_path, encoding='latin1')
        if self.dataset == 'population':
            return pd.DataFrame({
                                    "City": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
                                    "Population": [8419600, 3980400, 2716000, 2328000, 1690000],
                                    "Latitude": [40.7128, 34.0522, 41.8781, 29.7604, 33.4484],
                                    "Longitude": [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740]
                                })
        if self.dataset == 'temperatures':
            return pd.read_csv(self.available_datasets[self.dataset])
        
        return pd.read_csv(dataset_path)
    
    #lists all available keys that point to datasets
    def list_datasets(self):
        return [key for key in self.available_datasets.keys() if key]
    
    def no_data(self):
        #for error handling
        raise ValueError(
            f"No dataset established. "
            f"Choose from {self.list_datasets()}. "
            f"Call the `set_data()` method to establish a dataset."
        )
    
    def set_data(self, data):
         #if Data() class is called with no dataset given, a dataset can be established with this function
         if data not in self.available_datasets:
            raise ValueError(
                f"Dataset '{self.dataset}' is not available. "
                f"Choose from {self.list_datasets()}."
            )
         
         self.dataset = data.lower()

    def save(self) -> None:
        #saves dataset as csv in local directory
        if not self.dataset:
            self.no_data()

        df = self.dataframe()
        df.to_csv(self.available_datasets[self.dataset])

    def source(self, data=None) -> str:
        pass
    
    def standard(self, dim=1, size=100, state=None) -> pd.DataFrame:
        #generates a pandas dataframe with standard normal columns; dim=number of columns, size=number of rows
        #state = random state
        #This function could be removed if you wanted; generate() can accomplish the same tasks
        if state:
            np.random.seed(state)  
        data = np.random.standard_normal(size=(size, dim))  
        return pd.DataFrame(data, columns=[f"col_{i+1}" for i in range(dim)])

    def uniform(self, dim=1, size=100, state=None) -> pd.DataFrame:
        #generates a pandas dataframe with uniform columns; dim=number of columns, size=number of rows
        #state = random state
        #This function could be removed if you wanted; generate() can accomplish the same tasks
        if state:
            np.random.seed(state)  
        data = np.random.uniform(low=0, high=1, size=(size, dim))  
        return pd.DataFrame(data, columns=[f"col_{i+1}" for i in range(dim)])
    
    def generate(self, dim=1, size=100, mean=0, sd=1, distributions=['normal'], state=None, low=None, high=None):
        #generate() is a functin that can create a pandas dataframe containing many different randomly generated
        #distributions. dim = # of columns, size = # of rows, state = random state. By default, the function
        #generates one column following a standard normal distribution. The distributions parameter specifies
        #which distributions the function should sample from. The available distributions are listed below in the
        # 'Ds' dictionary. 

        # The mean and sd parameters can either be a list of numbers of length 2 or a floating point number. For the mean, if a list
        #(ex. [1, 5]), then the distributions will have a random mean within the values specified in the list. If a number,
        #then the means will be that number. The same goes for the sd parameter.

        #The low and high parameters are specifically for the uniform distribution. If 'uniform' is present in the distributions
        #paremeter and one or both of low and high are not specified, then the function will return an error.
        
        Ds = {'normal', 'uniform', 'beta', 'exponential', 'poisson', 'binomial'}
        distributions = [i.lower() for i in distributions]
        if not set(distributions) <= Ds:
            raise ValueError(f'Distribution list contains unrecognized distribution. Choose from the following: {Ds}')
        if 'uniform' in distributions and (low==None or high==None):
            raise ValueError("'uniform' distribution included in the distribution list. Please ensure the 'low' and 'high' parameters are given values, or remove the uniform distribution.")

        if state:
            np.random.seed(state)
            random.seed(state)
        if isinstance(mean, list):
            lowm = mean[0]
            highm = mean[1]
        else:
            lowm = mean
            highm = mean
        if isinstance(sd, list):
            lowsd = sd[0]
            highsd = sd[1]
        else:
            lowsd = sd
            highsd = sd
        
        data = pd.DataFrame()
        for i in range(dim):
            data_mean = random.randint(lowm, highm)
            data_sd = random.randint(lowsd, highsd)
            dist = random.choice(distributions)
            if dist == 'normal':
                new_data = np.random.normal(data_mean, data_sd, size=(size, 1))
            elif dist == 'uniform':
                new_data = np.random.uniform(low, high, size=(size, 1))
            elif dist == 'exponential':
                new_data = np.random.exponential(scale=max(1, data_mean), size=(size, 1))
            elif dist == 'poisson':
                new_data = np.random.poisson(lam=max(1, data_mean), size=(size, 1))
            elif dist == 'binomial':
                new_data = np.random.binomial(n=max(1, data_mean), p=min(1, max(0, data_sd / 10)), size=(size, 1))
            elif dist == 'beta':
                alpha = max(0.1, data_mean / 10)
                beta = max(0.1, data_sd / 10)
                new_data = np.random.beta(alpha, beta, size=(size, 1))

            data = pd.concat([data, pd.DataFrame(new_data)], axis=1)

        data.columns = [f'col_{i+1}' for i in range(dim)]
        return data

class OnlineResources():
    pass
