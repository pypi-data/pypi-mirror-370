#!/usr/bin/env python3
"""
Minecraft NBT Editor CLI - Standalone script with i18n support
"""

import json
import os
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text

from core import (
    NbtFile, NbtCompound, NbtTag, NbtList, NbtPath,
    NbtSetEdit, NbtAddEdit, NbtRemoveEdit, NbtMoveEdit,
    read_nbt_file, write_nbt_file, detect_file_format,
    get_node, apply_edit_tag, search_nodes
)

from utils.i18n import get_text, get_system_language, get_language_info

console = Console()


def print_nbt_tree(tag: NbtTag, path: str = "", max_depth: int = 10, current_depth: int = 0):
    """遞歸打印 NBT 樹狀結構"""
    if current_depth >= max_depth:
        console.print(f"{'  ' * current_depth}{get_text('max_depth_reached')}")
        return
    
    if isinstance(tag, NbtCompound):
        for key, value in tag.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, (NbtCompound, NbtList)) and current_depth < max_depth - 1:
                console.print(f"{'  ' * current_depth}{get_text('folder_icon')} {key}:")
                print_nbt_tree(value, current_path, max_depth, current_depth + 1)
            else:
                console.print(f"{'  ' * current_depth}{get_text('file_icon')} {key}: {value}")
    elif isinstance(tag, NbtList):
        for i, item in enumerate(tag._value):
            current_path = f"{path}[{i}]"
            if isinstance(item, (NbtCompound, NbtList)) and current_depth < max_depth - 1:
                console.print(f"{'  ' * current_depth}{get_text('folder_icon')} [{i}]:")
                print_nbt_tree(item, current_path, max_depth, current_depth + 1)
            else:
                console.print(f"{'  ' * current_depth}{get_text('file_icon')} [{i}]: {item}")
    else:
        console.print(f"{'  ' * current_depth}{get_text('file_icon')} {tag}")


def print_nbt_table(tag: NbtTag, path: str = ""):
    """以表格形式打印 NBT 數據"""
    table = Table(title=f"NBT Data: {path}" if path else "NBT Data")
    table.add_column(get_text('result_path'), style="cyan")
    table.add_column(get_text('result_type'), style="green")
    table.add_column(get_text('result_value'), style="yellow")
    
    def add_rows(tag: NbtTag, current_path: str):
        if isinstance(tag, NbtCompound):
            for key, value in tag.items():
                new_path = f"{current_path}.{key}" if current_path else key
                if isinstance(value, (NbtCompound, NbtList)):
                    table.add_row(new_path, type(value).__name__, f"[{len(value)} {get_text('items')}]")
                    add_rows(value, new_path)
                else:
                    table.add_row(new_path, type(value).__name__, str(value))
        elif isinstance(tag, NbtList):
            for i, item in enumerate(tag._value):
                new_path = f"{current_path}[{i}]"
                if isinstance(item, (NbtCompound, NbtList)):
                    table.add_row(new_path, type(item).__name__, f"[{len(item)} {get_text('items')}]")
                    add_rows(item, new_path)
                else:
                    table.add_row(new_path, type(item).__name__, str(item))
    
    add_rows(tag, path)
    console.print(table)


@click.group()
@click.version_option(version="0.1.0")
@click.option('--language', '-l', type=click.Choice(['en', 'zh']), help='Language for output (en/zh)')
@click.option('--debug-lang', is_flag=True, help='Show language detection debug info')
def cli(language: str, debug_lang: bool):
    """Minecraft NBT 編輯器 - 支援 Java 和 Bedrock 版本 / Supporting Java and Bedrock editions"""
    if debug_lang:
        lang_info = get_language_info()
        console.print("Language Detection Info:")
        console.print(f"  Current: {lang_info['current']}")
        console.print(f"  Supported: {lang_info['supported']}")
        console.print(f"  System Locale: {lang_info['system_locale']}")
        console.print(f"  LANG: {lang_info['env_lang']}")
        console.print(f"  LANGUAGE: {lang_info['env_language']}")
        console.print(f"  LC_ALL: {lang_info['env_lc_all']}")
    
    if language:
        os.environ['MINECRAFT_NBT_LANG'] = language
    
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['tree', 'table', 'json']), default='tree', help=get_text('options.format'))
@click.option('--max-depth', '-d', type=int, default=10, help=get_text('options.max_depth'))
@click.option('--path', '-p', help=get_text('options.path'))
def view(file_path: str, format: str, max_depth: int, path: str):
    """查看 NBT 文件內容 / View NBT file content"""
    try:
        console.print(get_text('reading_file', file_path))
        
        # 檢測文件格式
        format_info = detect_file_format(file_path)
        console.print(get_text('file_format', format_info))
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        console.print(get_text('file_type', type(nbt_file.root).__name__))
        console.print(get_text('compression', nbt_file.compression))
        console.print(get_text('byte_order', 'little-endian' if nbt_file.little_endian else 'big-endian'))
        console.print(get_text('bedrock_header', nbt_file.bedrock_header))
        
        # 如果指定了路徑，只顯示該路徑的內容
        if path:
            try:
                target_tag = get_node(nbt_file.root, NbtPath(path))
                console.print(f"\n{get_text('path_content', path)}")
                if format == 'tree':
                    print_nbt_tree(target_tag, path, max_depth)
                elif format == 'table':
                    print_nbt_table(target_tag, path)
                else:  # json
                    console.print_json(json.dumps(target_tag.to_json(), indent=2, ensure_ascii=False))
            except ValueError as e:
                console.print(f"{get_text('error', e)}")
                return
        else:
            # 顯示整個文件
            console.print(f"\n{get_text('file_content')}")
            if format == 'tree':
                print_nbt_tree(nbt_file.root, "", max_depth)
            elif format == 'table':
                print_nbt_table(nbt_file.root)
            else:  # json
                console.print_json(json.dumps(nbt_file.to_json(), indent=2, ensure_ascii=False))
                
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path: str):
    """顯示 NBT 文件信息 / Display NBT file information"""
    try:
        console.print(get_text('analyzing_file', file_path))
        
        # 檢測文件格式
        format_info = detect_file_format(file_path)
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        
        # 創建信息表格
        table = Table(title=get_text('file_info'))
        table.add_column(get_text('attribute'), style="cyan")
        table.add_column(get_text('value'), style="yellow")
        
        table.add_row(get_text('file_path'), file_path)
        table.add_row(get_text('file_size'), f"{os.path.getsize(file_path)} {get_text('bytes')}")
        table.add_row(get_text('compression'), format_info['compression'])
        table.add_row(get_text('byte_order'), 'little-endian' if format_info['little_endian'] else 'big-endian')
        table.add_row(get_text('bedrock_header'), str(format_info['bedrock_header']))
        table.add_row(get_text('root_tag_type'), type(nbt_file.root).__name__)
        table.add_row(get_text('nbt_compression'), nbt_file.compression)
        table.add_row(get_text('nbt_byte_order'), 'little-endian' if nbt_file.little_endian else 'big-endian')
        table.add_row(get_text('nbt_bedrock_header'), str(nbt_file.bedrock_header))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--path', '-p', required=True, help=get_text('options.path'))
