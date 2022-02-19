# fyi: this doesn't work 100% yet. always returns 0 for some reason
import struct
import traceback

from capstone import *
from unicorn import *
from unicorn.arm64_const import *
from crafting_calculator.isaac_pickups import PICKUP_LIST
from crafting_calculator.isaac_rng import string_to_seed
from crafting_calculator.isaac_item_pools import ITEM_POOLS
from crafting_calculator.isaac_items import ITEMS


with open("Repentance.nro", "rb") as f:
    nro = f.read()

seed = '7bvmyw7d'


start_addr = 0x124c354000
func_end_addr = 0x124c63fcc0
pattern = 'ff0304d1e923096dfd7b0aa9fd830291fc6f0ba9fa670ca9f85f0da9f6570ea9'
bytestring = bytes.fromhex(pattern)
func_offset = nro.index(bytestring)
func_addr = func_offset + start_addr
func_size = func_end_addr - func_addr

print(f"Address at 0x{func_addr:02x}")
print(f"Function size 0x{func_size:02x}")


mem_ptr = 0x8000000000
stack_ptr = mem_ptr + 0x1000000
var_ptr = 0xa000000000
g_manager_addr = 0xc000000000
g_game_addr = 0xd000000000
emulated_func_addresses = {0x124c997e30: "operator.new", 0x124c997e10: "operator.delete", 0x124c997ed0: "memcpy", 0x124c9a0e30: "ItemPool::GetPool", 0x124c999850: "ItemConfig::GetCollectible"}
known_addresses = {}


memory_allocations = {}


def pickups_to_hex(pickup_list):
    ret = 0
    for selected_pickup in pickup_list:
        for pickup in PICKUP_LIST:
            if pickup and selected_pickup == pickup.pickup_name:
                ret <<= 8
                ret |= pickup.pickup_id
    return ret


def pc_trace(uc, address, size, user_data):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

    if address in emulated_func_addresses:
        print(f"[0x{address:02x}]\t{emulated_func_addresses[address]}")
        return
    elif address in known_addresses:
        print(f"[0x{address:02x}]\t{known_addresses[address]}")

    inst = uc.mem_read(address, size)
    formatted_hexstr = ' '.join(f'{x:02x}' for x in inst[::-1])
    for i in md.disasm(inst, address):
        print(f"[0x{i.address:02x}]\t{formatted_hexstr}\t\t{i.mnemonic}\t{i.op_str}")
        if "w20" in i.op_str or "x20" in i.op_str:
            print(f"x20: {uc.reg_read(UC_ARM64_REG_X20):02x}")

    # if address == 0x124c63fbf8:
    #     breakpoint()


def mem_read(uc, access, address, size, value, user_data):
    try:
        instr_int = 0
        for addr in range(address, address + size, 4):
            instr_int <<= 32
            mem = uc.mem_read(addr, 4)
            instr_int |= int.from_bytes(mem[::-1], byteorder="little")
        hexstr = format(instr_int, 'x')
        print(f">>> 0x{address:02x} --> 0x{hexstr}")
    except Exception:
        print(f">>> 0x{address:02x} --> unmapped memory access")
        raise


def mem_write(uc, access, address, size, value, user_data):
    # mem = uc.mem_read(address, size)
    # instr_int = int.from_bytes(mem[::-1], byteorder="little")
    hexstr = format(value, 'x')
    print(f">>> 0x{address:02x} <-- 0x{hexstr}")


def operator_new(uc, address, size, user_data):
    global mem_ptr
    retval = mem_ptr
    new_size = uc.reg_read(UC_ARM64_REG_X0)
    for i in range(0, new_size, 8):
        uc.mem_write(mem_ptr, b'\x00' * 8)
        mem_ptr += 8
    print(f"operator.new({new_size}) --> 0x{retval:02x}")
    uc.reg_write(UC_ARM64_REG_X0, retval)
    return_addr = uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC, return_addr)

    memory_allocations[retval] = {"caller": return_addr - 4, "size": new_size, "allocated": True}


