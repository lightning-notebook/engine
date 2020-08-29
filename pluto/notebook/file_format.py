from pluto.notebook.notebook import Notebook
from pluto.cell import Cell
from pluto.run_order import RunOrder


intro_message = '\
# ♇ version 0.1.0\n\
# This is a valid Python file, but it\'s best viewed using Pluto!\n\
# Get Pluto from https://github.com/malyvsen/Pluto.py\n\
'
cell_order_header = '# ♇ cell order:'
cell_prefix = '# ♇ cell '


def to_file_format(notebook):
    run_order = RunOrder.from_notebook(notebook)
    save_order = run_order.order + [cell for cell in run_order.errors if cell not in run_order.order]
    cell_info = '\n'.join(f'{cell_prefix}{str(cell.id)}\n{cell.code}\n' for cell in save_order)
    order_info = ''.join(f'{cell_prefix}{str(cell.id)}\n' for cell in notebook.cells)
    return '\n'.join([intro_message, cell_info, cell_order_header, order_info])


def from_file_format(file_format):
    assert intro_message in file_format
    no_intro = file_format.replace(intro_message, '')
    cell_info, order_info = no_intro.split(cell_order_header)
    cell_blocks = split_cell_blocks(cell_info)
    cell_ids = order_info.replace(cell_prefix, '').splitlines()[1:]
    assert len(cell_blocks) == len(cell_ids)
    return Notebook(cells=[Cell(id=cell_id, code=cell_blocks[cell_id]) for cell_id in cell_ids])


def split_cell_blocks(cell_info):
    blocks_with_ids = cell_info.split(cell_prefix)[1:]
    block_lines = [block.split('\n') for block in blocks_with_ids]
    return {lines[0]: '\n'.join(lines[1:-2]) for lines in block_lines}


Notebook.to_file_format = to_file_format
Notebook.from_file_format = from_file_format