@click.option('--value', '-v', required=True, help=get_text('options.value'))
@click.option('--type', '-t', help=get_text('options.type'))
def set(file_path: str, path: str, value: str, type: str):
    """設置 NBT 路徑的值 / Set value at NBT path"""
    try:
        console.print(get_text('modifying_file', file_path))
        console.print(f"{get_text('path')}: {path}")
        console.print(f"{get_text('new_value')}: {value}")
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        
        # 創建編輯操作
        if type:
            from core.operations import auto_convert_to_nbt
            nbt_value = auto_convert_to_nbt(value, type)
        else:
            # 自動檢測類型
            from core.operations import auto_convert_to_nbt
            nbt_value = auto_convert_to_nbt(value)
        
        # 應用編輯
        edit = NbtSetEdit(NbtPath(path), nbt_value)
        apply_edit_tag(nbt_file.root, edit)
        
        # 寫回文件
        write_nbt_file(file_path, nbt_file)
        
        console.print(get_text('success'))
        
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--path', '-p', required=True, help=get_text('options.path'))
@click.option('--value', '-v', required=True, help=get_text('options.value_to_add'))
@click.option('--type', '-t', help=get_text('options.type'))
def add(file_path: str, path: str, value: str, type: str):
    """在 NBT 路徑添加新標籤 / Add new tag to NBT path"""
    try:
        console.print(get_text('adding_tag', file_path))
        console.print(f"{get_text('path')}: {path}")
        console.print(f"{get_text('value_to_add')}: {value}")
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        
        # 創建編輯操作
        if type:
            from core.operations import auto_convert_to_nbt
            nbt_value = auto_convert_to_nbt(value, type)
        else:
            # 自動檢測類型
            from core.operations import auto_convert_to_nbt
            nbt_value = auto_convert_to_nbt(value)
        
        # 應用編輯
        edit = NbtAddEdit(NbtPath(path), nbt_value)
        apply_edit_tag(nbt_file.root, edit)
        
        # 寫回文件
        write_nbt_file(file_path, nbt_file)
        
        console.print(get_text('success'))
        
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--path', '-p', required=True, help=get_text('options.path'))
def remove(file_path: str, path: str):
    """從 NBT 路徑刪除標籤 / Remove tag from NBT path"""
    try:
        console.print(get_text('removing_tag', file_path))
        console.print(f"{get_text('path')}: {path}")
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        
        # 應用編輯
        edit = NbtRemoveEdit(NbtPath(path))
        apply_edit_tag(nbt_file.root, edit)
        
        # 寫回文件
        write_nbt_file(file_path, nbt_file)
        
        console.print(get_text('success'))
        
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--value', '-v', help=get_text('options.value'))
@click.option('--type', '-t', help=get_text('options.tag_type'))
@click.option('--name', '-n', help=get_text('options.tag_name'))
def search(file_path: str, value: str, type: str, name: str):
    """搜索 NBT 文件中的標籤 / Search tags in NBT file"""
    try:
        console.print(get_text('searching_file', file_path))
        
        # 讀取 NBT 文件
        nbt_file = read_nbt_file(file_path)
        
        # 執行搜索
        results = search_nodes(nbt_file.root, value=value, tag_type=type, tag_name=name)
        
        if not results:
            console.print(get_text('no_results'))
            return
        
        # 顯示結果
        console.print(f"{get_text('found_results', len(results))}")
        for i, result in enumerate(results, 1):
            console.print(f"{i}. {get_text('result_path')}: {result['path']}")
            console.print(f"   {get_text('result_type')}: {result['tag'].type_id}")
            console.print(f"   {get_text('result_value')}: {result['tag']}")
            console.print()
        
    except Exception as e:
        console.print(f"{get_text('error', e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
