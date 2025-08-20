from collections.abc import Callable, Iterator
from typing import Any

# import pathos.multiprocessing as mp

import ut_com.dec as dec
import ut_com.com.Com as Com
import ut_log.log.LogEq as LogEq
import ut_dic.doc.DoC as DoC

TyArr = list[Any]
TyCallable = Callable[..., Any]
TyMsg = str
TyRun = dict[str, str | int]
TyTup = tuple[Any, ...]
TyDic = dict[Any, Any]
TyDoC = dict[str, TyCallable]

TyTask = Any
TyIterTup = Iterator[TyTup]
TnCallable = None | TyCallable


class CoFu:
    '''
    Concurrent Futures
    '''
    @staticmethod
    def process(task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Concurrent Futures process pool
        '''
        from concurrent.futures import ProcessPoolExecutor
        _run_cpus: int = d_run.get('cpus', 4)
        with ProcessPoolExecutor(max_workers=_run_cpus) as executor:
            executor.map(task_, yield_dl_tpl)

    @staticmethod
    def thread(task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Concurrent Futures thread pool
        '''
        from concurrent.futures import ThreadPoolExecutor
        _run_cpus: int = d_run.get('cpus', 4)
        with ThreadPoolExecutor(max_workers=_run_cpus) as executor:
            executor.map(task_, yield_dl_tpl)


class MuPr:
    '''
    Multiprocessing
    '''
    @staticmethod
    def process(task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Multiprocessing process pool
        '''
        import multiprocessing
        import multiprocessing.pool
        _run_cpus: int = d_run.get('cpus', 4)
        _run_ctx = d_run.get('ctx', "spawn")
        _run_exe = d_run.get('exe', "sync")

        # create a process context
        _ctx = multiprocessing.get_context(_run_ctx)
        # create a process pool with a given context
        with multiprocessing.pool.Pool(processes=_run_cpus, context=_ctx) as pool:
            if _run_exe == "sync":
                pool.map(task_, yield_dl_tpl)
                pool.close()
            else:
                pool.map_async(task_, yield_dl_tpl)
                pool.close()
                pool.join()

    @staticmethod
    def thread(task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Multiprocessing thread pool
        '''
        import multiprocessing
        import multiprocessing.pool
        _run_cpus: int = d_run.get('cpus', 4)
        _run_ctx = d_run.get('ctx', "fork")
        _run_exe = d_run.get('exe', "sync")

        _ctx = multiprocessing.get_context(_run_ctx)
        with multiprocessing.pool.Pool(processes=_run_cpus, context=_ctx) as pool:
            if _run_exe == "sync":
                pool.map(task_, yield_dl_tpl)
                pool.close()
            else:
                pool.map_async(task_, yield_dl_tpl)
                pool.close()
                pool.join()


class JoLi:
    '''
    Joblib run tasks in parallel
    '''
    @staticmethod
    def task(task_: TyCallable, args: TyTup):
        _kwargs = args[1]
        Com.init(_kwargs)
        task_(args)

    @classmethod
    def run(cls, task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Joblib run tasks in parallel using processes
        '''
        from joblib import Parallel, delayed
        _run_cpus: int = d_run.get('cpus', 4)
        results = Parallel(n_jobs=_run_cpus, prefer="threads")(
                delayed(cls.task)(task_, item) for item in yield_dl_tpl)
        LogEq.debug("results", results)

    @classmethod
    def thread(cls, task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        '''
        Joblib run tasks in parallel using threads
        '''
        from joblib import parallel_config, Parallel, delayed
        _run_cpus: int = d_run.get('cpus', 4)
        with parallel_config(backend='threading', n_jobs=_run_cpus):
            results = Parallel()(
                    delayed(cls.task)(task_, item) for item in yield_dl_tpl)
            LogEq.debug("results", results)


class SiPr:
    '''
    Single processing
    '''
    @staticmethod
    def run(task_: TyCallable, yield_dl_tpl: TyIterTup, d_run: TyDic) -> None:
        for _item in yield_dl_tpl:
            task_(_item)


class Ptc:
    '''
    Process Controller
    '''
    '''
    Dictionary to translate run method name into run method
    '''
    d_run_method_2_fnc: TyDoC = {
            'mp_process': MuPr.process,
            'mp_thread': MuPr.thread,
            'co_process': CoFu.process,
            'co_thread': CoFu.thread,
            'jl_run': JoLi.run,
            'jl_thread': JoLi.thread,
            'sp': SiPr.run
    }

    @classmethod
    @dec.timer_ptc
    def do(cls, **kwargs) -> None:
        _d_run = kwargs.get("d_run", {})
        _run_method: str = _d_run.get("method", "sp")
        _Task = kwargs.get('task')
        if _Task is None:
            return
        _yield_dl_tpl: TyIterTup = _Task.yield_dl_tpl(kwargs)
        _executor: TyCallable = DoC.sh(cls.d_run_method_2_fnc, _run_method)
        _executor(_Task.task, _yield_dl_tpl, _d_run)
