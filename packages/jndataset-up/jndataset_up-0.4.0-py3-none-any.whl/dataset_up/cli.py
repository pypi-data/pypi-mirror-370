import click

from dataset_up.config.constants import SERVER_URL
from dataset_up.client.Client import Client
from dataset_up.client.AuthClient import auth_client
from dataset_up.uploader.uploader import Uploader
from dataset_up.update.update_check import update_check
from dataset_up.utils.interrupt_utils import register_signal_handler
from dataset_up.utils.output_format import print_file_list
from dataset_up.utils.system_utils import stop_dataset_up_process

def validate_input(ctx, param, value):
    if not value or value.strip() == "":
        raise click.BadParameter("输入不能为空或空格")
    return value


@click.group()
def cli():
    pass


@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--source-path", required=True, help="本地文件路径",callback=validate_input)
@click.option("--target-path", default="/", help="目标路径",callback=validate_input)
@click.option("--version", default="master", help="版本号",callback=validate_input)
def upload_file(dataset_id, source_path, target_path, version):
    """上传单个文件"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.upload_file(source_path, target_path)
    except Exception as e:
        click.echo(f"上传文件失败: {e}")


@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--source-path", required=True, help="本地文件夹路径",callback=validate_input)
@click.option("--target-path", default="/",  required = True,help="目标路径",callback=validate_input)
@click.option("--version", default="master", help="版本号",callback=validate_input)
def upload_folder(dataset_id, source_path, target_path, version):
    """上传整个文件夹"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.upload_folder(source_path, target_path)
    except Exception as e:
        click.echo(f"上传文件夹失败: {e}")
        
@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master" ,help="版本号",callback=validate_input)
@click.option("--dir", required = True, help="目标目录",callback=validate_input)
def mkdir(dataset_id, version, dir):
    """新建目录"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.mkdir(dir)
        click.echo(f"创建目录{dir}成功")
    except Exception as e:
        click.echo(f"创建目录{dir}失败: {e}")

@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master" ,help="版本号",callback=validate_input)
@click.option("--dir", required = True, help="目标目录",callback=validate_input)
def rmdir(dataset_id, version, dir):
    """删除目录"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.deleteDir(dir)
        click.echo(f"删除目录{dir}成功")
    except Exception as e:
        click.echo(f"删除目录失败: {e}")
        

@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master" ,help="版本号",callback=validate_input)
@click.option("--file", required = True, help="目标文件",callback=validate_input)
def delete_file(dataset_id, version, file):
    """删除文件"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.deleteFile(file)
        click.echo(f"删除文件{file}成功")
    except Exception as e:
        click.echo(f"删除文件{file}失败: {e}")


@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master", help="版本",callback=validate_input)
@click.option("--dir", default="/", help="目标路径",callback=validate_input)
def list(dataset_id: str, version: str, dir: str):
    """列出目录下所有文件详情"""
    try:
        update_check()
        register_signal_handler()
        client = Client(host=SERVER_URL)
        uploader = Uploader(client, dataset_id, version)
        files = uploader.list(dir)
        print_file_list(files)
    except Exception as e:
        click.echo(f"列出目录{dir}失败: {e}")


@cli.command()
@click.option("--ak", required=True, help="Access Key")
@click.option("--sk", required=True, help="Secret Key")
def login(ak: str, sk: str):
    """登录"""
    try:
        auth_client.login(ak, sk)
        click.echo("登录成功")
    except Exception as e:
        click.echo(f"登录失败,请检查AK/SK是否输入正确! msg: {e}")


@cli.command()
def stop_running_uploading_process():
    """停止正在运行的上传进程"""
    stop_dataset_up_process()


def main():
    cli()


if __name__ == "__main__":
    main()