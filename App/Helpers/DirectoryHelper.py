import os

base_dir = os.getcwd()

def get_curr_work_dir():
    directories = dict()

    directories['templates_dir']  = os.path.join(base_dir, 'Views')
    directories['static_dir']  = os.path.join(base_dir, 'Views/Templates/Statics')
    directories['public_dir'] = os.path.join(base_dir, 'Public')
    directories['controllers_dir'] = os.path.join(base_dir, 'App/Controllers')
    directories['helpers_dir'] = os.path.join(base_dir, 'App/Helpers')
    
    return directories

def get_model_dir(model_nm, model_base_path='Public/Models'):
    path = os.path.join(base_dir, f'{model_base_path}/{model_nm}.sav')
    if os.path.exists(path):
        return path