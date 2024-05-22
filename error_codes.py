def get_error_codes_dictionnary():
    error_codes_dictionnary = {
        100 : ['INFO', 'VAULT ALREADY ENCRYPTED'],
        101 : ['INFO', 'VAULT ALREADY DECRYPTED'],
        # 102 : ['INFO', 'VAULT ALREADY EXISTS -> REMOVE IT BEFORE CREATING A NEW ONE'],
        102 : ['INFO', 'A VAULT WITH THE SAME NAME ALREADY EXISTS'],
        200 : ['INFO', 'OPERATION SUCCESSFUL'],
        400 : ['ERROR', 'WRONG MASTER PASSWORD'],
        401 : ['ERROR', 'WRONG VAULT CODE'],
        402 : ['ERROR', 'NO VAULT WAS FOUND']
    }

    return error_codes_dictionnary