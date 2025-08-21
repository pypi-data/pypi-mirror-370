"""High level Object-Oriented interface methods for the CDFWriter package."""

__author__ = "Joey Mukherjee <joey@swri.org>"

import os
import random
import datetime
from collections import OrderedDict
from collections.abc import Sequence

import numpy as np
from spacepy import pycdf


class CDFWriter(object):
    """
    A class used to hold information that is needed in order to create
    a common set of CDF files that are similar.

    This class uses spacepy.pycdf to generate the CDFs.

    There are 2 kinds of variables that can be defined:
    1) plot - integer or real numbers that are plottable
    2) support - integer or real "attached" variables (e.g. constants)

    For this class, the name of the time variable is assumed to be
    "epoch".

    Attributes
    ----------
    _prefix : str
        A string added at the beginning of the filename for every CDF
        file generated
    _output_directory : str
        The name of the directory in which the CDF file is to placed

        If the directory does not already exists, it will be created.
    _cdf_temp_name : str
        A temporary CDF filename used as the CDF file is being created
    _cdf : Python object representing a CDF file
        The handle to the CDF file being created
    _last_cdf_filenames : list
        The name of the last CDF files created
    _file_naming_convention : str
        The time range string as default for naming files (default: "%Y%m%d%H%M00")
    _version : str
        The version number of the CDF file created
    _merge_if_exists : Boolean
        Flag which specifies if the CDF file is to merge data if we try to write over it
    _do_not_split : Boolean
        Flag which specifies if the CDF file is to be split on a time boundary
    _boundary = datetime.timedelta
        Time interval at which the CDF file is to be split
    _variables : dictionary
        The variables defined for the CDF file
    _constants : dictionary
        The constants defined for the CDF file
    _global_attrs : dictionary
        The global attributes defined for the CDF file
    _variable_attrs : dictionary
        The attributes associated with the variables defined for the CDF file
    _first_time : CDF epoch data type
        The time associated with the first record in the CDF file
    _last_time : CDF epoch data type
        The time associated with the last record in the CDF file
    _data : dictionary
        The data associated with the plot variables defined for the CDF file
    _constant_data : dictionary
        The data associated with the constants defined for the CDF file
    """

    def __init__(self, prefix, outputdir='./'):
        """
        Create CDF files with a "common" look.

        Parameters
        ----------
        prefix : str
            String prefix which is prepended to every CDF file generated.
        outputdir : str, optional
            The location where the CDF file is to be placed (default is the current directory).
        """

        self._prefix = prefix

        pycdf.lib.set_backward(False)
        if not outputdir.endswith(('/', '\\')):
            outputdir += '/'
        self._output_directory = outputdir

        # Make sure directory exists or pycdf creates error

        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)

        self._cdf_temp_name = outputdir + '__tmp' + str(os.getpid()) + '_' \
                              + str(random.randint(1, 65535)) + '.cdf'
        self._cdf = pycdf.CDF(self._cdf_temp_name, '')
        self._last_cdf_filenames = []
        self._version = "0.0.0"
        self._file_naming_convention = "%Y%m%d%H%M00"
        self._do_not_split = True
        self._merge_if_exists = False
        self._boundary = datetime.timedelta(hours=6)
        self._generation_date_format="%Y%m%d"

        self._variables = []
        self._constants = []
        self._global_attrs = OrderedDict()
        self._variable_attrs = {}

        self._first_time = None
        self._last_time = None
        self._data = {}
        self._constant_data = {}
        self._timing_variable_name = 'epoch'

    def __repr__(self):
        """Define the string representation of the CDFWriter class object.

        Parameters
        ----------
        No parameters defined.

        Returns
        -------
        str
            The string representation of the key-value pairs of the CDFWriter
            attributes.
        """

        values = {k: repr(v) for (k, v) in self.__dict__.items()}

        return ('CDFWriter(name={_name}, prefix={_prefix}, \
                 outputdir={_outputdir})').format(**values)

    def __iter__(self):
        """Define the iterator for the CDFWriter class object.

        Parameters
        ----------
        No parameters defined.

        Returns
        -------
        iterator
            The CDFWriter custom iterator object
        """

        # OLD_WAY return iter([('name', self._name), ('prefix', self._prefix), \
        return iter([('prefix', self._prefix), ('version', self._version), \
                     ('outputdir', self._output_directory)])

    def __getitem__ (self, key):
        return self._data [key]

    def __setitem__ (self, key, data):
        self._data [key] = data

    # Add an attributes which is global in nature (i.e. covers entire CDF file)
    def add_global_attribute(self, name, value):
        """Define an attribute to be added to the global part of the CDF file.

        Parameters
        ----------
        name : str
            The string identifier for the global attribute.
        value : CDF_Data_Type
            The value to be assigned to the attribute being defined.

            CDF_Data_Type refers to the list of data types supported by CDF
            and used in pycdf.

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        """

        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')

        self._global_attrs[name] = value

    # Add an attribute which is tied to a single variable (plot or support)
    def add_variable_attribute(self, attribute_name, variable_name, value):
        """Define an attribute to be added to a variable in the CDF file.

        Parameters
        ----------
        attribute_name : str
            The string identifier for the variable attribute.
        variable_name : str
            The string identifier for the variable.
        value : CDF_Data_Type
            The value to be assigned to the variable attribute.

            CDF_Data_Type refers to the list of data types supported by CDF
            and used in pycdf.
        """

        # Before we store the value of the attribute, make sure this
        # variable has a place within the dictionary of variables with
        # attributes.

        if variable_name not in self._variable_attrs:
            self._variable_attrs[variable_name] = OrderedDict()
        self._variable_attrs[variable_name][attribute_name] = value

    # Add a variable to the CDF
    def add_variable(self, name, data_type, sizes=None,
                     dim_variances=None, variance=True, num_elements=1,
                     compression=pycdf.const.GZIP_COMPRESSION,
                     compression_param=6, sparse=False):
        """Define a variable to be included in the CDF file.

        pycdf.const refers to the list of constants supported by CDF
        when specifying a CDF data type for a variable.

        Parameters
        ----------
        name : str
            The string identifier for the variable.
        data_type : pycdf.const
            The data type of the variable.
        sizes : int, optional
            A python list which holds the size of each dimension defined
            for the constant.  The size must be greater than zero
            (default is None).
        dim_variances : pycdf.const, optional
            A python list which holds the dimension variance for each
            dimension defined for the variable (default is None).
        variance : Boolean, optional
            The record variance defined for the variable (default is True).
        num_elements : int, optional
            The number of elements of the data type for the variable
            (default is 1).
        compression : pycdf.const, optional
            The type of compression for the variable
            (default is pycdf.const.GZIP_COMPRESSION).
        compression_param : pycdf.const or int, optional
            The parameter value associated with the type of compression
            selected for the variable (default is 5).
        sparse: Boolean, optional
            Whether or not to set the sparse flag of the variable

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        """

        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')

        self._variables.append(
            {
                'name': name,
                'dataType': data_type,
                'sizes': sizes,
                'dimVariances': dim_variances,
                'variance': variance,
                'num_elements': num_elements,
                'compression': compression,
                'compression_param': compression_param,
                'sparse': sparse,
            }
        )

    # Add data to an already defined variable to the CDF
    # There are competing interests:
    # [NOTE: 1 cdf record and ALL cdf records are handled. Partial set of cdf
    #       records NOT handled. We may not want to handle partial sets.
    # ]
    #   1) input variable may be scalar or array
    #   2) array may contain 1 cdf record [or many cdf records] or all cdf records.
    #      As an example, epoch is either a single, scalar value = 1 cdf record or
    #                     an array of single, scalar values = many cdf records.
    #                     These many records [can be a partial set of epochs or]
    #                     will represent all epochs.
    #                     Counts_per_accum is a vector = 1 cdf record or
    #                     an array of vectors = many cdf records.
    #
    # If input is scalar, then can set [variable_name] = data or [data]
    #                     and can append data or [data]
    # If input is array:
    #   For new variable_name: if array is 1 cdf record: must set = [data]
    #                          if array is many cdf records: set = data
    #                                                       but can set = [data]
    #                          [if array is partial set, set = [data]]
    #   For old variable: if array is 1 cdf record: append ( ,[data], axis=0)
    #                     if array is many cdf records, append ( ,data, axis=0)
    #                     [if array is partial set, append [data]]

    def add_variable_data(self, variable_name, data, all_values=False):
        """Add data to the specified variable defined in the CDF file.

        Parameters
        ----------
        variable_name : str
            The name of the variable to which data is being added -
            case sensitive.
        data : CDF_Data_Type
            The data to be added to the constant variable.

            CDF_Data_Type refers to the list of data types supported by CDF
            and used in pycdf.
        all_values : Boolean, optional
            A flag which tells if the data contains values for all
            CDF records (default is False).

            True means data contains values for all CDF records.
            False means data contains values for a single CDF record.

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        ValueError
            If the variable name has not been previously defined
            (a call to add_variable() has not been made)
        """

        # for a variable called epoch (assume this is the name of the time variable!)

        if not isinstance(variable_name, str):
            raise TypeError('variable_name parameter must be a str')
        if not isinstance(all_values, bool):
            raise TypeError('all_values parameter must be a bool')

        # Make sure variable has already been defined before we try to
        # add the data.

        list_of_all_variables = []
        defined_variables = self._variables

        for variable in defined_variables:
            list_of_all_variables.append(variable['name'])

        if variable_name not in list_of_all_variables:
            raise ValueError('variable_name {0} must be one of {valids}'.format(
                variable_name, valids=repr(list_of_all_variables)))

        if variable_name == self._timing_variable_name:
            if not isinstance(data, (Sequence, np.ndarray)):
                times = [data]
            else:
                times = data
            if self._first_time is None:
                self._first_time = times[0]
            self._last_time = times[-1]

        if all_values:
            assert variable_name not in self._data
            self._data[variable_name] = data
        else:
            if variable_name not in self._data:
                self._data[variable_name] = [data]
            else:
                self._data[variable_name].append(data)

    # Add a constant to the CDF
    def add_constant(self, name, data_type, sizes):
        """Define a constant to be included in the CDF file.

        Parameters
        ----------
        name : str
            The string identifier for the constant.
        data_type : pycdf.const
            The data type of the constant.

            pycdf.const refers to the list of constants supported by CDF
            when specifying a CDF data type for a variable.
        sizes : int
            A python list which holds the size of each dimension defined for
            the constant.  Each size must be greater than zero (0).

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        """

        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')

        self._constants.append({'name': name, 'dataType': data_type, 'sizes': sizes})

    # Add data to an already defined constant to the CDF
    def add_constant_data(self, constant_name, data):
        """Add data to the specified constant defined in the CDF file.

        Parameters
        ----------
        constant_name : str
            The name of the constant variable to which data is being added -
            case sensitive.
        data : CDF_Data_Type
            The data to be added to the constant variable.

            CDF_Data_Type refers to the list of data types supported by CDF
            and used in pycdf.

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        ValueError
            If the constant variable named has not been previously defined
            (a call to add_constant() has not been made)
        """

        if not isinstance(constant_name, str):
            raise TypeError('constant_name parameter must be a str')

        # Make sure constant have already been defined before we try to
        # add the data.

        list_of_all_constants = []
        defined_constants = self._constants

        for constant in defined_constants:
            list_of_all_constants.append(constant['name'])

        if constant_name not in list_of_all_constants:
            raise ValueError('constant_name {0} must be one of {valids}'.format(
                constant_name, valids=repr(list_of_all_constants)))

        # First time data being added?

        if constant_name not in self._constant_data:
            self._constant_data[constant_name] = [data]
        else:
            self._constant_data[constant_name].append(data)

    def _write_data(self):
        """Write the data to the CDF file.

        Parameters
        ----------
        No parameters defined.
        """

        # Transfer the global attributes defined.

        for name, value in self._global_attrs.items():
            self._cdf.attrs[name] = value

        # Transfer the constants defined.

        for constant in self._constants:
            if constant ['dataType'] == pycdf.const.CDF_CHAR:
                n_elems = len(max(self._constant_data[constant['name']][0], key=len))
            else:
                n_elems = 1

            self._cdf.new(
                constant['name'],
                type=constant['dataType'],
                n_elements=n_elems,
                dims=constant['sizes'],
                dimVarys=None,
                recVary=False,
                compress=pycdf.const.NO_COMPRESSION
            )
            if constant['name'] in self._variable_attrs:
                for name, value in self._variable_attrs[constant['name']].items():
                    if value is not None:
                       self._cdf[constant['name']].attrs[name] = value
                    else:
                       print (f"{name} has no value set for constant {constant['name']}!")
            if constant['name'] in self._constant_data:
                self._cdf[constant['name']] = self._constant_data[constant['name']][0]

        # Transfer the variables defined.

        for variable in self._variables:
            try:

