import os, sys, getopt, json
from dotenv import load_dotenv
from schedulerlocal.node.cpuexplorer import CpuExplorer
from schedulerlocal.node.cpuset import ServerCpuSet
from schedulerlocal.node.memoryexplorer import MemoryExplorer
from schedulerlocal.node.memoryset import ServerMemorySet
from schedulerlocal.node.jsonencoder import GlobalEncoder
from schedulerlocal.domain.libvirtconnector import LibvirtConnector
from schedulerlocal.schedulerlocal import SchedulerLocal
from schedulerlocal.dataendpoint.dataendpointpool import DataEndpointPool
from schedulerlocal.dataendpoint.dataendpoint import DataEndpointLive, DataEndpointCSV

def print_usage():
    print('todo')

if __name__ == '__main__':

    short_options = "hd:t:"
    long_options = ["help", "debug=", "topology="]

    load_dotenv()
    cpuset = None
    memset = None
    debug_level = 0
    try:
        arguments, values = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print(str(err))
        print_usage()
    for current_argument, current_value in arguments:
        if current_argument in ('-h', '--help'):
            print_usage()
        elif current_argument in('-t', '--topology'):
            with open(current_value, 'r') as f:
                json_topology = f.read()
            cpuset = ServerCpuSet().load_from_json(json_topology).build_distances()
            memset = ServerMemorySet().load_from_json(json_topology)
        elif current_argument in('-d', '--debug'):
            debug_level = int(current_value)

    ###########################################
    # First, build node topology
    ###########################################
    if (cpuset is None) or (memset is None):
        to_exclude = [int(cpuid)for cpuid in os.getenv('TOPO_EXCLUDE').split(',')] if os.getenv('TOPO_EXCLUDE') else list()
        cpuset = CpuExplorer(to_exclude=to_exclude).build_cpuset()
        memset = MemoryExplorer().build_memoryset()
        if debug_level>0:
            topology = {'cpuset': cpuset, 'memset': memset}
            with open('debug/topology_local.json', 'w') as f: 
                f.write(json.dumps(topology, cls=GlobalEncoder))

    ###########################################
    # Second, initiate local libvirt connection
    ###########################################
    libvirt_connector = LibvirtConnector(url=os.getenv('QEMU_URL'),\
                                    loc=os.getenv('QEMU_LOC'),\
                                    machine=os.getenv('QEMU_MACHINE'))

    ###########################################
    # Third, manage Endpoints
    ##########################################
    saver = None
    if debug_level>0:
        saver = DataEndpointCSV(input_file=None, output_file='debug/monitoring.csv')
    endpoint_pool = DataEndpointPool(loader=DataEndpointLive(), saver=saver)

    ###########################################
    # Finally, launch scheduling facilities
    ###########################################
    scheduler_local = SchedulerLocal(cpuset=cpuset,\
                                    memset=memset,\
                                    endpoint_pool=endpoint_pool,\
                                    connector=libvirt_connector,\
                                    tick=0.2,\
                                    api_url='127.0.0.1',
                                    api_port='8099',
                                    debug_level=debug_level)
    try:
        scheduler_local.run()
    except KeyboardInterrupt:
        print("Program interrupted")
        del scheduler_local
        sys.exit(0)