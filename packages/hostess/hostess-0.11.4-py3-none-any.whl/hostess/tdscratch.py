import gc
import inspect
import sys
import time

import numpy as np
from rich import inspect as ri

from hostess.disintegration import disintegrate
from hostess.monitors import memory, mb
from hostess.profilers import yclept, namespace_ids, describe_frame_contents, \
    scopedict_ids, analyze_references

#
# def stepback():
#     def inner():
#         f = inspect.currentframe().f_back.f_back
#         # sf = (str(f),)
#         # del f
#         return {2}
#         # return {
#         #     k: id(v)
#         #     for k, v in inspect.currentframe().f_back.f_back.f_locals.items()
#         # }
#     # def localsmash(ldict):
#     #     for k in tuple(ldict.keys()):
#     #         ldict.pop(k)
#     try:
#         # locids = inner()
#         # return set(locids)
#         f = inspect.currentframe().f_back.f_locals
#         print(id(f))
#         # f.clear()
#         for k in tuple(f.keys()):
#             f.pop(k)
#         # print(ri(f))
#         # f = 1
#         return {1}
#         # return {str(f)}
#         # h = f.f_locals
#         # ids = {id(h), id(f)}
#         # print(gc.is_tracked(h))
#         # print(gc.is_tracked(f))
#         # print(id(f))
#         # return ids
#     finally:
#         pass
#         # del f
#         # del h, f
#         # print(gc.is_tracked(h))
#         # print(gc.is_tracked(f))
#         # locals().pop('f')
#         # locals().pop('h')
#
#
# def test_disintegrate_2():
#     # def wrapped_func():
#     initial_usage = mb(memory(), 1)
#     array = np.random.poisson(2, (4000, 4000))
#     mem_after_array_init = mb(memory(), 1)
#     print('ref before call', sys.getrefcount(array))
#     # print(id(locals()))
#     # yclept(array)
#     rn = analyze_references(
#         array, gc.get_referrers, filter_scopedict=True
#     )
#     print('ref on analysis return', sys.getrefcount(array))
#     # ids = scopedict_ids(scopenames=('locals',))
#     _arraylist = [array]
#     _arraydict = {'a': (array, (array, array))}
#     print(id(_arraylist), id(_arraydict['a']))
#     print(gc.is_tracked(_arraylist))
#     res = disintegrate(array, _debug=True, return_permit_ids=True)
#     # assert id(_arraylist) in res['permit_ids']
#     for s in res['success']:
#         print(s)
#     print(len(_arraylist))
#     print(len(_arraydict['a']))
#     # ids = stepback()
#     # print('caller frame id', id(inspect.currentframe()))
#     # print('local id intersection', ids.intersection(set(map(id, locals().values()))))
#
#     print('ref after call', sys.getrefcount(array))
#     gc.collect()
#     print('ref after collection', sys.getrefcount(array))
#     # a = str(locals())
#     del array
#     # time.sleep(0.1)
#     print('initial mem', initial_usage)
#     print('mem after pois', mem_after_array_init)
#     print('mem after delete', mb(memory(), 1))
#     gc.collect()
#     print('mem after second collect', mb(memory(), 1))
#     # time.sleep(0.1)
#
#
#
#     # wrapped_func()
#     # gc.collect()
#
#
#
# # test_disintegrate_2()
# # print('mem after exec complete', mb(memory(), 1))

def f3(x, z):
    xidnytta, yidnytta = map(yclept, (x, z))
    print('x id')
    print(xidnytta[0])
    print('\ny id')
    print(yidnytta[0])
    print('\nxnames')
    for r in xidnytta[1]:
        print(r)
    print('\nynames')
    for r in yidnytta[1]:
        print(r)
def f2(x):
    b = [2]
    return f3(x, b)

def f1():
    a = [1]
    return f2(a)
f1()
