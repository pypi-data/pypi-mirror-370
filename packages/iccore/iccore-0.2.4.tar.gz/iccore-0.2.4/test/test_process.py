from iccore.system import process
from iccore.runtime import ctx


def test_process_run():

    cmd = "echo 'hello world'"
    result = process.run(cmd)

    assert result.strip() == "hello world"


def test_process_dry_run():

    ctx.set_is_dry_run()
    cmd = "no_run"
    result = process.run(cmd)

    assert ctx.get_buffer()[-1] == "run no_run"

    ctx.set_is_dry_run(0)
