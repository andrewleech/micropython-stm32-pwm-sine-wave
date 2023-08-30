import fnmatch
import re
import sys
from collections import OrderedDict
from functools import partial
from pathlib import Path
from unittest import mock

# Stub in cpython mocks for the micropython modules included in the template below.
sys.modules["uctypes"] = mock.MagicMock()
sys.modules["micropython"] = mock.MagicMock()


# TEMPLATE MARK
import uctypes
from micropython import const


class Register:
    def __init__(self, addr) -> None:
        if not hasattr(self.__class__, "__regs__"):
            # We have register definitions defined on Register subclasses, which are used
            # to create the uctypes.struct instances.
            # These attributes get in the way of reading the struct attrs though, so move
            # them to an class.__regs__ dict for referencing and delete from the class itself.
            __regs__ = {k: v for k, v in self.__class__.__dict__.items() if not k.startswith("_")}
            setattr(self.__class__, "__regs__", __regs__)
            for k in __regs__:
                delattr(self.__class__, k)

        self.__addr__ = addr

        descriptor = {
            k: (v | uctypes.UINT32) for k, v in self.__class__.__regs__.items()  # type: ignore
        }
        self.__struct__ = uctypes.struct(addr, descriptor)

    def __reg_addr__(self, register: str):
        return self.__addr__ + self.__regs__[register]

    def __repr__(self):
        return f"<{self.__class__.__name__} 0x{self.__addr__:x}>"

    def __dir__(self):
        return [k for k in self.__regs__]

    def __inspect__(self):
        print(self.__class__.__name__)
        struct = self.__struct__
        for k, v in sorted(self.__regs__.items(), key=lambda t: t[1]):
            val = getattr(struct, k)
            print(f"{k : 10} (0x{v:04x}):  0x{val:04x}")

    def __getattr__(self, __name: str):
        if __name.startswith("_"):
            raise AttributeError(__name)

        v = getattr(self.__struct__, __name)
        return v

    def __setattr__(self, __name: str, __value) -> None:
        if __name.startswith("_"):
            object.__setattr__(self, __name, __value)
        else:
            setattr(self.__struct__, __name, __value)


# TEMPLATE MARK


