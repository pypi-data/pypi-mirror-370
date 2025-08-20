from .util import format_parsed_type, parse_type_str


def test_parse() -> None:
    def check(input: str) -> None:
        pt = parse_type_str(input)
        fmt = format_parsed_type(pt)
        assert input == fmt
        print(input, "=", fmt)

    check("Simple.path.more")
    check("path.List<Integer>")
    check("path.List<Integer,String>")
    check("path.List<ObjectId<Integer>,String>")
    check("Some<My.Path>")
    check("some.sub<Path<with.bits>,And<more>>")


test_parse()
