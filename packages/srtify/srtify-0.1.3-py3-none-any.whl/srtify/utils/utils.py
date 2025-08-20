import os


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def fancy_headline(text, style='double'):
    """
    Create headlines with various border styles using Unicode characters.

    Args:
        text: The headline text
        style: Border style ('double', 'heavy', 'rounded', 'dashed')
    """
    # Define different border character sets
    border_styles = {
        'double': {
            'top_left': '╔', 'top_right': '╗', 'bottom_left': '╚', 'bottom_right': '╝',
            'horizontal': '═', 'vertical': '║'
        },
        'heavy': {
            'top_left': '┏', 'top_right': '┓', 'bottom_left': '┗', 'bottom_right': '┛',
            'horizontal': '━', 'vertical': '┃'
        },
        'rounded': {
            'top_left': '╭', 'top_right': '╮', 'bottom_left': '╰', 'bottom_right': '╯',
            'horizontal': '─', 'vertical': '│'
        },
        'dashed': {
            'top_left': '┌', 'top_right': '┐', 'bottom_left': '└', 'bottom_right': '┘',
            'horizontal': '┄', 'vertical': '┆'
        }
    }

    # Get the border characters for the selected style
    borders = border_styles.get(style, border_styles['double'])

    # Calculate dimensions
    text_length = len(text)
    total_width = text_length + 4  # 2 spaces padding + 2 border chars

    # Build the headline
    top_line = borders['top_left'] + borders['horizontal'] * (total_width - 2) + borders['top_right']
    middle_line = borders['vertical'] + ' ' + text + ' ' + borders['vertical']
    bottom_line = borders['bottom_left'] + borders['horizontal'] * (total_width - 2) + borders['bottom_right']

    return f"{top_line}\n{middle_line}\n{bottom_line}"