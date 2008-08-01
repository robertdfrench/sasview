"""
    Unit tests for data manipulations
"""

import unittest
import numpy, math
from DataLoader.loader import  Loader
from DataLoader.data_info import Data1D
 
import os.path

class data_info_tests(unittest.TestCase):
    
    def setUp(self):
        self.data = Loader().load("cansas1d.xml")
        
    def test_clone1D(self):
        """
            Test basic cloning
        """
        clone = self.data.clone_without_data()
        
        for i in range(len(self.data.detector)):
            self.assertEqual(self.data.detector[i].distance, clone.detector[i].distance)
            

class manip_tests(unittest.TestCase):
    
    def setUp(self):
        # Create two data sets to play with
        x_0 = numpy.ones(5)
        for i in range(5):
            x_0[i] = x_0[i]*(i+1.0)
            
        y_0 = 2.0*numpy.ones(5)
        dy_0 = 0.5*numpy.ones(5)
        self.data = Data1D(x_0, y_0, dy=dy_0)
        
        x = self.data.x
        y = numpy.ones(5)
        dy = numpy.ones(5)
        self.data2 = Data1D(x, y, dy=dy)
        
        
    def test_load(self):
        """
            Test whether the test file was loaded properly
        """
        # There should be 5 entries in the file
        self.assertEqual(len(self.data.x), 5)
        
        for i in range(5):
            # The x values should be from 1 to 5
            self.assertEqual(self.data.x[i], float(i+1))
        
            # All y-error values should be 0.5
            self.assertEqual(self.data.dy[i], 0.5)    
            
            # All y values should be 2.0
            self.assertEqual(self.data.y[i], 2.0)    
        
    def test_add(self):
        result = self.data2+self.data
        for i in range(5):
            self.assertEqual(result.y[i], 3.0)
            self.assertEqual(result.dy[i], math.sqrt(0.5**2+1.0))
        
    def test_sub(self):
        result = self.data2-self.data
        for i in range(5):
            self.assertEqual(result.y[i], -1.0)
            self.assertEqual(result.dy[i], math.sqrt(0.5**2+1.0))
        
    def test_mul(self):
        result = self.data2*self.data
        for i in range(5):
            self.assertEqual(result.y[i], 2.0)
            self.assertEqual(result.dy[i], math.sqrt((0.5*1.0)**2+(1.0*2.0)**2))
        
    def test_div(self):
        result = self.data2/self.data
        for i in range(5):
            self.assertEqual(result.y[i], 0.5)
            self.assertEqual(result.dy[i], math.sqrt((1.0/2.0)**2+(0.5*1.0/4.0)**2))
        
    def test_radd(self):
        result = self.data+3.0
        for i in range(5):
            self.assertEqual(result.y[i], 5.0)
            self.assertEqual(result.dy[i], 0.5)
            
        result = 3.0+self.data
        for i in range(5):
            self.assertEqual(result.y[i], 5.0)
            self.assertEqual(result.dy[i], 0.5)
            
    def test_rsub(self):
        result = self.data-3.0
        for i in range(5):
            self.assertEqual(result.y[i], -1.0)
            self.assertEqual(result.dy[i], 0.5)
            
        result = 3.0-self.data
        for i in range(5):
            self.assertEqual(result.y[i], 1.0)
            self.assertEqual(result.dy[i], 0.5)
            
    def test_rmul(self):
        result = self.data*3.0
        for i in range(5):
            self.assertEqual(result.y[i], 6.0)
            self.assertEqual(result.dy[i], 1.5)
            
        result = 3.0*self.data
        for i in range(5):
            self.assertEqual(result.y[i], 6.0)
            self.assertEqual(result.dy[i], 1.5)
            
    def test_rdiv(self):
        result = self.data/4.0
        for i in range(5):
            self.assertEqual(result.y[i], 0.5)
            self.assertEqual(result.dy[i], 0.125)
            
        result = 6.0/self.data
        for i in range(5):
            self.assertEqual(result.y[i], 3.0)
            self.assertEqual(result.dy[i], 6.0*0.5/4.0)
            

if __name__ == '__main__':
    unittest.main()
   