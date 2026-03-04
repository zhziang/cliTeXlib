import click
import subprocess
import os

@click.command()
@click.argument('id', type=str, default='.')
def open(id):
    """
    使用 VS Code 打开指定目录。
    
    PATH: 要打开的目录路径（默认为当前目录）
    """
    try:
        # 获取绝对路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        texs_dir = os.path.join(os.path.dirname(base_path), "texs")
        abs_path = os.path.join(texs_dir, id)
        
        # 使用 VS Code 打开目录
        result = subprocess.run(['code', abs_path], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            click.echo(f"✅ 已成功在 VS Code 中打开: {abs_path}")
        else:
            click.echo(f"❌ 打开失败: {result.stderr}")
            
    except FileNotFoundError:
        click.echo("❌ 未找到 'code' 命令。请确保 VS Code 已安装并添加到 PATH 中。")
        click.echo("   提示：在 VS Code 中按 Ctrl+Shift+P，搜索 'Shell Command'，选择 'Install code command in PATH'")
    except Exception as e:
        click.echo(f"❌ 发生错误: {str(e)}")

if __name__ == '__main__':
    open()