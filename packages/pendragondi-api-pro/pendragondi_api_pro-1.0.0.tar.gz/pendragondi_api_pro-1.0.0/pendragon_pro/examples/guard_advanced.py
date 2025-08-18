from pendragon_pro import duplicate_guard_pro

@duplicate_guard_pro(window_ms=5000, capture_args=True, stack_depth=8)
def query_db(q, user=None):
    print(f"Executing {q} for {user}")

query_db('SELECT * FROM users', user='joe')
query_db('SELECT * FROM users', user='joe')  # Duplicate within 5s window
