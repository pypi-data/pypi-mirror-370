from speak2py.session import parse_basic

def test_parse_load_head_describe_alias():
    cmd = 'read "data/iris.csv" and head 5'
    plan = parse_basic(cmd)
    assert plan.op == "load_head"
    assert plan.args["path"].endswith("data/iris.csv")
    assert plan.args["n"] == 5
    assert plan.alias is None

    cmd2 = 'load "data/iris.csv" and describe as iris'
    plan2 = parse_basic(cmd2)
    assert plan2.op == "load_describe"
    assert plan2.alias == "iris"

def test_parse_histogram():
    cmd = 'read "data/nums.csv" and plot a histogram of value'
    plan = parse_basic(cmd)
    assert plan.op == "load_plot_hist"
    assert plan.args["col"] == "value"