# We noticed an issue where when if we cloned our variable, the size was not being saved!
# This should fix it

                if variable ['dataType'] == pycdf.const.CDF_CHAR.value:
                    n_elems = len(max(self._data[variable['name']])) + 1  # have to add 1 for some reason
                    self._cdf.new(
                        variable['name'],
                        type=variable['dataType'],
                        n_elements=n_elems,
                        dims=variable['sizes'],
                        dimVarys=variable['dimVariances'],
                        recVary=variable['variance'],
                        compress=variable['compression'],
                        compress_param=variable['compression_param'],
                        sparse=variable ['sparse']
                    )
                else:
                    if variable ['name'] == self._timing_variable_name:
                        self._cdf.new(
                            variable['name'],
                            type=variable['dataType'],
                            dims=variable['sizes'],
                            dimVarys=variable['dimVariances'],
                            recVary=variable['variance'],
                            compress=pycdf.const.NO_COMPRESSION,
                            compress_param=None,
                            sparse=variable ['sparse']
                        )
                    else:
                        self._cdf.new(
                            variable['name'],
                            type=variable['dataType'],
                            dims=variable['sizes'],
                            dimVarys=variable['dimVariances'],
                            recVary=variable['variance'],
                            compress=variable['compression'],
                            compress_param=variable['compression_param'],
                            sparse=variable ['sparse']
                        )
            except Exception as err:
                print("Can't add", variable['name'], "to CDF - already exists", err)
            if variable['name'] in self._variable_attrs:
                for name, value in self._variable_attrs[variable['name']].items():
                    if value is not None:
                       try:
                           self._cdf[variable['name']].attrs[name] = value
                       except ValueError as err_str:
                           print("Can't add attribute", value, "to attribute", \
                                 name, "on", variable['name'], err_str)
            if variable['name'] in self._data:
                try:
                    self._cdf[variable['name']] = self._data[variable['name']]
                except ValueError as err_str:
                    print("Can't add", self._data[variable['name']], \
                          "to variable", variable['name'], err_str)

    def clone_variable(self, zvar, name=None, clone_data=False, new_type=None,
                       new_attrs=None):
        """Define a new variable which is copied from the named input variable.

        Parameters
        ----------
        zvar : pycdf.Var
            The name of the variable to copy from (clone) for the new variable being defined.

            pycdf.Var refers a class which defines CDF variables of the type zVariable.
        name : str, optional
            The string identifier for the new variable being defined
            (default is None so the name value is cloned).
        clone_data : Boolean, optional
            A flag which tells if the data from the named variable (zvar) is to
            be copied to the new variable being defined (default is False).
        new_type : pycdf.const, optional
            The data type of the new variable being defined
            (default is None so the data type value is cloned).

            pycdf.const refers to the list of constants supported by CDF
            when specifying a CDF data type for a variable.
        new_attrs : CDF_Data_Type, optional
            The list of attributes to be defined for the new variable,
            overwriting any of the attributes cloned from the named variable
            zvar (default is None so that no additional attributes are defined).
        """

        if name is None:
            name = zvar.name()
        if new_type is None:
            new_type = zvar.type()

        # This is a mutable value so what really happens is that this "default"
        # list gets created as a persistent object, and every invocation of
        # this method that doesn't specify a new_attrs param will be using
        # that same list object any changes to it will persist and be carried
        # to every other invocation! That is why code is now written this way.

        if new_attrs is None:
            new_attrs = []

        self._variables.append(
            {
                'name': name,
                'dataType': new_type,
                'sizes': zvar._dim_sizes(),
                'dimVariances': zvar.dv(),
                'variance': zvar.rv(),
                'num_elements': zvar.nelems(),
                'compression': zvar.compress()[0],
                'compression_param': zvar.compress()[1],
                'sparse': zvar.sparse (),
            }
        )
        self._variable_attrs[name] = OrderedDict()
        attrs = zvar.attrs.items ()
        for k, val in attrs:
            self._variable_attrs[name][k] = val
        for k, val in new_attrs:  # overwrite any new ones
            self._variable_attrs[name][k] = val

        if clone_data:
            self._data[name] = zvar[...]
            if name == self._timing_variable_name:
               if self._first_time is None:
                  self._first_time = zvar[0]
               self._last_time = zvar[-1]


    def close(self):
        """Close the CDF file currently being processed.

        If data for any of the variables within the CDF was added,
        the CDF file is moved to the output directory specified.

        Parameters
        ----------
        No parameters defined.
        """

        self.add_global_attribute(
            'Generation_date', datetime.datetime.now().strftime(self._generation_date_format)
        )
        self.add_global_attribute('Data_version', "v" + self._version)
        self.add_global_attribute('Logical_source', self._prefix)

        if self._first_time is not None:
            new_filename = self._prefix + '_' \
                           + self._first_time.strftime(self._file_naming_convention) \
                           + '_v' + self._version + '.cdf'
            self.add_global_attribute('Logical_file_id', self._prefix + '_' \
                                    + self._first_time.strftime(self._file_naming_convention))
        else:
            new_filename = self._prefix + '_v' + self._version + '.cdf'

        if self._data:
            self._write_data()

        self._cdf.close()

        full_path_final_cdf = self._output_directory + new_filename
        # Moves the CDF file from the temporary to the permanent location
        # with the correct filename.

        if os.path.exists(full_path_final_cdf):
           if self._merge_if_exists:
              cdf_old = pycdf.CDF(full_path_final_cdf)
              cdf_new = pycdf.CDF(self._cdf_temp_name)
              cdf_new.readonly(False)
              if self._data:
                 epochs_combined = np.concatenate ((cdf_old [self._timing_variable_name], self._data[self._timing_variable_name]), axis=0)
                 sorted_epochs_combined = np.argsort (epochs_combined, axis=0)
                 for variable in self._variables:
                     # TODO - we need to merge this data in...
                     if variable['name'] in self._data:
                         try:
                             data_combined = np.concatenate ((cdf_old [variable['name']], self._data[variable['name']]), axis=0)
                             cdf_new [variable['name']] = data_combined [sorted_epochs_combined]
                         except ValueError as err_str:
                             print("Can't add data ", self._data[variable['name']], \
                                   "to variable", variable['name'], err_str)
              cdf_old.close()
              cdf_new.close()
           else:
              raise RuntimeError(full_path_final_cdf, 'already exists!')

        os.rename(self._cdf_temp_name, full_path_final_cdf)
        if not self._data:
            os.unlink(full_path_final_cdf)
        else:
            self._last_cdf_filenames.append (new_filename)

        self._data = {}
        self._first_time = None
        self._last_time = None

    def make_new_file(self):
        """Create a new CDF file.

        If there is a CDF file already being processed, close that CDF file.

        Parameters
        ----------
        No parameters defined.
        """

        self.close()

        self._cdf_temp_name = self._output_directory + '__tmp' \
                              + str(os.getpid()) + '_' \
                              + str(random.randint(1, 65535)) + '.cdf'
        self._cdf = pycdf.CDF(self._cdf_temp_name, '')

    # Close the CDF record and start a new record
    def close_record(self):
        """Close the current CDF record and start a new CDF record.

        If the CDF file is to be split at a pre-defined time boundary,
        then the current CDF file is closed and a new CDF file
        is created before a new CDF record commences if the file
        boundary condition is met.

        Parameters
        ----------
        No parameters defined.
        """

        ret_val = False
        if self._do_not_split:
            return ret_val
        if self._boundary > datetime.timedelta (hours = 23):
           if self._last_time.date () > self._first_time.date ():
              last_time = self._last_time
              self.make_new_file()
              ret_val = True
              self._first_time = last_time
              self._last_time = last_time
        if self._last_time - self._first_time >= self._boundary:
            self.make_new_file()
            ret_val = True

        return ret_val

    def set_file_naming_convention(self, file_naming_convention):
        """Set the file naming convention for the time string on the end.

        Currently, this is "%Y%m%d%H%M00", and only can use the start time.

        Parameters
        ----------
        file_naming_convention : str
            The file naming convention based on the start time.  The default is "%Y%m%d%H%M00".
        """
        if not isinstance(file_naming_convention, str):
            raise TypeError('file_naming_convention parameter must be a string')

        self._file_naming_convention = file_naming_convention

    def set_generation_date_format (self, date_format):
        if not isinstance(date_format, str):
            raise TypeError('generation_date_format parameter must be a string')

        self._generation_date_format = date_format
        
    # Set the version number of this CDF
    def set_version_number(self, version):
        """Set the version number for the CDF generated.

        The value is initially set to 0.0.0 by the class constructor

        Parameters
        ----------
        version : str
            The version number for the CDF produced in the format
            n.n.n, where n represents a number.

            For example, 4.2.0 is a valid value.

        Raises
        ------
        TypeError
            If the version argument is not of the correct type.
        ValueError
            If the version argument is not in the format n.n.n (e.g. 4.2.0).
        """

        if not isinstance(version, str):
            raise TypeError('version parameter must be a string')

        # Split the version parameter into separate components.

        version_numbers_list = version.split('.')
        num_levels = len(version_numbers_list)
        if num_levels != 3:
            raise ValueError('version should have 3 levels (e.g. 4.2.0)')

        # Make sure each component represents a digit since we only use
        # numbers for the version.

        for j in range(num_levels):
            vpart = version_numbers_list[j]
            good_val = vpart.isdigit()
            if not good_val:
                # print 'ERROR: ' + vpart + ' is invalid - must be an int.'
                raise TypeError('each level must consist only of integers')

        self._version = version

    # Set the directory to write the CDFs
    def set_output_directory(self, output_directory):
        """Set the directory into which the CDF files are to be written.

        If this method is not called, the CDF files are written in the directory
        specified when the class is instantiated.

        Parameters
        ----------
        output_directory : str
            The name of the directory where the CDF files are to be placed.

            If the directory does not already exists, it will be created.

        Raises
        ------
        TypeError
            If the output_directory argument is not of the correct type.
        """

        if not isinstance(output_directory, str):
            raise TypeError('output_directory parameter must be a string')

        if not output_directory.endswith(('/', '\\')):
            output_directory += '/'
        self._output_directory = output_directory

        # Make sure directory exists or pycdf creates error

        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)

    def set_timing_variable_name(self, timing_variable_name):
    # Set this to the name of the timing variable, usually "epoch"
        if not isinstance(timing_variable_name, str):
            raise TypeError('timing_variable_name parameter must be a str')

        self._timing_variable_name = timing_variable_name

    def set_merge_if_exists(self, merge_if_exists):
    # Set this to true to never split the file based on six hours
        if not isinstance(merge_if_exists, bool):
            raise TypeError('merge_if_exists parameter must be a bool')

        self._merge_if_exists = merge_if_exists

    def set_do_not_split(self, do_not_split,
                         boundary=datetime.timedelta(hours=6)):
        """Determines if CDF files are to be split on a pre-defined boundary.

        The default, as set by the class constructor, generates a single CDF file.

        Parameters
        ----------
        do_not_split : Boolean
            A flag which defines whether or not the CDF file(s) generated are
            to be split on a pre-defined time boundary (default is 6 hours).

            True means never split the file - one single CDF file is generated.
            False means automatically split the CDF file at the pre-defined
            time boundaries.

        boundary : datetime.timedelta, optional
            The time interval at which the CDF file is to be split into
            multiple files (default = 6 hours).

        Raises
        ------
        TypeError
            If one of the arguments is not of the correct type.
        """

        if not isinstance(do_not_split, bool):
            raise TypeError('do_not_split parameter must be a bool')
        if not isinstance(boundary, datetime.timedelta):
            raise TypeError('boundary parameter must be a datetime.timedelta value')

        self._do_not_split = do_not_split
        self._boundary = boundary

    # Will return the names of the last CDF files created
    # NOTE: this will return [] if no CDF files have been written yet
    def get_last_cdf_filenames(self):
        """Return the name of the last CDF file produced.

        Parameters
        ----------
        No parameters defined.

        Returns
        -------
        str
            The name of the last CDF file created (keyword None if no CDF)
        """

        return self._last_cdf_filenames