def operator_delete(uc, address, size, user_data):
    obj_addr = uc.reg_read(UC_ARM64_REG_X0)
    print(f"operator.delete(0x{obj_addr:02x})")
    return_addr = uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC, return_addr)

    memory_allocations[obj_addr]["allocated"] = False


def memcpy(uc, address, size, user_data):
    dest = uc.reg_read(UC_ARM64_REG_X0)
    src = uc.reg_read(UC_ARM64_REG_X1)
    n = uc.reg_read(UC_ARM64_REG_X2)
    print(f"memcpy(0x{dest:02x}, 0x{src:02x}, {n})")
    mem = uc.mem_read(src, n)
    uc.mem_write(dest, bytes(mem))
    return_addr = uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC, return_addr)


def get_pool(uc, address, size, user_data):
    global var_ptr
    pool_id = uc.reg_read(UC_ARM64_REG_W1)
    # no idea how to interpret the itempool struct. just putting something that works.
    # itempool entries are (maybe?) id (uint32), weight (float32), decreaseby (float32), removeon (float32), next (ptr)
    item_pool_ptr = var_ptr
    var_ptr += 0x18

    item_pool = ITEM_POOLS[pool_id].get_all_items()
    for item in item_pool:
        uc.mem_write(var_ptr, int.to_bytes(item[0], length=4, byteorder="little"))
        var_ptr += 0x04
        uc.mem_write(var_ptr, struct.pack("<f", item[1]/100.0))
        var_ptr += 0x04
        uc.mem_write(var_ptr, int.to_bytes(0, length=8, byteorder="little"))
        var_ptr += 0x08
        uc.mem_write(var_ptr, int.to_bytes(var_ptr + 8, length=8, byteorder="little"))
        var_ptr += 0x08

    uc.mem_write(item_pool_ptr + 0x8, addr_to_hex(item_pool_ptr + 0x18))
    uc.mem_write(item_pool_ptr + 0x10, addr_to_hex(var_ptr))
    uc.reg_write(UC_ARM64_REG_X0, item_pool_ptr)
    return_addr = uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC, return_addr)


def get_collectible(uc, address, size, user_data):
    global var_ptr
    item_id = uc.reg_read(UC_ARM64_REG_W1)
    print(f"ItemConfig::GetCollectible({item_id})")

    if item_id not in ITEMS:
        uc.reg_write(UC_ARM64_REG_X0, 0)
        return_addr = uc.reg_read(UC_ARM64_REG_LR)
        uc.reg_write(UC_ARM64_REG_PC, return_addr)
        return

    item_config_ptr = var_ptr
    # actual size is something like 0x80 bytes, but I put 0x100 here to be safe.
    var_ptr += 0x100
    # no idea how to interpret the itemconfig struct. just putting something that works.
    # offsets 0xcc and 0xc8 somehow correspond to item quality.
    uc.mem_write(item_config_ptr + 0xcc, int.to_bytes(ITEMS[item_id].quality, length=4, byteorder="little"))
    uc.mem_write(item_config_ptr + 0xc8, b'\x00' * 4)
    uc.reg_write(UC_ARM64_REG_X0, item_config_ptr)
    return_addr = uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC, return_addr)


def emulate_func(mu, func_name, func_addr, retval):
    def hook_func(uc, address, size, user_data):
        uc.reg_write(UC_ARM64_REG_X0, retval)
        return_addr = uc.reg_read(UC_ARM64_REG_LR)
        uc.reg_write(UC_ARM64_REG_PC, return_addr)

    mu.hook_add(UC_HOOK_CODE, hook_func, begin=func_addr, end=func_addr)
    emulated_func_addresses[func_addr] = func_name


def fix_ptr(mu, name, ptr_addr, real_addr):
    mu.mem_write(ptr_addr, addr_to_hex(real_addr))
    known_addresses[real_addr] = name


