import json
import ida_dbg
import ida_bytes
import idautils
import ida_strlist
import idaapi
import idc
import ida_idd
import struct

XREF_TYPE2STR = {idaapi.fl_U: "User Defined",
                 idaapi.fl_CF: "Far Call",
                 idaapi.fl_CN: "Near Call",
                 idaapi.fl_JF: "Far Jump",
                 idaapi.fl_JN: "Near Jump"}


def find_xrefs_from(func_ea):
    xrefs = []

    for item in idautils.FuncItems(func_ea):

        ALL_XREFS = 0
        for ref in idautils.XrefsFrom(item, ALL_XREFS):

            if ref.type not in XREF_TYPE2STR:
                continue

            if ref.to in idautils.FuncItems(func_ea):
                continue

            disas = idc.GetDisasm(item)
            # curr_xref = XrefFrom( item, ref.to, ref.type, disas )
            xrefs.append(ref)

    return xrefs


def locate_func():
    str_opts = ida_strlist.get_strlist_options()
    str_opts.minlen = 10
    str_opts.display_only_existing_strings = True

    candidate_xrefs = []
    for s in idautils.Strings():
        if str(s) == "RNG: Invalid ShiftIdx\n":
            candidate_xrefs.extend(idautils.XrefsTo(s.ea))
            break

    for s in idautils.Strings():
        if str(s) == "RNG Seed is zero!\n":
            for xref in idautils.XrefsTo(s.ea):
                for candidate_xref in candidate_xrefs:
                    if idaapi.get_func(xref.frm) == idaapi.get_func(candidate_xref.frm):
                        return idaapi.get_func(xref.frm)
    raise ValueError("Couldn't find func")


def locate_seed_ptr(func):
    for s in idautils.Strings():
        if str(s) == "Error: Game Start Seed was not set.\n":
            for xref in idautils.XrefsTo(s.ea):
                if idaapi.get_func(xref.frm) != func:
                    continue
                last_inst_ea = idc.prev_head(xref.frm)
                penultimate_inst_ea = idc.prev_head(last_inst_ea)
                while last_inst_ea >= func.start_ea:
                    if idc.print_insn_mnem(last_inst_ea) == 'mov' and idc.get_operand_type(last_inst_ea, 1) == 4:
                        if idc.print_insn_mnem(penultimate_inst_ea) == 'mov' and idc.get_operand_type(
                                penultimate_inst_ea, 1) == 2:
                            print(hex(last_inst_ea))
                            offset = idc.get_operand_value(last_inst_ea, 1)
                            base_addr = idc.get_operand_value(penultimate_inst_ea, 1)
                            return idaapi.get_dword(base_addr) + offset

                    last_inst_ea = penultimate_inst_ea
                    penultimate_inst_ea = idc.prev_head(penultimate_inst_ea)
    raise ValueError("Couldn't find ptr")


def scan_for_item_unlock(craft_func):
    xrefs = find_xrefs_from(craft_func.start_ea)
    xrefs = {xref.to for xref in xrefs}

    candidates = []
    for func_ea in xrefs:
        func = idaapi.get_func(func_ea)
        if func is None:
            continue
        ea = func.start_ea
        while ea < func.end_ea:
            ea = idc.next_head(ea)
            mnem = idc.print_insn_mnem(ea)
            if mnem != "cmp":
                continue
            if not (idc.get_operand_type(ea, 0) == 1 and idc.get_operand_type(ea, 1) == 5):
                continue
            if not idc.get_operand_value(ea, 1) == 0x27e:
                continue
            candidates.append(func_ea)
            break
    assert len(candidates) == 1, "Found either zero or more than one candidate"
    return candidates[0]


def scan_for_achievement_array(craft_func):
    ea = craft_func.start_ea
    while ea < craft_func.end_ea:
        ea = idc.next_head(ea)
        mnem = idc.print_insn_mnem(ea)
        if mnem != "cmp":
            continue
        if not (idc.get_operand_type(ea, 0) == 1 and idc.get_operand_type(ea, 1) == 5):
            continue
        if not idc.get_operand_value(ea, 1) == 0x27e:
            continue
        test_ea = ea
        for _ in range(10):
            test_ea = idc.next_head(test_ea)
            if not (idc.print_insn_mnem(test_ea) == "mov" and idc.get_operand_type(test_ea,
                                                                                   0) == 1 and idc.get_operand_type(
                    test_ea, 1) == 2):
                continue
            base_addr = idc.get_operand_value(test_ea, 1)
            offset = idc.get_operand_value(idc.next_head(test_ea), 0)
            return idaapi.get_dword(base_addr) + offset
    raise ValueError("couldn't find ptr")


def patch_func(func, retval, argc):
    if retval is not None:
        shellcode = b'\xb8' + struct.pack("<i", retval) + b'\xc2' + struct.pack("<h", argc * 4)
        ida_bytes.patch_bytes(func, shellcode)
        return True
    else:
        for i in range(8):
            ida_bytes.revert_byte(func + i)
        return False


def build_test_cases():
    craft_func = locate_func()
    seed_ptr = locate_seed_ptr(craft_func)
    # item_unlock_func = scan_for_item_unlock(craft_func)
    achievement_ptr = scan_for_achievement_array(craft_func)

    # Set up Appcall stuff
    decl = idc.parse_decl('int __stdcall get_crafting_output(byte*)', 0)
    idc.apply_type(craft_func.start_ea, decl, 0)
    buf = ida_idd.Appcall.buffer(b'\x00' * 8)

    # Write seed

    with open(r"bindingofisaac/tests/test_cases/binary_inputs.json", "r") as f:
        cases = json.load(f)

    output_cases = []
    # patch_func(item_unlock_func, 1, 1)
    for case in cases:
        seed = case["seed"]
        pickups = case["pickups"]
        achievement_id = case.get("achievement_id")
        ida_dbg.write_dbg_memory(seed_ptr, struct.pack("<I", seed))
        buf.value = bytes(pickups)

        new_case = case.copy()

        if achievement_id:
            ida_dbg.write_dbg_memory(achievement_ptr + achievement_id, b'\x01')

        new_case["output"] = ida_idd.Appcall["get_crafting_output"](buf)
        new_case["unlocked"] = True
        output_cases.append(new_case)

        if achievement_id:
            ida_dbg.write_dbg_memory(achievement_ptr + achievement_id, b'\x00')

            new_case = case.copy()
            new_case["output"] = ida_idd.Appcall["get_crafting_output"](buf)
            new_case["unlocked"] = False
            output_cases.append(new_case)
            ida_bytes.revert_byte(achievement_ptr + achievement_id)

    with open(r"bindingofisaac/tests/test_cases/pc178.json", "w") as f:
        json.dump(output_cases, f)
