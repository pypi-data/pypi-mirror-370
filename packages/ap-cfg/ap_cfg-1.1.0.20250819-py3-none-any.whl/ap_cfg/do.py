import sys
import ut_com.dec as dec
import ut_com.com.Com as Com
import ap_cfg.parms.Parms as Parms
import ap_cfg.task.Task as Task


class Do:

    @classmethod
    @dec.handle_error
    @dec.timer
    def do(cls) -> None:
        Task.do(Com.sh_kwargs(cls, Parms, sys.argv))


if __name__ == "__main__":
    Do.do()
