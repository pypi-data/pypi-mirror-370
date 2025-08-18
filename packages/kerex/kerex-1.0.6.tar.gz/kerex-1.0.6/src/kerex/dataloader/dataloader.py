import tensorflow as tf
import numpy as np
import json
from pathlib import Path
import warnings
from string import ascii_lowercase


class TFRecordsHandlerBase:
    """
    Base dataloader class for TFRecord files

    This base class can be subclassed to easily generate input pipelines for ML 
    based on [`tf.data.Dataset`](https://www.tensorflow.org/api_docs/python/tf/data/Dataset).

    This base class can
    - automatically write numpy arrays to tfrecord files,
    - generate a basic `tf.data.Dataset` from a list of tfrecord files
    
    Parameters
    ----------
    path : str | Path, otptional
        Path to where TFRecord files (and metadata.json) are stored.

    Examples
    --------
    Let's write some arbitrary data (`x` and `y`) to `data.tfrecords`. `x` is of type `float32`, `y` is of type `int16`.
    >>> import numpy as np
    >>> x = np.arange(32).reshape(4, 8).astype(np.float32)
    >>> y = np.array([1, 0, 0, 1]).astype(np.int16)
    >>> dataloader = TFRecordsHandlerBase(path=".")
    >>> dataloader.setup(x=x, y=y)
    >>> dataloader.metadata
    {'x': {'dtype': 'float32', 'shape': (4, 8), 'shape_names': ('a', 'b')}, 'y': {'dtype': 'int16', 'shape': (4,), 'shape_names': ('a',)}}
    >>> dataloader.write_tfrecords(file="data.tfrecords", x=x, y=y)
    >>> dataset = dataloader.get_dataset(files=["data.tfrecords"])
    >>> x_tf, y_tf = next(iter(dataset.take(1)))
    >>> x_tf
    <tf.Tensor: shape=(32,), dtype=float32, numpy=
    array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11., 12.,
        13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25.,
        26., 27., 28., 29., 30., 31.], dtype=float32)>
    >>> y_tf
    <tf.Tensor: shape=(4,), dtype=int16, numpy=array([1, 0, 0, 1], dtype=int16)>

    """

    def __init__(self, path=None):
        if path:
            self.path = Path(path)
            try:
                self.metadata = self.read_metadata()
            except FileNotFoundError:
                pass

        self.valid_dtype = (np.number, np.ndarray)

    def setup(self, **kwargs):
        """
        Initialize dimensions dictionary by passing all features to the setup

        Builds a metadata file from named numpy arrays.
        The metadata.json contains
        - the dtype (e.g., `"float32"`),
        - the shape (e.g., `(5,2)`), and
        - the shape_names (e.g., `(a, b)`)
        for each key (named numpy input file.)

        Parameters
        ----------
        **kwargs : Keyword arguments
            Have to be numpy arrays. The key determines the key in the metadata.json

        Returns
        -------
        metadata : dict
            A dictionary containing essential information about the arrays.

        Raises
        ------
        TypeError
            If not all inputy are numpy arrays.

        Examples
        --------
        >>> dataloader.setup(x=np.ones((5, 2)), y=np.ones((1)))
        >>> dataloader.metadata
        {'x': {'dtype': 'float64', 'shape': (5,2), 'shape_names': ('a','b')}, 'y': {'dtype': 'float64', 'shape': (1,), 'shape_names': ('a',)}}

        """

        if all(isinstance(v, self.valid_dtype) for v in kwargs.values()):
            self.metadata = {
                k: {
                    "dtype": str(v.dtype),
                    "shape": v.shape,
                    "shape_names": tuple([d for _, d in zip(v.shape, ascii_lowercase)])
                    } for k, v in kwargs.items()
                }
        else:
            raise TypeError(f"Unknown data type, received {[type(item) for item in kwargs.values()]}")
        
    @property
    def get_metadata(self):
        """
        Returns the self.metadata

        Returns
        -------
        metadata : dict
            The metadata or "architecture" of the TFRecord files.

        """

        try:
            return self.metadata
        except AttributeError as e:
            warnings.warn("dataloader.metadata is not set yet. Run dataloader.setup() to initialize it", RuntimeWarning)
    
    def write_metadata(self, path=None):
        """
        Write self.metadata to json

        Parameters
        ----------
        path : str | Path, optional
            Path to save metadata.json to.
            If `self.path` is defined, `path` is ignored. Else, `self.path` is set to `path`.
            Defaults to `None`.

        Raises
        ------
        ValueError
            If `path=None` and `self.path` is not set.

        """

        if hasattr(self, "path"):
            path = self.path
        elif path is not None:
            setattr(self, "path", path)
            print(f"Set self.path={self.path}")
        else:
            raise ValueError(f"Please define path when initializing or here, received None.")
        
        with open(Path(self.path, "tfrecord_metadata.json"), "w") as fp:
            json.dump(self.metadata, fp)

    def read_metadata(self):
        """
        Read metadata.json

        Returns
        -------
        metadata : dict
            The metadata (architecture) of the TFRecord files.

        """
        with open(Path(self.path, 'tfrecord_metadata.json'), 'r') as fp:
            metadata = json.load(fp)

        # cast lists to tuples to restore original design of "metadata"
        for v in metadata.values():
            for k_, v_ in v.items():
                if isinstance(v_, list):
                    v.update({k_: tuple(v_)})

        return metadata
    
    def get_dim_keys(self, key: str) -> list:
        """
        Get dimension-names of a `key` in `self.metadata`

        Parameters
        ----------
        key : str
            Key of the entry to obtain the dimension-names from 

        Returns
        -------
        dim : list
            A sorted list with all dimension-names of `key`.

        Raises
        ------
        KeyError
            If key does not exist in `self.metadata`

        """

        try:
            return sorted([f"{key}_{d}" for d in self.metadata[key]["shape_names"]])
        except KeyError as e:
            raise KeyError(f"Key '{key}' does not exist in metadata.") from e
    
    
    def get_dtype(self, key):
        """
        Get dtype of a `key` in `self.metadata`

        Parameters
        ----------
        key : str
            Key of the entry to obtain the dtype from.

        Raises
        ------
        KeyError
            If key does not exist in `self.metadata`

        """

        try:
            return self.metadata[key]["dtype"]
        except KeyError as e:
            raise KeyError(f"Key '{key}' does not exist in metadata.") from e
    
    def _get_data_structure(self, **kwargs) -> dict:
        """
        Returns a dictionary with the structure of the TFRecord file

        Parameters
        ----------
        **kwargs : Additional optional keyword arguments

        Returns
        -------
        d : dict
            A dictionary holding the features and the respective dimensions.
        
        Raises
        ------
        RuntimeError
            If called without any `**kwargs` and `self.metadata` is not set yet.
        TypeError
            If `**kwargs` contains other dtypes than `numpy.ndarray`
        
        Notes
        -----
        This function behaves differently depending on the optional `**kwargs` argument.
        - If `**kwargs` contains `numpy.ndarrays`, the function serializes the features and their dimensions to store them in TFRecords.
        - If no `**kwargs` are defined, the function returns the features and their dimensions to instances of `tf.io.FixedLenFeature`.

        The latter requires the existance of a `self.metadata` dictionary, which defines the architecture of the TFRecord files.

        **This function is called internally, it should not be necessary to call it manually!**

        """
        if not kwargs:
            # """
            # Example usage
            #     return dictionary with keys and tf-specific data types, e.g.,
            #     >>> raw_feature = dict(feature_name=tf.io.FixedLenFeature([], tf.string))
            #     >>> dimensions = dict(x=tf.io.FixedLenFeature([], tf.int64), y=tf.io.FixedLenFeature([], tf.int64))
            #     >>> return {**raw_feature, **dimensions}
            # """
            if not hasattr(self, "metadata"):
                raise RuntimeError(f"'self.metadata' is not yet initialized. Run 'self.setup()' with all features once to set it up.")
            
            features = {k: tf.io.FixedLenFeature([], tf.string) for k in self.metadata.keys()}
            dimensions = {f"{k}_{s}": tf.io.FixedLenFeature([], tf.int64) for k in self.metadata.keys() for s in self.metadata[k]["shape_names"]}
            return {**features, **dimensions}

        if all(isinstance(v, self.valid_dtype) for v in kwargs.values()):
            # """
            # Example usage
            #     >>> serialized_feature = dict(feature_name=self._bytes_feature(tf.io.serialize_tensor(feature)))
            #     >>> dimensions = {k: self._int64_feature(feature.shape[i]) for i, k in enumerate(self.metadata))}
            #     >>> return {**serialied_feature, **dimensions}
            # """
            if not hasattr(self, 'metadata'):
                self.setup(**kwargs)

            features = {k: self._bytes_feature(tf.io.serialize_tensor(v)) for k, v in kwargs.items()}
            dimensions = {f"{k}_{d}": self._int64_feature(v.shape[i]) for k, v in kwargs.items() for i, d in enumerate(self.metadata[k]["shape_names"])}
            return {**features, **dimensions}
        
        raise TypeError(f"Unknown data type.")
        
    def _parse_write(self, **kwargs):
        """
        Writes data in `**kwargs` to `tf.train.Example`.
        
        Parameters
        ----------
        **kwargs : Additional optional keyword arguments
            Has to contain `numpy.ndarrays`.

        Returns
        -------
        y : tf.train.Example
            `x` encoded in TFRecord data format.

        Notes
        -----
        Key names have to resemble the feature names,
        e.g., `x=np.ones((32,))` writes the serialized array `np.ones((32,))` with key `x` to the `tf.train.Example`

        """

        if not kwargs:
            return
        
        if not hasattr(self, "metadata"):
            self.setup(**kwargs)
            
        return tf.train.Example(features=tf.train.Features(feature=self._get_data_structure(**kwargs)))
    
    def _parse_read(self, serialized_data):
        """
        Reads serialized `tf.train.Example` and parses them to `tf.Tensor`.

        Parameters
        ----------
        serialized_data : tf.train.Example
            Serialized data as stored in TFRecord files.

        Returns
        -------
        data : tf.Tensor
            Decoded data from TFRecord files.

        """

        structure = tf.io.parse_single_example(serialized_data, self._get_data_structure())

        if len(self.metadata.keys()) == 1:
            k = list(self.metadata.keys())[0]
            dim_keys = self.get_dim_keys(key=k)
            dtype = self.get_dtype(key=k)

            serialized_data = structure.pop(k)
            shape = tuple([structure.pop(dk) for dk in dim_keys])
            return tf.reshape(tf.io.parse_tensor(serialized_data, out_type=dtype), shape=shape)
        
        features = []
        for k in self.metadata.keys():
            dim_keys = self.get_dim_keys(key=k)
            dtype = self.get_dtype(key=k)

            serialized_data = structure.pop(k)
            shape = tuple([structure.pop(dk) for dk in dim_keys])
            features.append(tf.reshape(tf.io.parse_tensor(serialized_data, out_type=dtype), shape=shape))

        return tuple(features)

    def write_tfrecords(self, file, verbose=True, **kwargs):
        """
        Write an arbitrary amount of `numpy.ndarray` to `file`.
        The file contains a serialized version of the `numpy.ndarray`.

        Parameters
        ----------
        file : str | Path
            Filehandle `(path/to/file.tfrecords)` to where the tfrecord data should be written
        verbose : bool, optional
            If `True` verbosity is enabled.
        **kwargs : Additional optional keywords for `self._parse_write`

        Notes
        -----
        See `Examples` of the class for a MWE on how to use this function.

        """
        
        file = Path(file).absolute()
        if file.exists():
            return
        
        with tf.device("/cpu:0"):
            with tf.io.TFRecordWriter(str(file)) as writer:
                out = self._parse_write(**kwargs)
                writer.write(out.SerializeToString())
            
            if verbose:
                print(f"Successfully written data to {file}")

    def get_dataset(self, files):
        """
        Get a dataset which just decodes TFRecord files

        This method can be overwritten for more complex datasets including excessive data augmentation etc.

        Parameters
        ----------
        files : list
            List of files that form the dataset.

        Returns
        -------
        dataset : tf.data.DatasetV2
            Dataset from `files`.

        Raises
        ------
        RuntimeError
            If files is an empty list.

        """
        files = [str(file) for file in files]

        if files:
            with tf.device("/cpu:0"):
                dataset = tf.data.TFRecordDataset(filenames=files)
                dataset = dataset.map(self._parse_read, num_parallel_calls=tf.data.AUTOTUNE)

                return dataset
            
        raise RuntimeError(f"Empty dataset. Please ensure that `*.tfrecords` exist.")
    
    @staticmethod
    def _bytes_feature(value):
        """
        Returns a `tf.train.BytesList` from a string/byte.

        Parameters
        ----------
        value : tf.Tensor | ndarray
            Data in either tf.Tensor or numpy ndarray.

        Returns
        -------
        feature : tf.train.Feature
            Data encoded as `tf.train.BytesList`.

        """

        if isinstance(value, tf.Tensor):
            value = value.numpy()
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
    
    @staticmethod
    def _float_feature(value):
        """
        Returns a `tf.train.FloatList` from a float / double.
        
        Parameters
        ----------
        value : tf.Tensor | ndarray
            Data in either tf.Tensor or numpy ndarray.

        Returns
        -------
        feature : tf.train.Feature
            Data encoded as `tf.train.FloatList`.

        """

        return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

    @staticmethod
    def _int64_feature(value):
        """
        Returns an `tf.train.Int64List` from a bool/enum/int/uint.

        Parameters
        ----------
        value : tf.Tensor | ndarray
            Data in either tf.Tensor or numpy ndarray.

        Returns
        -------
        feature : tf.train.Feature
            Data encoded as `tf.train.Int64List`.

        """

        if isinstance(value, tf.Tensor):
            value = value.numpy()
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))
        