from XwingDataDevTools.normalize.base import (DataCollector, DateDataCollector)
from pprint import pprint


class AddMissingSlots(DataCollector):
    source_key = 'upgrades'
    field_name = 'slot'

    memory = {
        294: 'Modification',
    }

    def __init__(self):
        self.slots = []
        super().__init__()

    def analise(self):
        for model in self.data:
            if model.get('slot'):
                self.slots.append(model['slot'])
        self.slots = list(set(self.slots))

    def clean_input(self, new_data):
        try:
            new_data = int(new_data)
            new_data = self.slots[int(new_data)]
        except:
            pass
        else:
            return new_data
        return new_data

    def validate_input(self, new_data):
        return new_data in self.slots

    def print_model(self, model):
        print('\n')
        pprint(model)

    def input_text(self):
        options = '\n\t'.join(
            ['{} - {}'.format(i, self.slots[i]) for i in range(len(self.slots))]
        )
        return  'Which {} should it have?\n\t{}\nResponse:'.format(self.field_name, options)


class AddMissingReleaseDate(DateDataCollector):
    source_key = 'sources'
    field_name = 'release_date'
    input_format = '%B %d, %Y'
    output_format = '%Y-%m-%d'

    memory = {
        0: '2012-09-14',
        1: '2012-09-14',
        2: '2012-09-14',
        3: '2012-09-14',
        4: '2012-09-14',
        5: '2013-02-28',
        6: '2013-02-28',
        7: '2013-02-28',
        8: '2013-02-28',
        9: '2013-09-12',
        10: '2013-09-12',
        11: '2013-09-12',
        12: '2013-09-12',
        13: '2014-03-14',
        14: '2014-06-26',
        15: '2014-06-26',
        16: '2014-06-26',
        17: '2014-06-26',
        18: '2014-09-25',
        19: '2014-05-22',
        20: '2014-04-30',
        21: '2014-11-26',
        22: '2014-11-26',
        23: '2015-02-26',
        24: '2015-02-26',
        25: '2015-02-26',
        26: '2015-02-26',
        27: '2015-08-13',
        28: '2015-08-25',
        29: '2015-08-25',
        30: '2015-08-25',
        31: '2015-08-25',
        32: '2015-09-04',
        33: '2015-12-17',
        34: '2015-12-17',
        35: '2016-03-17',
        36: '2016-03-17',
        37: '2016-03-17',
        38: '2016-03-17',
        39: '2015-12-21',
        40: '2016-06-30',
        41: '2016-10-27',
        42: '2016-09-22',
        43: '2016-09-22',
        44: '2016-09-22',
        45: '2016-09-22',
        49: '2016-12-15',
        50: '2016-12-15'
     }


class AddMissingAnnouncedDate(DateDataCollector):
    source_key = 'sources'
    field_name = 'announcement_date'
    input_format = '%B %d, %Y'
    output_format = '%Y-%m-%d'

    memory = {
        0: '2011-08-02',
        1: '2012-04-17',
        2: '2012-04-17',
        3: '2012-04-17',
        4: '2012-04-17',
        5: '2012-09-14',
        6: '2012-09-14',
        7: '2012-09-14',
        8: '2012-09-14',
        9: '2013-05-04',
        10: '2013-05-04',
        11: '2013-05-04',
        12: '2013-05-04',
        13: '2013-09-16',
        14: '2014-02-07',
        15: '2014-02-07',
        16: '2014-02-07',
        17: '2014-02-07',
        18: '2014-03-18',
        19: '2013-08-20',
        20: '2013-08-20',
        21: '2014-06-13',
        22: '2014-06-13',
        23: '2014-08-15',
        24: '2014-08-15',
        25: '2014-08-15',
        26: '2014-08-15',
        27: '2014-12-19',
        28: '2015-04-20',
        29: '2015-04-20',
        30: '2015-04-20',
        31: '2015-04-20',
        32: '2015-09-03',
        33: '2015-09-10',
        34: '2015-09-10',
        35: '2015-07-31',
        36: '2015-07-31',
        37: '2015-07-31',
        38: '2015-07-31',
        39: '2015-07-31',
        40: '2015-12-14',
        41: '2016-05-04',
        42: '2016-06-02',
        43: '2016-06-02',
        44: '2016-06-02',
        45: '2016-06-02',
        46: '2016-08-05',
        47: '2016-08-05',
        48: '2016-08-05',
        49: '2016-09-02',
        50: '2016-09-02'
    }

if __name__ == '__main__':
    pass
    #print('AddMissingSlots')
    #AddMissingSlots()
    #print('AddMissingReleaseDate')
    #AddMissingReleaseDate()
    #print('AddMissingAnnouncedDate')
    #AddMissingAnnouncedDate()
