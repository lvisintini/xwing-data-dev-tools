from base import XWingDataNormalizer


class AddShipsIds(XWingDataNormalizer):
    source_key = 'ships'

    @staticmethod
    def analise():
        print('No data to show')

    def normalize(self):
        for index in range(0, len(self.data)):
            self.data[index]['id'] = index + 1


if __name__ == '__main__':
    print('ShipsIds')
    AddShipsIds()
