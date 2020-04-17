from .descriptor import (
    Descriptor, LockedDescriptor, NoInputFunctionAlias
)
from .cummulative_decompose import (
    cummulative_decompose, IsSubsetString,
)
from .is_something import (
    IsAny, Isinstance, Issubclass, is_none, is_iterable,
    Isin, is_string, is_int
)
from .memory_location import hex_memory
from .sequential_functions import SequentialFunction
from .alias_dict import AliasDict
from .len_dim_shape import (
    LenDimShape, len_dim_shape_axis, len_dim_shape_longest,
    len_dim_shape_shortest
)
from .dim_shape import (
    is_1d, len_shape, make_column, make_row
)
from .multiprocessing_tools import (
    chunk_iterable, enumerate_chunk, sort_pair_list_and_extract_items,
    time_func
)
from .array_size import memory_size
from .lim_gen import gap_space, make_odd

def listZip(*args):
        return list(zip(*args))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def removeKeyList(myList,key): return [item for item in myList if not key(item)]

def chunkIt(seq, num):
        avg = len(seq) // num
        out = []

        for i in list(range(num)):
                k = i*avg
                if i < (num-1):
                        out.append(seq[k:(k+avg)])
                else:
                        out.append(seq[k:])
        return out

def makeIDchunks(*args,num):
        iDs         = np.arange(num)
        finalList   = [iDs];  finalListSetter = finalList.append
        for item in args:
                vals = chunkIt(item,num)
                for i in range(len(vals)):
                        if len(vals[i]) == 1:
                                vals[i] = vals[i][0]
                finalListSetter(vals)
        zipped      = list(zip(*finalList))
        return zipped

def mergeListofLists(listoflists):
        result = []
        setter = result.extend
        list(map(setter, listoflists))
        return result

def getkwargs(function):
        inspected = inspect.getfullargspec(function)
        keywords  = inspected.args[-len(inspected.defaults):]
        return keywords

def listFolders(mainFolder, hidden = ['.','_']):
        mainFolder  = Path(mainFolder)
        folders   = mainFolder.glob('*')
        if isinstance(hidden,str):
                return [folder for folder in folders if not folder.name.startswith(hidden) ]

        for h in hidden:
                folders = [folder for folder in folders if not folder.name.startswith(h)]
        return folders

def grabSingleFolderFromPattern(pattern,workingDirectory):
    workingDirectory = Path(workingDirectory)
    try:
        folders = [path for path in workingDirectory.glob(pattern) if path.is_dir()]
        assert len(folders) == 1, 'multiple image directories located'
    except:
        folders = [path for path in workingDirectory.glob(pattern.lower()) if path.is_dir()]
        assert len(folders) == 1, 'multiple image directories located'
    return folders[0]

def isNumber(string):
        string = str(string)
        if string.isdigit():
            location        = int(string)
            return True
        else:
            try:
                location        = float(location)
                return True
            except:
                return False

def getNunmberedFolders(mainFolder):
        mainFolder = Path(mainFolder)
        folders = [folder for folder in mainFolder.glob('*') if isNumber(folder.name)]
        folders = [folder for folder in folders if folder.is_dir()]
        return folders

def longestLine(string):
        return max([len(x) for x in string.splitlines()])

def smartSpaceListOfStrings(
        listOftstrings,
        separator,
        joiner = '\n\n'
        ):

        tmp = []; setter = tmp.append
        for item in listOftstrings:
                if '\n' not in item: item = item.split(separator,1)
                setter(item)
        listOftstrings = tmp
        try:
                maxLen = max([len(item[0]) for item in listOftstrings
                        if isinstance(item,list)]
                )

                body = [] ; setter = body.append
                for item in listOftstrings:
                        if isinstance(item,list):
                                setter(
                                        item[0]+' '*(1+ (maxLen - len(item[0]) ) ) + item[1]
                                )
                        else:
                                setter(item)
        except:
                body = listOftstrings
        body   = joiner.join(body)
        return body

def tablines(string):
        listofStrings = ['\t'+item for item in string.split('\n')]
        return '\n'.join(listofStrings)

def pathOrString(obj):
    if any( [ isinstance(obj,objType) for objType in [Path,str] ] ):
        return True
    return False

def sortMPlist(mpList):
        mpList.sort(key = lambda x: x[0])
        output = []
        mpList = [item[1] for item in mpList ]
        [output.extend(item) for item in mpList]
        mpList = output
        return mpList


comparison_methods = (
    '__lt__', '__le__', '__eq__', '__ne__', '__ge__', '__gt__'
)

__all__ = [
    'Descriptor', 'LockedDescriptor', 'NoInputFunctionAlias',
    'cummulative_decompose', 'IsSubsetString', 'IsAny', 'Isinstance',
    'Issubclass', 'is_none', 'is_iterable', 'Isin', 'is_string', 'hex_memory',
    'SequentialFunction', 'AliasDict', 'LenDimShape', 'len_dim_shape_axis',
    'len_dim_shape_longest', 'len_dim_shape_shortest', 'is_1d', 'len_shape',
    'make_column', 'make_row', 'chunk_iterable', 'enumerate_chunk',
    'sort_pair_list_and_extract_items', 'memory_size', 'comparison_methods',
    'is_int', 'time_func', 'gap_space', 'make_odd'
]
