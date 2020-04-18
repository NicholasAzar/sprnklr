from enum import Enum

AppLoggerName = "sprnkler"

class AccountType(Enum):
    GOOGLE = "GOOGLE"
    AUTH0 = "AUTH0"

    # Defining the sprnklr account type
    SPRNKLR = "AUTH0" 
    
def merge_two_sorted_object_lists(list1:list, list2:list, key_lambda) -> list:
    len1 = len(list1)
    len2 = len(list2)
    result = []
    i, j = 0, 0
    while i < len1 and j < len2:
        if key_lambda(list1[i]) < key_lambda(list2[j]):
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    return result + list1[i:] + list2[j:]
