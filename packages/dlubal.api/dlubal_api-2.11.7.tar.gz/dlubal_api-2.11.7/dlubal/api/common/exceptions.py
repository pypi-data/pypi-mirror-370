def exception_handler(exception, value, traceback):
    '''
    Exception handler
    '''
    print('ERROR:')
    if traceback:
        print(f'File: {traceback.tb_frame.f_code.co_filename}, line: {traceback.tb_frame.f_lineno}')
    if value:
        try:
            print('Message:', value.details())
        except:
            print('Message:', value)