# -------------------------------------------------------------------------------
    def add_support_variable_attributes(self, variable_name,
                                        short_description='',
                                        long_description='', units_string=' ',
                                        format_string='', validmin=None,
                                        validmax=None, lablaxis=' ',
                                        si_conversion=' > ', scale_type='linear',
                                        add_fill=False, fill_val=None, other_attrs={}):
        """Define required attributes for a support variable in the CDF file.

        These required attributes include FIELDNAM, VALIDMIN, VALIDMAX,
                                 LABLAXIS, UNITS, FORMAT, CATDESC,
                                 VAR_TYPE and SI_CONVERSION.

        VAR_TYPE is defaulted to "support_data".

        Parameters
        ----------
        variable_name : str
            The string identifier for the variable.
        short_description : str, optional
            The string which describes the variable (default is empty string).
        long_description : str, optional
            A catalog description of the variable (default is empty string).
        units_string : str, optional
            A string representing the units of the variable,
            e.g., nT for magnetic field (default is ' ').

            Use a blank character, rather than "None" or "unitless",
            for variables that have no units (e.g., a ratio).
        format_string : str, optional
            The output format used when extracting data values (default is empty string).

            The magnitude and the number of significant figures needed
            should be carefully considered, with respect to the values
            of validmin and validmax parameters.
        validmin : pycdf.const, optional
            The minimum value for the variable that are expected over the
            lifetime of a mission (default is None).

            The value must match variable's data type.
        validmax : pycdf.const, optional
            The maximum value for the variable that are expected over the
            lifetime of a mission (default is None).

            The value must match variable's data type.
        lablaxis : str, optional
            A short string which can be used to label a y-axis for a plot
            or to provide a heading for a data listing (default is " ").
        si_conversion : str, optional
            A string which defines the conversion factor that the variable
            must be multiplied by in order to turn it to generic SI units
            (default is " > ").

            The string must contain 2 text fields separated by the delimiter >.
        scale_type : str, optional
            A string which indicates whether the variable should have a linear
            or a log scale (default is 'linear').
        """

        self.add_variable_attribute("FIELDNAM", variable_name, short_description)
        self.add_variable_attribute("VALIDMIN", variable_name, validmin)
        self.add_variable_attribute("VALIDMAX", variable_name, validmax)
        if len(units_string) == 0:
            units_string = 'unitless'
        self.add_variable_attribute("UNITS", variable_name, units_string)
        self.add_variable_attribute("FORMAT", variable_name, format_string)
        self.add_variable_attribute("CATDESC", variable_name, long_description)
        self.add_variable_attribute("VAR_TYPE", variable_name, "support_data")
        self.add_variable_attribute("SI_CONVERSION", variable_name, si_conversion)
        self.add_variable_attribute("LABLAXIS", variable_name, lablaxis)
        self.add_variable_attribute("SCALETYP", variable_name, scale_type)
        if add_fill and fill_val is None:
           if data_type == pycdf.const.CDF_DOUBLE:
               self.add_variable_attribute("FILLVAL", variable_name, 1.0e31)
           elif data_type == pycdf.const.CDF_FLOAT:
               self.add_variable_attribute("FILLVAL", variable_name, 1.0e31)
           elif data_type == pycdf.const.CDF_UINT1:
               self.add_variable_attribute("FILLVAL", variable_name, 255)
           elif data_type == pycdf.const.CDF_UINT2:
               self.add_variable_attribute("FILLVAL", variable_name, 65535)
           elif data_type == pycdf.const.CDF_INT4:
               self.add_variable_attribute("FILLVAL", variable_name, 1)
           elif data_type == pycdf.const.CDF_UINT4:
               self.add_variable_attribute("FILLVAL", variable_name, 4294967294)
           else:
               valid_data_types = ('CDF_DOUBLE', 'CDF_FLOAT', 'CDF_UINT1', \
                                   'CDF_UINT2', 'CDF_INT4', 'CDF_UINT4')
               print('For {0} data_type must be one of {valids}'.format(
                   variable_name, valids=repr(valid_data_types)))
               os.abort()
        elif fill_val is not None:
           self.add_variable_attribute("FILLVAL", variable_name, fill_val)
        for k, v in other_attrs.items ():
           self.add_variable_attribute(k.upper (), variable_name, v)