def __register_file_generator(stm_cpu, requirements):
    """
    This function can be run from cpython with the stm hal cpu name
    for the target processor to generate the register definitions required.
    eg. stm32wb55
    """

    project_dir = Path(__file__).parent.resolve()
    stm32lib = project_dir / "stm32lib"

    include_dir = stm32lib / "CMSIS" / "STM32WBxx" / "Include"
    if not include_dir.exists():
        raise ValueError("stm32lib submodule needs to be checked out")

    includes = list(include_dir.glob(f"{stm_cpu}*"))
    if len(includes) > 1:
        names = [f.stem for f in includes]
        raise ValueError(f"{stm_cpu} isn't specific enough, choose from: {names}")
    elif not includes:
        raise ValueError(f"No matching header found, see list in {include_dir}")
    else:
        filename = includes[0]

    print(f"Generating register definitions from {filename.relative_to(project_dir)}")

    cpu = filename.stem[0:7]

    hal_include = stm32lib / f"{cpu.upper()}xx_HAL_Driver" / "Inc"
    # header_ll_dma = hal_include / f"{cpu}xx_ll_dma.h"
    # header_ll_dmamux = hal_include / f"{cpu}xx_ll_dmamux.h"
    header_ll_system = hal_include / f"{cpu}xx_ll_system.h"
    if not header_ll_system.exists():
        raise SystemExit(f"Can't find matching system headers: {header_ll_system}")

    system_header = header_ll_system.read_text()
    expected_dev_id = re.findall(r"the device ID is (0x[0-9a-fA-F]+)", system_header)[0]

    content = filename.read_text()
    for header in hal_include.iterdir():
        if header.suffix == ".h":
            content += header.read_text()
    # content += header_ll_dmamux.read_text()

    template = Path(__file__).read_text().split("# TEMPLATE MARK")[1]

    output = Path(__file__).parent / "signal_gen" / f"_stm_registers.py"
    out_content = [
        "# AUTOGENERATED from:",
        f"# $ python {Path(__file__).name} {filename.relative_to(stm32lib.parent)}",
        "",
        template,
    ]
    out_elements = OrderedDict()

    # Track text that contains register names we need to filter for
    __desired__ = [partial(fnmatch.fnmatch, pat='DBGMCU*')]
    if Path(requirements).exists():
        contents = Path(requirements).read_text()
        __desired__.append(lambda v: v in contents)
    else:
        for field in requirements.split(" "):
            if "*" in field:
                __desired__.append(
                    partial(fnmatch.fnmatch, pat=field)
                )
            else:
                __desired__.append(
                    partial(lambda v, f: f in v, f=field)
                )

    # Parse #defines in the header files

    register_instances = OrderedDict()
    register_instances_content = ""
    defines = {}
    for line in re.findall(r"#define (\S+) +(.+)\n", content):
        name, details = line
        if "(" in name:
            # ignore macros
            continue

        if details.endswith("\\"):
            continue
        comment = ""
        for comments in re.findall(r"(/\*!?<?(.*?)\*/)", details):
            comment = "  # " + comments[1].strip()
            details = details.split("/*")[0]
            break

        value = details.strip()
        if not value:
            continue

        # Remove UL suffix from numbers
        value = re.sub(r"(0x[a-fA-F0-9]+)[UL]*", r"\1", value)
        value = re.sub(r"([0-9]+)[uUL]*", r"\1", value)
        # Parse out any type casting
        value = re.sub(r"\(uint\d+_t\)(.*)", r"\1", value)
        if value.startswith("(") and value.endswith(")"):
            value = value[1:-1]

        # The headers have bitfields broken out into 3 lines. Optimise them when possible...
        if name.endswith("_Pos"):
            defines[name] = (value, comment)
            continue

        elif name.endswith("_Msk"):
            pos = name.replace("_Msk", "_Pos")
            if pos in value and pos in defines:
                pos_value, pos_comment = defines[pos]
                value = value.replace(pos, pos_value)
                comment += pos_comment
            defines[name] = (value, comment)
            continue

        for ptn in re.findall(r"(\S+_(Msk|Pos))", value):
            if ptn[0] in defines:
                ptn_value, ptn_comment = defines[ptn[0]]
                value = value.replace(ptn[0], ptn_value)
                comment += ptn_comment

        if "TypeDef *)" in value:
            for details in re.findall(r"\((\S+TypeDef) *\*\) (\S+)", value):
                value = f"{details[0]}({details[1]})"
                break
            if any((check(name) for check in __desired__)):
                register_instances[name] = f"{name} = {value}{comment}"
                register_instances_content += value
        else:
            if "*" in value:
                value = "# " + value
            out_elements[name] = f"{name} = const({value}){comment}"

    # Register TypeDef's
    # out_content.append("")

    registers = []

    registers_h = re.findall(
        r"((@brief (.+)\n *\*/\n)?typedef struct\n\{\n(.*uint32_t *\S+ *; */\*!<.*\*/\n\n?)+\} ?(\S+TypeDef);)",
        content,
    )

    for reg in registers_h:
        name = reg[4]
        fields = []
        i_off = 0
        for i, row in enumerate(re.findall("\n.*uint32_t *(\S+) *;( */\*!<(.*)\*/)?", reg[0])):
            field = row[0]
            if "[" in field:
                # Don't support arrays, just fix index
                i_off += int(field.split("[")[-1].split("]")[0]) - 1
                field = "# " + field
            if field.startswith("RESERVED"):
                field = "# " + field
            index = (i + i_off) * 4
            comment = row[1].strip().replace("  ", " ")
            fields.append((field, index, comment))

        title = reg[2] or name

        if name in register_instances_content or any((check(name) for check in __desired__)):
            registers.extend(
                [
                    "",
                    f"# {title}",
                    f"class {name}(Register):",
                ]
                + [f"    {fn}: int = 0x{i:02X}  # {c}" for fn, i, c in fields]
            )

    keep = set()
    keep_content = ""
    last_keep_len = None
    while last_keep_len != len(keep):
        last_keep_len = len(keep)
        for name, val in out_elements.items():
            if name in register_instances_content or name in keep_content or any((check(name) for check in __desired__)):
                keep.add(name)
                keep_content += val

    out_content.append("")

    for name, elem in out_elements.items():
        if name in keep:
            out_content.append(elem)

    out_content.append("")
    out_content.extend(registers)

    out_content.append("")
    out_content.extend(register_instances.values())

    out_content.append("")
    out_content.extend([
        f"",
        f"__dev_id = DBGMCU.IDCODE & 0xFFF",
        f"if __dev_id != {expected_dev_id}:",
        f'    raise RuntimeError(f"{output.name} was generated for {cpu} ({expected_dev_id}), running on {{__dev_id}}")',
        f"",
    ])

    Path(output).write_text("\n".join(out_content))
    print(f"Written: {output}")


if __name__ == "__main__":
    import sys

    __register_file_generator(sys.argv[1], sys.argv[2])
    sys.exit()
