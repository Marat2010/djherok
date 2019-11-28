import json
file_answer = 'answer.json'
file_city = 'answer_city.json'

# def write_json(data, filename=file_answer): # write str city to file
#     with open(filename, 'w') as f:
#         f.write(data)
#
# def read_json(filename=file_answer):
#     with open(filename, 'r') as f:
#         r = f.readline()
#     return r


def write_json(data, filename=file_answer):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_answer):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


message = '1212Казань, RU'

d = read_json()

# print(d['message'].keys())
# print(d.keys())
d['city_message'] = message
print(d.keys())

# d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)
print(type(d))
# print("Вывод:\n" + d)
#
# r = json.loads(d)
# print("после loads ", type(r))

write_json(d, file_city)

