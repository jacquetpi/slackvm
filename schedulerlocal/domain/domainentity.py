from collections import defaultdict

class DomainEntity:
    """
    Data Access Object (DAO) representing a domain (i.e. a VM)
    ...

    Attributes
    ----------
    uuid : str
        VM identifier
    name : str
        VM name
    cpu : int
        CPU allocation
    cpu_pin : list
        list of vCPU pinned situation
    cpu_ratio : float
        CPU oversubscription ratio

    Public Methods
    -------
    Getter/Setter
    """

    def __init__(self, **kwargs):
        req_attributes = ['uuid', 'name', 'mem', 'cpu', 'cpu_pin', 'cpu_ratio']
        for req_attribute in req_attributes:
            if req_attribute not in kwargs: raise ValueError('Missing required argument', req_attributes)
            setattr(self, req_attribute, kwargs[req_attribute])

    def get_uuid(self):
        """Return VM uuid
        ----------
        """
        return self.uuid

    def get_name(self):
        """Return VM name
        ----------
        """
        return self.name

    def get_mem(self):
        """Return mem allocation
        ----------
        """
        return self.mem

    def get_cpu(self):
        """Return CPU allocation
        ----------
        """
        return self.cpu

    def get_cpu_pin(self):
        """Return CPU pin situation
        ----------
        """
        return self.cpu_pin

    def get_cpu_pin_aggregated(self):
        """Return a dict specifying for each cpuid if at least one vCPU is pinned to it (boolean value)
        ----------
        """
        aggregated_vm_cpu_pin = defaultdict(lambda: False)
        for vcpu_pin in self.get_cpu_pin(): 
            for cpu, is_pinned in enumerate(vcpu_pin): 
                aggregated_vm_cpu_pin[cpu] = (aggregated_vm_cpu_pin[cpu] or is_pinned)
        return aggregated_vm_cpu_pin

    def get_cpu_ratio(self):
        """Return CPU ratio
        ----------
        """
        return self.cpu_ratio

    def __str__(self):
        """Convert state to string
        ----------
        """
        return 'vm ' + self.get_name() + ' ' + str(self.get_cpu()) + 'vCPU ' + str(self.get_mem()) + 'MB with oc ' + str(self.get_cpu_ratio) + '\n'