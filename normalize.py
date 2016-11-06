import json
from collections import OrderedDict


class XWingDataNormalizer:
    source_key = ''

    def filter(self, model):
        raise NotImplementedError

    def __init__(self):
        self.data = []
        self.load_data()
        print('BEFORE --------')
        self.analise()
        self.normalize()
        print('\nAFTER ---------')
        self.analise()
        self.save_data()

    def load_data(self):
        with open('./data/{}.js'.format(self.source_key), 'r') as file_object:
            self.data.extend(json.load(file_object, object_pairs_hook=OrderedDict))

    def save_data(self):
        with open('./data/{}.js'.format(self.source_key), 'w') as file_object:
            json.dump(self.data, file_object, indent=2)

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError


class ManouverNormalizer(XWingDataNormalizer):
    source_key = 'ships'

    min_maneuvers_override = 10

    def analise(self):
        self.filtered_max_speed = 0
        self.filtered_min_speed = 1000
        self.max_speed = 0
        self.min_speed = 1000
        self.filtered_max_maneuvers = 0
        self.filtered_min_maneuvers = 1000
        self.max_maneuvers = 0
        self.min_maneuvers = 1000
        self.types = set()
        for model in self.data:
            if self.filter(model):
                if 'maneuvers' not in model:
                    print(model['name'])
                    continue

                speed = len(
                    ''.join(['1' if any(m) else '0' for m in model['maneuvers']]).rstrip('0')
                )

                self.filtered_max_speed = max(speed, self.filtered_max_speed)
                self.filtered_min_speed = min(speed, self.filtered_min_speed)
                self.max_speed = max(len(model['maneuvers']), self.max_speed)
                self.min_speed = min(len(model['maneuvers']), self.min_speed)

                for speed in model['maneuvers']:
                    maneuver = ''.join([str(s) for s in speed]).rstrip('0')
                    self.filtered_max_maneuvers = max(len(maneuver), self.filtered_max_maneuvers)
                    self.filtered_min_maneuvers = min(len(maneuver), self.filtered_min_maneuvers)
                    self.max_maneuvers = max(len(speed), self.max_maneuvers)
                    self.min_maneuvers = min(len(speed), self.min_maneuvers)

                    if len(speed) == 0:
                        self.types.add(None)
                    else:
                        self.types = self.types.union(speed)

        print('Max Speed', self.max_speed)
        print('Filtered Max Speed', self.filtered_max_speed)
        print('Min Speed', self.min_speed)
        print('Filtered Min Speed', self.filtered_min_speed)

        print('Types', list(self.types))
        print('Max Maneuvers', self.max_maneuvers)
        print('Filtered Max Maneuvers', self.filtered_max_maneuvers)
        print('Min Maneuvers', self.min_maneuvers)
        print('Filtered Min Maneuvers', self.filtered_min_maneuvers)

    def normalize(self):
        for model in self.data:
            if self.filter(model):
                if 'maneuvers' not in model:
                    model['maneuvers'] = [
                         [0]*max(self.filtered_max_maneuvers, self.min_maneuvers_override)
                    ]*self.filtered_max_speed
                    continue

                for index in range(len(model['maneuvers'])):
                    if len(model['maneuvers'][index]) > self.filtered_max_maneuvers:
                        model['maneuvers'][index] = model['maneuvers'][index][0:max(
                            self.filtered_max_maneuvers, self.min_maneuvers_override
                        )]
                    else:
                        model['maneuvers'][index].extend([0]*(max(
                            self.filtered_max_maneuvers, self.min_maneuvers_override
                        ) - len(model['maneuvers'][index])))


class SmallShipManouverNormalizer(ManouverNormalizer):
    def filter(self, model):
        return model['size'] == 'small'


class LargeShipManouverNormalizer(ManouverNormalizer):
    def filter(self, model):
        return model['size'] == 'large'


class HugeShipManouverNormalizer(ManouverNormalizer):
    min_maneuvers_override = 5

    def filter(self, model):
        return model['size'] == 'huge'

    def normalize(self):
        super().normalize()
        # Handle maneuvers_energy attr
        for model in self.data:
            if self.filter(model):
                if 'maneuvers' not in model:
                    model['maneuvers_energy'] = [
                         [0]*max(self.filtered_max_maneuvers, self.min_maneuvers_override)
                    ]*self.filtered_max_speed
                    continue

                for index in range(len(model['maneuvers_energy'])):
                    if len(model['maneuvers_energy'][index]) > self.filtered_max_maneuvers:
                        model['maneuvers_energy'][index] = model['maneuvers_energy'][index][0:max(
                            self.filtered_max_maneuvers, self.min_maneuvers_override
                        )]
                    else:
                        model['maneuvers_energy'][index].extend([0]*(max(
                            self.filtered_max_maneuvers, self.min_maneuvers_override
                        ) - len(model['maneuvers_energy'][index])))


if __name__ == '__main__':
    print('SmallShipManouverNormalizer')
    SmallShipManouverNormalizer()
    #print('\n\nLargeShipManouverNormalizer')
    #LargeShipManouverNormalizer()
    #print('\n\nHugeShipManouverNormalizer')
    #HugeShipManouverNormalizer()
