import numpy as np


class np_stats_descriptor:

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.set_name = f'_{name}'
        self.kwargs = kwargs
        self.args = args

    def __get__(self, obj, obj_type):
        if not hasattr(obj, self.set_name):
            value = getattr(np, self.name)(
                obj.data,
                *self.args, **self.kwargs,
                **obj.kwargs
            )
            setattr(
                obj, self.set_name, value
            )
        return getattr(
            obj, self.set_name
        )


class SummaryStatistics:

    calculated_statistics = [
        'mean', 'std', 'var', 'median', 'q_25', 'q_75', 'max', 'min']
    default_kwargs = dict(
        axis=-1, keepdims=False
    )
    mean = np_stats_descriptor('mean')
    std = np_stats_descriptor('std')
    var = np_stats_descriptor('var')
    median = np_stats_descriptor('median')
    q_25 = np_stats_descriptor('quantile', 0.25)
    q_75 = np_stats_descriptor('quantile', 0.75)
    max = np_stats_descriptor('amax')
    min = np_stats_descriptor('amin')
    
    def __init__(
            self, data, **kwargs):
        self.default_kwargs.update(kwargs)
        self.kwargs = self.default_kwargs
        self._data = data
        self.plots = {}

    @property
    def shape(self):
        return self.data.shape

    @property
    def data(self):
        return self._data

    def mean_std(self, n_std):
        return self.mean + n_std * self.std

    @property
    def mu_p_2sigma(self):
        return self.mean_std(2)

    @property
    def mu_m_2sigma(self):
        return self.mean_std(-2)


        
if __name__ == "__main__":
    data = np.arange(0,100)
    data_2 = np.arange(0,100).reshape(2,50)
    stats_1 = SummaryStatistics(data)
    stats_2 = SummaryStatistics(data_2)
    print(stats_2.mu_p_2sigma)
    print(stats_2.mu_m_2sigma)
    print(stats_2.max)
    print(stats_2.min)
    print('done')
