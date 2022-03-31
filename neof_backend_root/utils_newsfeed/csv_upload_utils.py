from csv import reader


def get_csv_data_size(file_path=None):
    with open(file_path, "r") as csv_file:
        data = reader(csv_file, delimiter=",")
        next(data)
        index = 0
        for index, _ in enumerate(data):
            pass
        return index + 1
