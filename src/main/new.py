import click
import os
import shutil
import datetime
import random
import string
import yaml
from pathlib import Path

def find_unique_project_id(base_dir):
    """生成不重复的项目标识符，按顺序使用字母"""
    # 生成时间部分
    time_part = datetime.datetime.now().strftime("%Y%b")
    
    # 获取当前目录下已存在的同月份项目
    existing_projects = []
    for item in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, item)) and item[1:] == time_part:
            if len(item) > 0 and item[0].islower():
                existing_projects.append(item[0])
    
    # 按顺序找到第一个可用的字母
    for letter in string.ascii_lowercase:
        if letter not in existing_projects:
            project_id = f"{letter}{time_part}"
            project_path = os.path.join(base_dir, project_id)
            return project_id
    
    return project_id

def replace_placeholders_in_tex(tex_file, title, author_yaml_path):
    """替换.tex文件中的占位符"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    with open(author_yaml_path, 'r', encoding='utf-8') as f:
        author_info = yaml.safe_load(f)
    
    # 替换标题
    content = content.replace('<TITLE>', title)
    
    # 替换作者信息
    for key, value in author_info.items():
        placeholder = f'<{key.upper()}>'
        content = content.replace(placeholder, str(value))
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(content)

@click.command()
@click.argument('title')
@click.option('--template', default='default', help='模板类型，默认为default')
@click.option('--tags', '-t', multiple=True, help='项目标签，可指定多个')
def new(title, template, tags):
    """创建新的LaTeX项目"""
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    texs_path = os.path.join(os.path.dirname(base_path), "texs")
    author_yaml_path = os.path.join(base_path, 'config', 'author.yaml')
        
    template_dir = os.path.join(base_path, "assets", "templates", template)
    if not os.path.exists(template_dir):
        click.echo(f"错误：模板 '{template}' 不存在", err=True)
        return
    
    # 生成项目标识符和路径
    project_id = find_unique_project_id(texs_path)
    project_path = os.path.join(texs_path, project_id)
    
    try:
        # 复制模板文件
        shutil.copytree(template_dir, project_path)
        click.echo(f"已创建项目: {project_id}")
        
        # 加载作者信息
        
        # 替换.tex文件中的占位符
        tex_files = list(Path(project_path).glob('*.tex'))
        for tex_file in tex_files:
            replace_placeholders_in_tex(tex_file, title, author_yaml_path)
        
        # 创建元数据文件
        metadata = {
            'project_id': project_id,
            'title': title,
            'created_at': datetime.datetime.now().isoformat(),
            'tags': list(tags) if tags else [],
            'template': template
        }
        
        metadata_path = os.path.join(project_path, 'metadata.yaml')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        
        click.echo(f"项目路径: {project_path}")
        click.echo(f"标题: {title}")
        if tags:
            click.echo(f"标签: {', '.join(tags)}")
            
    except Exception as e:
        click.echo(f"创建项目时出错: {e}", err=True)
        # 清理已创建的文件
        if os.path.exists(project_path):
            shutil.rmtree(project_path)

if __name__ == '__main__':
    new()