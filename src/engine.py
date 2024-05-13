class Engine(object):
    @staticmethod
    def ordering(data):
        pass

    @staticmethod
    def filtering(data):
        filtered = []
        for i in range(0, 3):
            filtered.append(data['restaurant']['results'][i])

        for i in range(0, 3):
            filtered.append(data['transit']['results'][i])

        for i in range(0, 4):
            filtered.append(data['tourist']['results'][i])

        return filtered

    
    @staticmethod
    def covertFlat(data):
        flatData = []

        for row in data:
            flatRow = {}
            flatRow['latitude'] = row['geometry']['location']['lat']
            flatRow['longitude'] = row['geometry']['location']['lng']
            flatRow['latitudeDelta'] = 1
            flatRow['longitudeDelta'] = 1
            flatRow['icon'] = row['icon']
            flatRow['name'] = row['name']
            flatRow['photos'] = row['photos'][0]
            flatData.append(flatRow)
        
        return flatData