def g_manager_access(uc, access, address, size, value, user_data):
    offset = address - g_manager_addr
    if access == UC_MEM_WRITE:
        print(f">>> g_manager write at offset 0x{offset:02x} (0x{address:02x}, 0x{value:02x})")
    elif access == UC_MEM_READ:
        print(f">>> g_manager read at offset 0x{offset:02x} (0x{address:02x}, 0x{value:02x})")


def g_game_access(uc, access, address, size, value, user_data):
    offset = address - g_game_addr
    if access == UC_MEM_WRITE:
        print(f">>> g_game write at offset 0x{offset:02x} (0x{address:02x}, 0x{value:02x})")
    elif access == UC_MEM_READ:
        print(f">>> g_game read at offset 0x{offset:02x} (0x{address:02x})")


def read_pool_weights(uc, base_address):
    weights = {}
    for i in range(16):
        address = base_address + 8 * i
        if uc.mem_read(address, 8) == b'\x00' * 8:
            break
        pool_id_bytes = uc.mem_read(address, 4)
        weight_bytes = uc.mem_read(address + 4, 4)
        pool_id = int.from_bytes(pool_id_bytes, byteorder='little')
        weight = struct.unpack("<f", weight_bytes)[0]
        weights[pool_id] = weight
    return {x: weights[x] for x in sorted(weights)}


pickup_int = pickups_to_hex([
    "Red Heart",
    "Red Heart",
    "Soul Heart",
    "Soul Heart",
    "Penny",
    "Nickel",
    "Nickel",
    "Key"
])


def addr_to_hex(addr):
    return int.to_bytes(addr, length=8, byteorder="little")


