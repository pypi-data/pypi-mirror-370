# @Author: xiewenqian <int>
# @Date:   2022-10-24:10:33+08:00
# @Email:  wixb50@gmail.com
# @Last modified by:   int
# @Last modified time: 2022-10-24T16:27:14+08:00


from supermind.data.main import cli, click, command


@cli.command()
@click.help_option('-h', '--help')
@click.option('-u', '--username', 'username', required=True, help="用户名")
@click.option('-p', '--password', 'password', required=True, help="密码")
def login(username, password):
    """用户登录
    """
    return command.login(username, password)


@cli.command()
@click.help_option('-h', '--help')
def logout():
    """用户注销
    """
    return command.logout()


if __name__ == '__main__':
    cli()
