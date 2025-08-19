# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NVIDIA-SOFTWARE-LICENSE

# This code was automatically generated with version 13.0.0. Do not modify it directly.

from libc.stdint cimport uintptr_t
cimport cython

from cuda.bindings cimport driver, runtime, cydriver, cyruntime


cdef dict _handle_getters = None

@cython.embedsignature(True)
def get_cuda_native_handle(obj) -> int:
    """ Returns the address of the provided CUDA Python object as Python int.

    Parameters
    ----------
    obj : Any
        CUDA Python object

    Returns
    -------
    int : The object address.
    """
    global _handle_getters
    obj_type = type(obj)
    if _handle_getters is None:
        _handle_getters = dict()
        def CUcontext_getter(driver.CUcontext x): return <uintptr_t><void*><cydriver.CUcontext>(x._pvt_ptr[0])
        _handle_getters[driver.CUcontext] = CUcontext_getter
        def CUmodule_getter(driver.CUmodule x): return <uintptr_t><void*><cydriver.CUmodule>(x._pvt_ptr[0])
        _handle_getters[driver.CUmodule] = CUmodule_getter
        def CUfunction_getter(driver.CUfunction x): return <uintptr_t><void*><cydriver.CUfunction>(x._pvt_ptr[0])
        _handle_getters[driver.CUfunction] = CUfunction_getter
        def CUlibrary_getter(driver.CUlibrary x): return <uintptr_t><void*><cydriver.CUlibrary>(x._pvt_ptr[0])
        _handle_getters[driver.CUlibrary] = CUlibrary_getter
        def CUkernel_getter(driver.CUkernel x): return <uintptr_t><void*><cydriver.CUkernel>(x._pvt_ptr[0])
        _handle_getters[driver.CUkernel] = CUkernel_getter
        def CUarray_getter(driver.CUarray x): return <uintptr_t><void*><cydriver.CUarray>(x._pvt_ptr[0])
        _handle_getters[driver.CUarray] = CUarray_getter
        def CUmipmappedArray_getter(driver.CUmipmappedArray x): return <uintptr_t><void*><cydriver.CUmipmappedArray>(x._pvt_ptr[0])
        _handle_getters[driver.CUmipmappedArray] = CUmipmappedArray_getter
        def CUtexref_getter(driver.CUtexref x): return <uintptr_t><void*><cydriver.CUtexref>(x._pvt_ptr[0])
        _handle_getters[driver.CUtexref] = CUtexref_getter
        def CUsurfref_getter(driver.CUsurfref x): return <uintptr_t><void*><cydriver.CUsurfref>(x._pvt_ptr[0])
        _handle_getters[driver.CUsurfref] = CUsurfref_getter
        def CUevent_getter(driver.CUevent x): return <uintptr_t><void*><cydriver.CUevent>(x._pvt_ptr[0])
        _handle_getters[driver.CUevent] = CUevent_getter
        def CUstream_getter(driver.CUstream x): return <uintptr_t><void*><cydriver.CUstream>(x._pvt_ptr[0])
        _handle_getters[driver.CUstream] = CUstream_getter
        def CUgraphicsResource_getter(driver.CUgraphicsResource x): return <uintptr_t><void*><cydriver.CUgraphicsResource>(x._pvt_ptr[0])
        _handle_getters[driver.CUgraphicsResource] = CUgraphicsResource_getter
        def CUexternalMemory_getter(driver.CUexternalMemory x): return <uintptr_t><void*><cydriver.CUexternalMemory>(x._pvt_ptr[0])
        _handle_getters[driver.CUexternalMemory] = CUexternalMemory_getter
        def CUexternalSemaphore_getter(driver.CUexternalSemaphore x): return <uintptr_t><void*><cydriver.CUexternalSemaphore>(x._pvt_ptr[0])
        _handle_getters[driver.CUexternalSemaphore] = CUexternalSemaphore_getter
        def CUgraph_getter(driver.CUgraph x): return <uintptr_t><void*><cydriver.CUgraph>(x._pvt_ptr[0])
        _handle_getters[driver.CUgraph] = CUgraph_getter
        def CUgraphNode_getter(driver.CUgraphNode x): return <uintptr_t><void*><cydriver.CUgraphNode>(x._pvt_ptr[0])
        _handle_getters[driver.CUgraphNode] = CUgraphNode_getter
        def CUgraphExec_getter(driver.CUgraphExec x): return <uintptr_t><void*><cydriver.CUgraphExec>(x._pvt_ptr[0])
        _handle_getters[driver.CUgraphExec] = CUgraphExec_getter
        def CUmemoryPool_getter(driver.CUmemoryPool x): return <uintptr_t><void*><cydriver.CUmemoryPool>(x._pvt_ptr[0])
        _handle_getters[driver.CUmemoryPool] = CUmemoryPool_getter
        def CUuserObject_getter(driver.CUuserObject x): return <uintptr_t><void*><cydriver.CUuserObject>(x._pvt_ptr[0])
        _handle_getters[driver.CUuserObject] = CUuserObject_getter
        def CUgraphDeviceNode_getter(driver.CUgraphDeviceNode x): return <uintptr_t><void*><cydriver.CUgraphDeviceNode>(x._pvt_ptr[0])
        _handle_getters[driver.CUgraphDeviceNode] = CUgraphDeviceNode_getter
        def CUasyncCallbackHandle_getter(driver.CUasyncCallbackHandle x): return <uintptr_t><void*><cydriver.CUasyncCallbackHandle>(x._pvt_ptr[0])
        _handle_getters[driver.CUasyncCallbackHandle] = CUasyncCallbackHandle_getter
        def CUgreenCtx_getter(driver.CUgreenCtx x): return <uintptr_t><void*><cydriver.CUgreenCtx>(x._pvt_ptr[0])
        _handle_getters[driver.CUgreenCtx] = CUgreenCtx_getter
        def CUlinkState_getter(driver.CUlinkState x): return <uintptr_t><void*><cydriver.CUlinkState>(x._pvt_ptr[0])
        _handle_getters[driver.CUlinkState] = CUlinkState_getter
        def CUdevResourceDesc_getter(driver.CUdevResourceDesc x): return <uintptr_t><void*><cydriver.CUdevResourceDesc>(x._pvt_ptr[0])
        _handle_getters[driver.CUdevResourceDesc] = CUdevResourceDesc_getter
        def CUlogsCallbackHandle_getter(driver.CUlogsCallbackHandle x): return <uintptr_t><void*><cydriver.CUlogsCallbackHandle>(x._pvt_ptr[0])
        _handle_getters[driver.CUlogsCallbackHandle] = CUlogsCallbackHandle_getter
        def CUeglStreamConnection_getter(driver.CUeglStreamConnection x): return <uintptr_t><void*><cydriver.CUeglStreamConnection>(x._pvt_ptr[0])
        _handle_getters[driver.CUeglStreamConnection] = CUeglStreamConnection_getter
        def EGLImageKHR_getter(runtime.EGLImageKHR x): return <uintptr_t><void*><cyruntime.EGLImageKHR>(x._pvt_ptr[0])
        _handle_getters[runtime.EGLImageKHR] = EGLImageKHR_getter
        def EGLStreamKHR_getter(runtime.EGLStreamKHR x): return <uintptr_t><void*><cyruntime.EGLStreamKHR>(x._pvt_ptr[0])
        _handle_getters[runtime.EGLStreamKHR] = EGLStreamKHR_getter
        def EGLSyncKHR_getter(runtime.EGLSyncKHR x): return <uintptr_t><void*><cyruntime.EGLSyncKHR>(x._pvt_ptr[0])
        _handle_getters[runtime.EGLSyncKHR] = EGLSyncKHR_getter
        def cudaArray_t_getter(runtime.cudaArray_t x): return <uintptr_t><void*><cyruntime.cudaArray_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaArray_t] = cudaArray_t_getter
        def cudaArray_const_t_getter(runtime.cudaArray_const_t x): return <uintptr_t><void*><cyruntime.cudaArray_const_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaArray_const_t] = cudaArray_const_t_getter
        def cudaMipmappedArray_t_getter(runtime.cudaMipmappedArray_t x): return <uintptr_t><void*><cyruntime.cudaMipmappedArray_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaMipmappedArray_t] = cudaMipmappedArray_t_getter
        def cudaMipmappedArray_const_t_getter(runtime.cudaMipmappedArray_const_t x): return <uintptr_t><void*><cyruntime.cudaMipmappedArray_const_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaMipmappedArray_const_t] = cudaMipmappedArray_const_t_getter
        def cudaStream_t_getter(runtime.cudaStream_t x): return <uintptr_t><void*><cyruntime.cudaStream_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaStream_t] = cudaStream_t_getter
        def cudaEvent_t_getter(runtime.cudaEvent_t x): return <uintptr_t><void*><cyruntime.cudaEvent_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaEvent_t] = cudaEvent_t_getter
        def cudaGraphicsResource_t_getter(runtime.cudaGraphicsResource_t x): return <uintptr_t><void*><cyruntime.cudaGraphicsResource_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaGraphicsResource_t] = cudaGraphicsResource_t_getter
        def cudaExternalMemory_t_getter(runtime.cudaExternalMemory_t x): return <uintptr_t><void*><cyruntime.cudaExternalMemory_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaExternalMemory_t] = cudaExternalMemory_t_getter
        def cudaExternalSemaphore_t_getter(runtime.cudaExternalSemaphore_t x): return <uintptr_t><void*><cyruntime.cudaExternalSemaphore_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaExternalSemaphore_t] = cudaExternalSemaphore_t_getter
        def cudaGraph_t_getter(runtime.cudaGraph_t x): return <uintptr_t><void*><cyruntime.cudaGraph_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaGraph_t] = cudaGraph_t_getter
        def cudaGraphNode_t_getter(runtime.cudaGraphNode_t x): return <uintptr_t><void*><cyruntime.cudaGraphNode_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaGraphNode_t] = cudaGraphNode_t_getter
        def cudaUserObject_t_getter(runtime.cudaUserObject_t x): return <uintptr_t><void*><cyruntime.cudaUserObject_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaUserObject_t] = cudaUserObject_t_getter
        def cudaFunction_t_getter(runtime.cudaFunction_t x): return <uintptr_t><void*><cyruntime.cudaFunction_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaFunction_t] = cudaFunction_t_getter
        def cudaKernel_t_getter(runtime.cudaKernel_t x): return <uintptr_t><void*><cyruntime.cudaKernel_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaKernel_t] = cudaKernel_t_getter
        def cudaLibrary_t_getter(runtime.cudaLibrary_t x): return <uintptr_t><void*><cyruntime.cudaLibrary_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaLibrary_t] = cudaLibrary_t_getter
        def cudaMemPool_t_getter(runtime.cudaMemPool_t x): return <uintptr_t><void*><cyruntime.cudaMemPool_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaMemPool_t] = cudaMemPool_t_getter
        def cudaGraphExec_t_getter(runtime.cudaGraphExec_t x): return <uintptr_t><void*><cyruntime.cudaGraphExec_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaGraphExec_t] = cudaGraphExec_t_getter
        def cudaGraphDeviceNode_t_getter(runtime.cudaGraphDeviceNode_t x): return <uintptr_t><void*><cyruntime.cudaGraphDeviceNode_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaGraphDeviceNode_t] = cudaGraphDeviceNode_t_getter
        def cudaAsyncCallbackHandle_t_getter(runtime.cudaAsyncCallbackHandle_t x): return <uintptr_t><void*><cyruntime.cudaAsyncCallbackHandle_t>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaAsyncCallbackHandle_t] = cudaAsyncCallbackHandle_t_getter
        def cudaLogsCallbackHandle_getter(runtime.cudaLogsCallbackHandle x): return <uintptr_t><void*><cyruntime.cudaLogsCallbackHandle>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaLogsCallbackHandle] = cudaLogsCallbackHandle_getter
        def cudaEglStreamConnection_getter(runtime.cudaEglStreamConnection x): return <uintptr_t><void*><cyruntime.cudaEglStreamConnection>(x._pvt_ptr[0])
        _handle_getters[runtime.cudaEglStreamConnection] = cudaEglStreamConnection_getter
    try:
        return _handle_getters[obj_type](obj)
    except KeyError:
        raise TypeError("Unknown type: " + str(obj_type)) from None