try:
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

    mu.mem_map(start_addr, 128 * 1024 * 1024)
    mu.mem_map(mem_ptr, 64 * 1024 * 1024)
    mu.mem_map(g_manager_addr, 1024 * 1024)
    mu.mem_map(g_game_addr, 1024 * 1024)
    mu.mem_map(var_ptr, 1024 * 1024)
    mu.mem_write(start_addr, nro)
    mu.mem_write(mem_ptr, b'\x00' * 64 * 1024 * 1024)
    mu.mem_write(g_manager_addr, b'\x00' * 1024 * 1024)
    mu.mem_write(g_game_addr, b'\x00' * 1024 * 1024)
    mu.mem_write(var_ptr, b'\x00' * 1024 * 1024)

    # PTR_g_Manager
    mu.mem_write(0x124cdb1d60, b'\x00\x00\x00\x00\xc0\x00\x00\x00')
    mu.mem_write(g_manager_addr, b'\x00\x00\x00\x00\xc0\x00\x00\x00')
    # total item count?
    mu.mem_write(g_manager_addr + 0x34858, int.to_bytes(1, length=8, byteorder='little'))
    mu.mem_write(g_manager_addr + 0x34860, int.to_bytes(len(ITEMS), length=8, byteorder='little'))

    # PTR_g_Game
    mu.mem_write(0x124cdb1db0, b'\x00\x00\x00\x00\xd0\x00\x00\x00')
    mu.mem_write(g_game_addr, b'\x00\x00\x00\x00\xd0\x00\x00\x00')
    # rng state?
    mu.mem_write(g_game_addr + 0x2528c, int.to_bytes(g_game_addr + 0x2528c + 8, length=8, byteorder='little'))
    mu.mem_write(g_game_addr + 0x2528c + 8, int.to_bytes(string_to_seed(seed), length=8, byteorder='little'))

    # manually fix pointers
    fix_ptr(mu, name="RNG::RNG", ptr_addr=0x124cda38a8, real_addr=0x124c77cf1c)
    fix_ptr(mu, name="RNG::s_Shifts", ptr_addr=0x124cdb29a8, real_addr=0x124cbc8128)
    fix_ptr(mu, name="RNG::Next", ptr_addr=0x124cda38e0, real_addr=0x124c77d020)
    fix_ptr(mu, name="RNG::Random", ptr_addr=0x124cda38f0, real_addr=0x124c77d07c)
    fix_ptr(mu, name="RNG::~RNG", ptr_addr=0x124cda38b8, real_addr=0x124c77cf78)

    # setup pickup array
    pickup_array_ptr = var_ptr
    mu.mem_write(var_ptr, b'\x08\x00\x00\x00\xa0\x00\x00\x00')
    var_ptr += 8
    mu.mem_write(var_ptr, int.to_bytes(pickup_int, length=8, byteorder='little'))
    var_ptr += 8

    # Entity_Player*
    mu.reg_write(UC_ARM64_REG_X0, 0)
    # pickups
    mu.reg_write(UC_ARM64_REG_X1, pickup_array_ptr)
    # param_2 (idk? maybe set to 1 when ignoring unlocks?)
    mu.reg_write(UC_ARM64_REG_X2, 1)

    # initialize stack
    mu.reg_write(UC_ARM64_REG_SP, stack_ptr)

    # Set FPEN on CPACR_EL1 to access vector registers
    # https://github.com/unicorn-engine/unicorn/issues/940
    val = mu.reg_read(UC_ARM64_REG_CPACR_EL1)
    val |= 0x300000
    mu.reg_write(UC_ARM64_REG_CPACR_EL1, val)

    # emulate functions
    emulate_func(mu, func_name="ItemConfig::CraftingRecipeToU64", func_addr=0x124c9a1110, retval=pickup_int)
    emulate_func(mu, func_name="ItemConfig::GetCraftingOutput", func_addr=0x124c9a1120, retval=0)
    emulate_func(mu, func_name="PersistentGameData::Unlocked", func_addr=0x124c999150, retval=1)
    mu.hook_add(UC_HOOK_CODE, operator_new, begin=0x124c997e30, end=0x124c997e30)
    mu.hook_add(UC_HOOK_CODE, operator_delete, begin=0x124c997e10, end=0x124c997e10)
    mu.hook_add(UC_HOOK_CODE, memcpy, begin=0x124c997ed0, end=0x124c997ed0)
    mu.hook_add(UC_HOOK_CODE, get_pool, begin=0x124c9a0e30, end=0x124c9a0e30)
    mu.hook_add(UC_HOOK_CODE, get_collectible, begin=0x124c999850, end=0x124c999850)

    # install hooks
    mu.hook_add(UC_HOOK_CODE, pc_trace, begin=0, end=0xffffffffffffffff)
    mu.hook_add(UC_HOOK_MEM_READ, mem_read, begin=0, end=0xffffffffffffffff)
    mu.hook_add(UC_HOOK_MEM_READ_INVALID, mem_read, begin=0, end=0xffffffffffffffff)
    mu.hook_add(UC_HOOK_MEM_WRITE, mem_write, begin=0, end=0xffffffffffffffff)
    mu.hook_add(UC_HOOK_MEM_WRITE_INVALID, mem_write, begin=0, end=0xffffffffffffffff)
    mu.hook_add(UC_HOOK_MEM_READ, g_manager_access, begin=g_manager_addr, end=g_manager_addr + (1024 * 1024))
    mu.hook_add(UC_HOOK_MEM_WRITE, g_manager_access, begin=g_manager_addr, end=g_manager_addr + (1024 * 1024))
    mu.hook_add(UC_HOOK_MEM_READ, g_game_access, begin=g_game_addr, end=g_game_addr + (1024 * 1024))
    mu.hook_add(UC_HOOK_MEM_WRITE, g_game_access, begin=g_game_addr, end=g_game_addr + (1024 * 1024))

    mu.emu_start(func_addr, func_end_addr)

    # pool weights
    print(read_pool_weights(mu, 0x8000000078))
    print(f"Item ID: {mu.reg_read(UC_ARM64_REG_X0)}")
except UcError as e:
    traceback.print_exc()
