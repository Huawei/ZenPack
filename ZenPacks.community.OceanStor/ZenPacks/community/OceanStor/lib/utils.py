def convert_capacity(v, sector_size=512):
    capacity = float(v) * sector_size
    capacity_units = ("B", "KB", "MB", "GB", "TB", "PB")

    i = 0
    while i < len(capacity_units):
        if capacity < 1024:
            break
        else:
            capacity = capacity / 1024
            i += 1

    return "%.3f%s" % (int(capacity * 1000) / float(1000), capacity_units[i])