# -----------------------------------------------------------------------------------------
    def add_plot_variable_attributes(self, variable_name, short_description='',
                                     long_description='', display_type='',
                                     units_string=' ', format_string='',
                                     lablaxis='', data_type=None, validmin=None,
                                     validmax=None, scale_type='linear',
                                     add_fill=True, fill_val=None, other_attrs={}):
        """Define required attributes for a plot variable in the CDF file.

        These required attributes include FIELDNAM, VALIDMIN, VALIDMAX,
                                LABLAXIS, FILLVAL, SCALETYP, UNITS, FORMAT,
                                CATDESC, VAR_TYPE, DISPLAY_TYPE, SI_CONVERSION,
                                DEPEND_0, and COORDINATE_SYSTEM.

        FILLVAL is defaulted based upon the data_type value specified.
        VAR_TYPE is defaulted to "data".
        SI_CONVERSION is defaulted to " > ".
        DEPEND_0 is defaulted to "epoch".
        COORDINATE_SYSTEM is defaulted to "BCS".

        Parameters
        ----------
        variable_name : str
            The string identifier for the variable.
        short_description : str, optional
            The string which describes the variable (default is empty string).
        long_description : str, optional
            A catalog description of the variable (default is empty string).
        display_type : str, optional
            A string which tells automated software what type of plot to make
            (default is empty string).

            Examples include time_series, spectrogram, stack_plot, image.
        units_string : str, optional
            A string representing the units of the variable,
            e.g., nT for magnetic field (default is ' ').

            Use a blank character, rather than "None" or "unitless", for
            variables that have no units (e.g., a ratio or a direction cosine).
        format_string : str, optional
            The output format used when extracting data values
            (default is empty string).

            The magnitude and the number of significant figures needed should
            be carefully considered, with respect to the values of validmin
            and validmax parameters.
        lablaxis : str, optional
            A short string which can be used to label a y-axis for a plot
            or to provide a heading for a data listing (default is empty string).
        data_type : pycdf.const, optional
            The data type of the variable (default is None).

            If the add_fill flag is set to True, then the data_type parameter
            must be specified; otherwise, an abort is issued by the code.
        validmin : pycdf.const, optional
            The minimum value for the variable that are expected over the
            lifetime of a mission (default is None).

            The value must match data_type value specified.
        validmax : pycdf.const, optional
            The maximum value for the variable that are expected over the
            lifetime of a mission (default is None).

            The value must match data_type value specified.
        scale_type : str, optional
            A string which indicates whether the variable should have a linear
            or a log scale (default is 'linear').
        add_fill : Boolean, optional
            A flag to indicate if the FILLVAL attribute is to be set
            (default is True).
        fill_val: pycdf.const, optional
            The fill value defined.

            FILLVAL is the number inserted in the CDF in place of data values
            that are known to be bad or missing.  The value used is dependent
            upon the data_type value specified and should match the data type
            of the variable.
        """

        self.add_variable_attribute("FIELDNAM", variable_name, short_description)
        self.add_variable_attribute("VALIDMIN", variable_name, validmin)
        self.add_variable_attribute("VALIDMAX", variable_name, validmax)
        self.add_variable_attribute("LABLAXIS", variable_name, lablaxis)
        if add_fill and fill_val is None:
            if data_type == pycdf.const.CDF_DOUBLE:
                self.add_variable_attribute("FILLVAL", variable_name, 1.0e31)
            elif data_type == pycdf.const.CDF_FLOAT:
                self.add_variable_attribute("FILLVAL", variable_name, 1.0e31)
            elif data_type == pycdf.const.CDF_UINT1:
                self.add_variable_attribute("FILLVAL", variable_name, 255)
            elif data_type == pycdf.const.CDF_UINT2:
                self.add_variable_attribute("FILLVAL", variable_name, 65535)
            elif data_type == pycdf.const.CDF_INT4:
                self.add_variable_attribute("FILLVAL", variable_name, 1)
            elif data_type == pycdf.const.CDF_UINT4:
                self.add_variable_attribute("FILLVAL", variable_name, 4294967294)
            else:
                valid_data_types = ('CDF_DOUBLE', 'CDF_FLOAT', 'CDF_UINT1', \
                                    'CDF_UINT2', 'CDF_INT4', 'CDF_UINT4')
                print('For {0} data_type must be one of {valids}'.format(
                    variable_name, valids=repr(valid_data_types)))
                os.abort()
        elif fill_val is not None:
            self.add_variable_attribute("FILLVAL", variable_name, fill_val)
        self.add_variable_attribute("SCALETYP", variable_name, scale_type)
        self.add_variable_attribute("UNITS", variable_name, units_string)
        self.add_variable_attribute("FORMAT", variable_name, format_string)
        self.add_variable_attribute("CATDESC", variable_name, long_description)
        self.add_variable_attribute("VAR_TYPE", variable_name, "data")
        self.add_variable_attribute("DISPLAY_TYPE", variable_name, display_type)
        self.add_variable_attribute("SI_CONVERSION", variable_name, " > ")
        self.add_variable_attribute("DEPEND_0", variable_name, self._timing_variable_name)
        self.add_variable_attribute("COORDINATE_SYSTEM", variable_name, "BCS")
        for k, v in other_attrs.items ():
           self.add_variable_attribute(k.upper (), variable_name, v)
