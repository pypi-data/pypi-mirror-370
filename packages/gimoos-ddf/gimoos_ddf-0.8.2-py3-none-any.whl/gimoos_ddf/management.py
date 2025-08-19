#!/usr/bin/env python
# -*- coding: utf-8 -*-

def execute_from_command_line():
    import argparse
    from pathlib import Path

    from gimoos_ddf import __version__
    from gimoos_ddf import DriverType
    from gimoos_ddf import logger

    parser = argparse.ArgumentParser(prog='gimoos_ddf', description='Gimccs 驱动开发脚手架', add_help=False)
    subparsers = parser.add_subparsers(
        title='可选命令',
        dest='cmd',
    )

    parser.add_argument('-h', '--help', help='显示帮助信息并退出', action='help')
    parser.add_argument('-v', '--version', help='显示版本信息并退出', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--path', help='工作路径', default='.')
    parser.add_argument('--lv', help='日志级别', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])

    parser_create = subparsers.add_parser('create', help='创建驱动', add_help=False)
    parser_create.add_argument('-h', '--help', help='显示帮助信息并退出', action='help')
    parser_create.add_argument('name', help='驱动名称')
    parser_create.add_argument('type', help=f'驱动类型, 可选值: {DriverType.get_values()}')

    parser_update = subparsers.add_parser('update', help='更新驱动', add_help=False)
    parser_update.add_argument('-h', '--help', help='显示帮助信息并退出', action='help')
    parser_update.add_argument('host', help='主机地址')
    parser_update.add_argument('-u', help='用户名, 默认为 root', default='root')
    parser_update.add_argument('-p', help='密码, 默认为 123456', default='123456')
    parser_update.add_argument('-i', help='忽略列表, 以空格分隔', nargs='*', default=[])

    args = parser.parse_args()

    logger.setLevel(args.lv)
    logger.debug(f'工作路径: {Path(args.path).absolute()}')

    match args.cmd:
        case 'create':
            from .create import DriverCreator

            try:
                DriverCreator().create(args.path, args.name, args.type)
            except Exception as e:
                logger.warning(f'创建驱动失败: {e}')
        case 'update':
            from .update import DriverUpdater

            DriverUpdater(args.path, args.host, args.u, args.p, args.i).update()


if __name__ == '__main__':
    execute_from_command_line()
