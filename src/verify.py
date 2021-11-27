import subprocess
from concurrent.futures import ThreadPoolExecutor
import random


from crafting_calculator import get_result


def check_output(items, seed):
    result = subprocess.run(
        ["node", "new_bag.js", *[str(x) for x in items], str(seed)],
        capture_output=True,
        text=True,
    )
    item = result.stdout.strip()
    if int(item) != get_result(items, seed)[0]:
        print(f"Failure when running {items}, {seed}")
        return False
    # print(item)
    return True


def verify() -> None:
    def wrap_check_output(index):
        seed = 1302889765
        arr = [random.randint(1, 29) for _ in range(8)]
        result = check_output(arr, seed)
        return result

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(wrap_check_output, range(10000), chunksize=10)
        for result in results:
            assert result


if __name__ == "__main__":
    verify()
