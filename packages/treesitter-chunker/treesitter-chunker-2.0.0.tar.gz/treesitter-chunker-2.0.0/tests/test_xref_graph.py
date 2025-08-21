from chunker.graph.xref import build_xref
from chunker.types import CodeChunk


def make_chunk(
    node_type: str,
    name: str,
    imports: list[str] | None = None,
    calls: list[str] | None = None,
    inherits: list[str] | None = None,
    references: list[str] | None = None,
):
    md = {
        "signature": {"name": name},
    }
    if imports:
        md["imports"] = imports
    if calls:
        md["calls"] = calls
    if inherits:
        md["inherits"] = inherits
    if references:
        md["references"] = references
    return CodeChunk(
        language="python",
        file_path="/tmp/x.py",
        node_type=node_type,
        start_line=1,
        end_line=3,
        byte_start=0,
        byte_end=10,
        parent_context="module",
        content="def f():\n  pass\n",
        metadata=md,
    )


def test_xref_builds_edges_from_metadata_and_parent():
    parent = make_chunk("class_definition", "Base")
    child = make_chunk("method_definition", "foo")
    child.parent_chunk_id = parent.node_id

    imported = make_chunk("function_definition", "util")
    importer = make_chunk("function_definition", "caller", imports=["util"])

    callee = make_chunk("function_definition", "g")
    caller = make_chunk("function_definition", "f", calls=["g"])

    derived = make_chunk("class_definition", "Child", inherits=["Base"])

    ref_target = make_chunk("function_definition", "h")
    referrer = make_chunk("function_definition", "ref", references=["h"])

    nodes, edges = build_xref(
        [
            parent,
            child,
            imported,
            importer,
            callee,
            caller,
            derived,
            ref_target,
            referrer,
        ],
    )

    def has_edge(src, dst, typ):
        return any(
            e["src"] == src and e["dst"] == dst and e["type"] == typ for e in edges
        )

    assert has_edge(parent.node_id, child.node_id, "DEFINES")
    assert has_edge(importer.node_id, imported.node_id, "IMPORTS")
    assert has_edge(caller.node_id, callee.node_id, "CALLS")
    assert has_edge(derived.node_id, parent.node_id, "INHERITS")
    assert has_edge(referrer.node_id, ref_target.node_id, "REFERENCES")
