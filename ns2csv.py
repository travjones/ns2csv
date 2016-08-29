import csv


def partition(alist, indices):
    return [alist[i:j] for i, j in zip([0] + indices, indices + [None])]

num_subjects = 28

with open("pre.txt") as f:
    content = f.readlines()

splitIndexes = [i for i, x in enumerate(content) if "Calculate measure" in x]
print splitIndexes
# use splitIndex to split content
shards = partition(content, splitIndexes)
# print shards[1]

for shard_index in range(1, len(shards)):
    shard_data = {}
    comp_tmp = shards[shard_index][0].split("event ")
    shard_data['component'] = comp_tmp[1].split(",")[0]
    shard_data['type'] = shards[shard_index][1].split(
        " averaged")[0].replace(" ", "").lower()

    numNewLines = 0
    chunks = []
    for j, line in enumerate(shards[shard_index]):
        if line == '\n':
            numNewLines = numNewLines + 1
            if numNewLines == 2:
                # BASED ON NUMBER OF SUBJECTS
                chunks.append(shards[shard_index][
                              (j + 1):(j + 1 + num_subjects + 1 + 3)])
                numNewLines = 0
    chunksToDel = []
    # del indexes starting at 2, every 3
    for i in range(2, len(chunks), 3):
        chunksToDel.append(chunks[i])

    rawData = [x for x in chunks if x not in chunksToDel]
    # even indexes trailing "/n", odd indexes preceding "/n"
    for i, value in enumerate(rawData):
        if i % 2 == 0:
            rawData[i].pop(-1)
        else:
            rawData[i].pop(0)

    print rawData
    for data in rawData:
        # shard_data['segment'] = data[0].rstrip()
        shard_data['data'] = []
        values = rawData[0][1].split("\t")
        values.pop(0)
        for val in values:
            shard_data['data'].append(
                val.strip("_").lower().strip().replace(" ", ""))

    with open("data" + str(shard_index) + ".csv", "w+") as out:
        header = ['subjID', 'type', 'component', 'segment']
        csv_out = csv.writer(out)
        header.extend(shard_data['data'])
        csv_out.writerow(header)
        print rawData
        for data in rawData:
            for i in range(3, len(data)):
                data_vals = data[i].split("\t")
                data_vals.pop(-1)
                subj_id = data_vals[0].split("_")[1]
                data_vals.pop(0)
                shard_data['segment'] = data[
                    0].rstrip().replace(" ", "").lower()
                data_vals_float = [float(i) for i in data_vals]
                row = [subj_id, shard_data['type'], shard_data[
                    'component'], shard_data['segment']]
                row.extend(data_vals_float)
                print row
                csv_out.writerow(row)
