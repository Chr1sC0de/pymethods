def gap_space(start, lim, gap):
    output = []

    if start < lim:
        pt = start
        while pt < lim:
            output.append(pt)
            pt += gap

    if start > lim:
        pt = start
        while pt > lim:
            output.append(pt)
            pt -= gap

    return output


def make_odd(input):
    input = int(input)
    if input % 2 == 0:
        input += 1
    return input