from iccore.runtime import ctx


def test_runtime_context():

    # check defaults to non dry run
    assert not ctx.is_dry_run()
    assert ctx.can_read()
    assert ctx.can_modify()

    # read only mode
    ctx.set_is_read_only()
    assert ctx.can_read()
    assert not ctx.can_modify()
    assert ctx.is_dry_run()

    # full dry run mode
    ctx.set_is_dry_run()
    assert not ctx.can_read()
    assert not ctx.can_modify()

    # command buffer
    ctx.add_cmd("test_cmd")
    assert ctx.get_buffer()[-1] == "test_cmd"

    # Restore default state
    ctx.set_is_dry_run(0)
    ctx.clear_buffer()
