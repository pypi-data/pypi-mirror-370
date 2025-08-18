


def force_id_on_sbml(file_path, model_id):
    
    with open(file_path, 'r') as file:
        content = file.read()
    content = content.replace(
        f'<model metaid="meta_{model_id}" fbc:strict="true">', 
        f'<model metaid="meta_{model_id}" id="{model_id}" fbc:strict="true">'
    )
    with open(file_path, 'w') as file:
        file.write(content)