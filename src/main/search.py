import click
import os
import yaml
import re
from datetime import datetime
from typing import List, Dict, Tuple
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

def calculate_match_score(term: str, title: str, tags: List[str]) -> int:
    """计算匹配分数"""
    score = 0
    
    # 标题匹配
    if term.lower() in title.lower():
        score += 2
    
    # 标签匹配
    for tag in tags:
        if term.lower() == tag.lower():
            score += 3  # 完全匹配标签得分更高
        elif term.lower() in tag.lower():
            score += 1
    
    return score

def highlight_text(text: str, term: str) -> Text:
    """高亮匹配的文本"""
    if not term:
        return Text(text)
    
    term_lower = term.lower()
    text_lower = text.lower()
    result = Text()
    
    i = 0
    while i < len(text):
        # 查找匹配位置
        match_pos = text_lower.find(term_lower, i)
        
        if match_pos == -1:
            # 没有更多匹配，添加剩余文本
            result.append(text[i:])
            break
        
        # 添加匹配前的文本
        if match_pos > i:
            result.append(text[i:match_pos])
        
        # 添加高亮的匹配文本
        result.append(
            text[match_pos:match_pos + len(term)],
            style="bold red"
        )
        
        i = match_pos + len(term)
    
    return result

@click.command()
@click.argument('term')
def search(term: str):
    """搜索TeX项目，按匹配程度排序并高亮显示结果"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    texs_dir = os.path.join(os.path.dirname(base_path), "texs")
    
    if not os.path.exists(texs_dir):
        click.echo("错误: .texs目录不存在", err=True)
        return
    
    projects = []
    
    # 遍历所有项目
    for item in os.listdir(texs_dir):
        project_dir = os.path.join(texs_dir, item)
        
        if not os.path.isdir(project_dir):
            continue
        
        meta_file = os.path.join(project_dir, "metadata.yaml")
        if not os.path.exists(meta_file):
            continue
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = yaml.safe_load(f)
            
            title = meta_data.get('title', '')
            tags = meta_data.get('tags', [])
            creation_time = meta_data.get('created_at', '')
            
            # 计算匹配分数
            match_score = calculate_match_score(term, title, tags)
            
            # 解析创建时间
            try:
                create_dt = datetime.fromisoformat(creation_time.replace("'", ""))
            except (ValueError, AttributeError):
                create_dt = datetime.min
            
            projects.append({
                'name': item,
                'title': title,
                'tags': tags,
                'creation_time': creation_time,
                'created_at': create_dt,
                'match_score': match_score
            })
            
        except (yaml.YAMLError, IOError) as e:
            continue
    
    # 按匹配分数和创建时间排序
    projects.sort(key=lambda x: (-x['match_score'], -x['created_at'].timestamp()))
    
    # 使用Rich创建表格
    console = Console()
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    
    # 添加列
    table.add_column("Identifier", style="cyan", width=15)
    table.add_column("Title", style="green", width=30)
    table.add_column("Tags", style="blue", width=30)
    table.add_column("Create Time", style="yellow", width=25)
    
    # 添加行
    for project in projects:
        # 创建高亮文本
        name_text = Text(project['name'])
        title_text = highlight_text(project['title'], term)
        
        # 处理标签
        tags_str = ', '.join(project['tags'])
        tags_text = Text()
        for tag in project['tags']:
            if term.lower() in tag.lower():
                tags_text.append(tag, style="bold red")
            else:
                tags_text.append(tag)
            if tag != project['tags'][-1]:
                tags_text.append(", ")
        
        # 格式化时间
        try:
            time_str = project['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = str(project['creation_time'])
        
        # 添加行到表格
        table.add_row(
            name_text,
            title_text,
            tags_text,
            time_str
        )
    
    # 输出表格
    if projects:
        console.print(table)
        console.print(f"\n找到 {len(projects)} 个项目 (搜索词: '{term}')")
    else:
        console.print(f"未找到匹配 '{term}' 的项目", style="bold yellow")

if __name__ == '__main__':
    search()