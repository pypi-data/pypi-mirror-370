from pendragon_pro import duplicate_guard

@duplicate_guard
def greet(name):
    print(f"Hello, {name}!" * 2)

greet('Jin')
greet('Jin')  # Will be detected as duplicate within 2 seconds
