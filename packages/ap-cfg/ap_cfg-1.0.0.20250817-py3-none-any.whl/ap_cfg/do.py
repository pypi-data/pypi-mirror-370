import sys
import ut_com.dec as dec
import ut_com.com.Com as Com
import .parms.Parms as Parms
import .task.Task as Task


class Do:

    @classmethod
    @dec.handle_error
    @dec.timer
    def do(cls) -> None:
        Task.do(Com.sh_kwargs(cls, Parms, sys.argv))


if __name__ == "__main__":
    Do.do()
