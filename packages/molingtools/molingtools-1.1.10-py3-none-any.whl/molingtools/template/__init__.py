import shutil
import os
import click


@click.command()
@click.argument('name')
def project(name):
    if os.path.exists(name): raise Exception(f'{name}项目已存在')    
    shutil.copytree(os.path.dirname(os.path.abspath(__file__)) + '/project', f'./{name}')
    shutil.move(f'./{name}/.gitignore_exp', f'./{name}/.gitignore')
    shutil.move(f'./{name}/README.md_exp', f'./{name}/README.md')
    print(f'{name}-项目模板创建成功')
    
    