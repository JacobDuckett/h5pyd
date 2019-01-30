##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

import numpy as np
import math
import logging

import config

if config.get("use_h5py"):
    import h5py
else:
    import h5pyd as h5py

from common import ut, TestCase


class TestTable(TestCase):
    def test_create_table(self):
        filename = self.getFileName("create_table_dset")
        print("filename:", filename)
        if config.get("use_h5py"):
            return # Table not supported with h5py
        f = h5py.File(filename, "w")
        if not f.id.id.startswith("g-"):
            return # append not supported with h5serv
        
        count = 10

        dt = np.dtype([('real', np.float), ('img', np.float)])
        table = f.create_table('complex', numrows=10, dtype=dt)

        elem = table[0]
        for i in range(count):
            theta = (4.0 * math.pi)*(float(i)/float(count))
            elem['real'] = math.cos(theta)
            elem['img'] = math.sin(theta)
            table[i] = elem

        self.assertEqual(table.colnames, ['real', 'img'])
        self.assertEqual(table.nrows, count)
        for row in table:
            self.assertEqual(len(row), 2)
        arr = table.read(start=5, stop=6)
        self.assertEqual(arr.shape, (1,))

            
        f.close()

    def test_query_table(self):
        filename = self.getFileName("query_compound_dset")
        print("filename:", filename)
        if config.get("use_h5py"):
            return # Table not supported with h5py
        f = h5py.File(filename, "w")

        if not f.id.id.startswith("g-"):
            return # append not supported with h5serv
        
        # write entire array
        data = [
            ("EBAY", "20170102", 3023, 3088),
            ("AAPL", "20170102", 3054, 2933),
            ("AMZN", "20170102", 2973, 3011),
            ("EBAY", "20170103", 3042, 3128),
            ("AAPL", "20170103", 3182, 3034),
            ("AMZN", "20170103", 3021, 2788),
            ("EBAY", "20170104", 2798, 2876),
            ("AAPL", "20170104", 2834, 2867),
            ("AMZN", "20170104", 2891, 2978),
            ("EBAY", "20170105", 2973, 2962),
            ("AAPL", "20170105", 2934, 3010),
            ("AMZN", "20170105", 3018, 3086)
        ] 
         
        dt = np.dtype([('symbol', 'S4'), ('date', 'S8'), ('open', 'i4'), ('close', 'i4')])
        table = f.create_table('stock', dtype=dt)
        
        table.append(data)

        self.assertEqual(table.nrows, len(data))

        for indx in range(len(data)):
            row = table[indx]
            item = data[indx]
            for col in range(2,3):
                # first two columns will come back as bytes, not strs
                self.assertEqual(row[col], item[col])
         
        quotes = table.read_where("symbol == b'AAPL'")
        self.assertEqual(len(quotes), 4)
        for i in range(4):
            quote = quotes[i]
            self.assertEqual(quote[0], b'AAPL')
        f.close()



if __name__ == '__main__':
    loglevel = logging.ERROR
    logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
    ut.main()