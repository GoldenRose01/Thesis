from src.enums import TraceLabel
import numpy as np

# Classe Bucket per tenere traccia delle statistiche
class Bucket:
    def __init__(self, num_traces=None,
                 trace_attributes=None, resource_attributes=None,
                 num_positive_not_compliant_traces=None, num_positive_compliant_traces=None,
                 num_compliant_traces=None):
        self._num_traces = num_traces if num_traces is not None else 0
        self._num_positive_not_compliant_traces = num_positive_not_compliant_traces \
            if num_positive_not_compliant_traces is not None else 0
        self._num_positive_compliant_traces = num_positive_compliant_traces \
            if num_positive_compliant_traces is not None else 0
        self._num_compliant_traces = num_compliant_traces if num_compliant_traces is not None else 0
        self._trace_attributes = trace_attributes if trace_attributes is not None else {}
        self._resource_attributes = resource_attributes if resource_attributes is not None else {}
        self._prefix = None

    def add_trace_attributes(self, new_attributes):
        for key, value in new_attributes.items():
            if key in self._trace_attributes:
                self._trace_attributes[key].append(value)
            else:
                self._trace_attributes[key] = [value]

    def add_resource_attributes(self, new_attributes):
        for key, value in new_attributes.items():
            if key in self._resource_attributes:
                self._resource_attributes[key].append(value)
            else:
                self._resource_attributes[key] = [value]

    def __str__(self):
        return (f"Traces:{self._num_traces}, "
                f"PNCT: {self._num_positive_not_compliant_traces},"
                f" PCT: {self._num_positive_compliant_traces},"
                f" CT: {self._num_compliant_traces}, "
                f"Trace Attributes: {self._trace_attributes}, "
                f"Resource Attributes: {self._resource_attributes}, "
                f"Prefix: {self._prefix}")

# Classe Bucketer per gestire i bucket
class Bucketer:
    def __init__(self, bucket_list=None):
        self._bucket_list = bucket_list if bucket_list is not None else []
        self.prova = []
        self.smooth_factor = 1
        self.num_classes = 2
        self.total_pos_compl_traces = None
        self.total_pos_not_compl_traces = None
        self.total_compl_traces = None
        self.total_traces = None

    # Aggiungi una traccia al bucket
    def add_trace(self, prefix, trace_label, compliant, trace_attributes=None, resource_attributes=None):
        found_bucket = False
        if len(self._bucket_list) > 0:
            for bucket in self._bucket_list:
                if prefix == bucket._prefix:
                    bucket._num_traces += 1
                    bucket._num_positive_not_compliant_traces += 0 if compliant else 1
                    bucket._num_positive_compliant_traces += 1 if compliant and trace_label == TraceLabel.TRUE else 0
                    bucket._num_compliant_traces += 1 if compliant else 0
                    if trace_attributes is not None:
                        bucket.add_trace_attributes(trace_attributes)
                    if resource_attributes is not None:
                        bucket.add_resource_attributes(resource_attributes)
                    found_bucket = True
                    break
        if len(self._bucket_list) == 0 or not found_bucket:
            new_bucket = Bucket(num_traces=1,
                                num_positive_not_compliant_traces=0 if compliant else 1,
                                num_positive_compliant_traces=1 if compliant and trace_label == TraceLabel.TRUE else 0,
                                num_compliant_traces=1 if compliant else 0,
                                trace_attributes=trace_attributes,
                                resource_attributes=resource_attributes)
            new_bucket._prefix = prefix
            new_bucket._num_positive_not_compliant_traces = 0 if compliant else 1
            new_bucket._num_positive_compliant_traces = 1 if compliant and trace_label == TraceLabel.TRUE else 0
            new_bucket._num_compliant_traces = 1 if compliant else 0
            new_bucket._prefix = prefix
            self.add_bucket(new_bucket)

    # Aggiungi un bucket
    def add_bucket(self, bucket):
        self._bucket_list.append(bucket)

    def __str__(self):
        return " | ".join([str(bucket) for bucket in self._bucket_list])

    # Calcola la probabilità di tracce positive compliant
    def prob_positive_compliant(self):
        self.total_pos_compl_traces = sum([bucket._num_positive_compliant_traces for bucket in self._bucket_list])
        self.total_compl_traces = sum([bucket._num_compliant_traces for bucket in self._bucket_list])
        prob = (self.total_pos_compl_traces + self.smooth_factor) /\
               (self.total_compl_traces + self.smooth_factor*self.num_classes)
        return prob

    # Calcola la probabilità di tracce positive non compliant
    def prob_positive_not_compliant(self):
        self.total_pos_not_compl_traces = sum([bucket._num_positive_not_compliant_traces
                                               for bucket in self._bucket_list])
        self.total_compl_traces = sum([bucket._num_compliant_traces
                                       for bucket in self._bucket_list])
        self.total_traces = sum([bucket._num_traces
                                 for bucket in self._bucket_list])

        prob = (self.total_pos_not_compl_traces + self.smooth_factor) / \
               (self.total_traces - self.total_compl_traces + self.smooth_factor*self.num_classes)
        return prob

    # Calcola il guadagno
    def gain(self):

        ee=np.array(self.prova)
        comp = np.sum(ee[:, 1])
        non_comp = len(ee) - comp
        pos_comp = len(np.where((ee == (1, 1)).all(axis=1))[0])
        pos_non_comp = len(np.where((ee == (1, 0)).all(axis=1))[0])
        prob1 = (pos_comp + self.smooth_factor) / (comp + self.smooth_factor*self.num_classes)
        prob2 = (pos_non_comp + self.smooth_factor) / (non_comp + self.smooth_factor*self.num_classes)
        gain = prob1/prob2
        return gain

    def __str__(self):
        return " | ".join([str(bucket) for bucket in self._bucket_list])

bucketer = Bucketer()