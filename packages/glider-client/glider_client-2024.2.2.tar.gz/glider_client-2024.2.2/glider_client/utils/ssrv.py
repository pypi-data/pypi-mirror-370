import getpass
import requests
import json

SSRV_URL = 'https://ssrv/'

def ensure_cavity_system_sample(serial_number):
    cavity_name = 'GLIDER_{}'.format(serial_number)
    rsp = requests.get(SSRV_URL + 'samples',
        params={'filters': json.dumps([{'name': 'name',
        'op': 'like',
        'val': cavity_name}])
                },
                       verify=False)
    rsp.raise_for_status()
    data = rsp.json()
    if data['num_results'] == 0:
        rsp = requests.post(SSRV_URL + 'samples',
                            params={'name': 'GLIDER_{}'.format(serial_number),
                                    'fullname': 'GLIDER_{}'.format(serial_number),
                                    'sample_type': 'CAVITY_SYSTEM'},
                            verify=False)
        rsp.raise_for_status()

def get_laser_name_from_sn(sn):
    rsp = requests.get(SSRV_URL + '/results/resources/laspar',
                       data=json.dumps({'filters': json.dumps([{'name': 'no',
                                                     'op': 'eq',
                                                     'val': sn}])}),
                       headers={'Content-Type': 'application/json'},
                       verify=False)
    rsp.raise_for_status()
    data = rsp.json()
    return data['objects'][0]['data']['lasnom']

def store_stepping_poi(glider_config, dataset, comment=None):
    serial_number = glider_config['serial']
    cavity_name = 'GLIDER_{}'.format(serial_number)
    laser_name = get_laser_name_from_sn(glider_config['cavities']['1']['laserSerial'])
    laser_name2 = get_laser_name_from_sn(glider_config['cavities']['2']['laserSerial'])
    dataset['laser_name'] = laser_name
    dataset['laser_name2'] = laser_name2
    dataset['poi_list_postdwellms'] = [x['postDwellMs'] for x in dataset['poi_list']]
    dataset['poi_list_laserdwellms'] = [x['laserDwellMs'] for x in dataset['poi_list']]
    dataset['poi_list_wavenumber'] = [x['wavenumber'] for x in dataset['poi_list']]
    dataset.pop('poi_list')
    rsp = requests.post(SSRV_URL + '/measures',
                        params={'sample_name': cavity_name,
                                'session_type': 'test',
                                'measure_type': 'gli_stepping_poi',
                                'station_name': 'PRISM',
                                'setup_name': None,
                                'user_name': getpass.getuser()},
                        json={'data': dataset},
                        verify=False)
    rsp.raise_for_status()
    if comment:
        meas_id = rsp.json()['catalog_id']
        rsp = requests.patch(SSRV_URL + '/measures/{}'.format(meas_id),
                             params={'operation': 'update',
                                     'user_name': getpass.getuser()},
                             json={'patch': {'comment': comment}},
                             verify=False)
        rsp.raise_for_status()

def store_adc_delay(glider_config, dataset):
    serial_number = glider_config['serial']
    cavity_name = 'GLIDER_{}'.format(serial_number)
    laser_name = get_laser_name_from_sn(glider_config['cavities'][str(dataset['cavity'])]['laserSerial'])
    dataset['laser_name'] = laser_name
    rsp = requests.post(SSRV_URL +'/measures',
                        params={'sample_name': cavity_name,
                                'session_type': 'test',
                                'measure_type': 'gli_scan_adc_delay',
                                'station_name': 'PRISM',
                                'setup_name': None,
                                'user_name': getpass.getuser()},
                        json={'data': dataset},
                        verify=False)
    rsp.raise_for_status()

if __name__ == '__main__':
    from glider_client.utils.glider import get_glider_configuration
   # ensure_cavity_system_sample(190)
    print(get_laser_name_from_sn(17030))
    #store_stepping_poi(190, {})