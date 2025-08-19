__all__ = [
    'clear_previous',
]


def clear_previous(lines: int = 1) -> None:
    print('\033[F\033[K' * lines, end='\r')
