import re
from typing import List
from .models import Model, Lake, Table, Column
from .exceptions import CMetaParseError

_CONTAINER_RE = re.compile(
    r"""^(?P<indent>\s*)
        (?P<name>[^\[\]:]+)
        (?:\[(?P<desc>(?:\\\]|\\<|\\>|[^\\\]])*)\])?
        :\s*$
    """,
    re.VERBOSE,
)

_COLUMN_RE = re.compile(
    r"""^(?P<indent>\s*)\*\s
        (?P<name>[^\[<\s]+)
        (?:<(?P<dtype>[^>]+)>)?
        (?:\[(?P<desc>(?:\\\]|\\<|\\>|[^\\\]])*)\])?
        \s*$
    """,
    re.VERBOSE,
)


def _unescape(text: str | None) -> str | None:
    if text is None:
        return None
    return text.replace(r"\]", "]").replace(r"\<", "<").replace(r"\>", ">")


def parse_cmeta(text: str) -> Model:
    """
    Parse CMeta v1 text into a Model.
    - Lakes: indent level 0, container line ends with ':'
    - Tables: indent level 2 spaces
    - Columns: indent level 4 spaces, lines start with '* '
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip() != ""]
    lakes: List[Lake] = []
    current_lake: Lake | None = None
    current_table: Table | None = None

    def indent_level(s: str) -> int:
        # 2 spaces per level
        return len(s) // 2

    for i, line in enumerate(lines, start=1):
        m_cont = _CONTAINER_RE.match(line)
        if m_cont:
            name = m_cont.group("name").strip()
            desc = _unescape(m_cont.group("desc"))
            lvl = indent_level(m_cont.group("indent"))
            if lvl == 0:
                current_lake = Lake(name=name, description=desc, tables=[])
                lakes.append(current_lake)
                current_table = None
            elif lvl == 1:
                if current_lake is None:
                    raise CMetaParseError(f"Table without lake at line {i}: {line}")
                current_table = Table(name=name, description=desc, columns=[])
                current_lake.tables.append(current_table)
            else:
                raise CMetaParseError(f"Unexpected container indent at line {i}: {line}")
            continue

        m_col = _COLUMN_RE.match(line)
        if m_col:
            if current_table is None:
                raise CMetaParseError(f"Column without table at line {i}: {line}")
            name = m_col.group("name").strip()
            dtype = (m_col.group("dtype") or "string").strip()
            desc = _unescape(m_col.group("desc"))
            lvl = indent_level(m_col.group("indent"))
            if lvl != 2:
                raise CMetaParseError(
                    f"Columns must be indented at level 2 (4 spaces) at line {i}: {line}"
                )
            current_table.columns.append(Column(name=name, data_type=dtype, description=desc))
            continue

        raise CMetaParseError(f"Unrecognized line at {i}: {line}")

    return Model(lakes=lakes)


def to_cmeta(model: Model) -> str:
    """
    Serialize Model -> CMeta v1 text.
    """
    out: List[str] = []

    def esc(s: str | None) -> str:
        if not s:
            return ""
        s = s.replace("]", r"\]").replace("<", r"\<").replace(">", r"\>")
        return f"[{s}]"

    for lake in model.lakes:
        out.append(f"{lake.name}{esc(lake.description)}:")
        for table in lake.tables:
            out.append(f"  {table.name}{esc(table.description)}:")
            for col in table.columns:
                dtype = f"<{col.data_type}>" if col.data_type else ""
                desc = esc(col.description)
                out.append(f"    * {col.name}{dtype}{desc}")
    return "\n".join(out) + "\n"
