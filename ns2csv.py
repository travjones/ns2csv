import csv


def partition(alist, indices):
    # splices list by indices
    return [alist[i:j] for i, j in zip([0] + indices, indices + [None])]

# user input N, cast to int
num_subjects = int(raw_input("Number of subjects? "))

# user input filename or path
filename = raw_input("Filename or path? ")

# read entire file into content list
with open(filename) as f:
    content = f.readlines()

# identify indices where new sets of data are (splits into event/measure
# combos)
splitIndexes = [i for i, x in enumerate(content) if "Calculate measure" in x]
# use splitIndex to split content
shards = partition(content, splitIndexes)

# start from index 1, process each shard (event/measure combo)
for shard_index in range(1, len(shards)):
    # shard_data dictionary to hold info about each piece of data
    shard_data = {}
    comp_tmp = shards[shard_index][0].split("event ")
    shard_data['component'] = comp_tmp[1].split(",")[0]
    shard_data['type'] = shards[shard_index][1].split(
        " averaged")[0].replace(" ", "").lower()

    numNewLines = 0
    chunks = []
    # each segment of data within a shard is separated by two new lines
    for j, line in enumerate(shards[shard_index]):
        if line == '\n':
            numNewLines = numNewLines + 1
            if numNewLines == 2:
                # BASED ON NUMBER OF SUBJECTS
                chunks.append(shards[shard_index][
                              (j + 1):(j + 1 + num_subjects + 1 + 3)])
                numNewLines = 0

    chunksToDel = []
    # store chunkes to del in new list starting at 2, every 3 to fix duplicates
    for i in range(2, len(chunks), 3):
        chunksToDel.append(chunks[i])

    # rawData list contains data chunks that aren't in chunksToDel
    rawData = [x for x in chunks if x not in chunksToDel]

    # even indexes trailing "/n", odd indexes preceding "/n" -- so delete
    for i, value in enumerate(rawData):
        if i % 2 == 0:
            rawData[i].pop(-1)
        else:
            rawData[i].pop(0)

    # add headers for data to shard_data
    for data in rawData:
        shard_data['data'] = []
        values = rawData[0][1].split("\t")
        values.pop(0)
        # cleanup each heading (montage name in NetStation)
        for val in values:
            shard_data['data'].append(
                val.strip("_").lower().strip().replace(" ", ""))

    # create a csv file for each shard (event + measure combo)
    with open(filename.split(".")[0] + "data" + str(shard_index) + ".csv", "w+") as out:
        # assemble and write header
        header = ['subjID', 'type', 'component', 'segment']
        csv_out = csv.writer(out)
        header.extend(shard_data['data'])
        csv_out.writerow(header)
        # cleanup and write each line of data
        for data in rawData:
            for i in range(3, len(data)):
                data_vals = data[i].split("\t")
                data_vals.pop(-1)
                # LINE BELOW DEPENDS ON SUBJID FORMAT (i.e., "_x_")
                subj_id = data_vals[0].split("_")[1]
                data_vals.pop(0)
                shard_data['segment'] = data[
                    0].rstrip().replace(" ", "").lower()
                data_vals_float = [float(i) for i in data_vals]
                row = [subj_id, shard_data['type'], shard_data[
                    'component'], shard_data['segment']]
                row.extend(data_vals_float)
                csv_out.writerow(row)
