/*
 * Copyright (c) 2019-25, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 */


/**
 * @file
 * @brief This file contains all public function declarations of the cuTENSOR
 * library.
 */
#pragma once

#define CUTENSOR_MAJOR 2 //!< cuTensor major version.
#define CUTENSOR_MINOR 3 //!< cuTensor minor version.
#define CUTENSOR_PATCH 0 //!< cuTensor patch version.
#define CUTENSOR_VERSION (CUTENSOR_MAJOR * 10000 + CUTENSOR_MINOR * 100 + CUTENSOR_PATCH)

#include <stdint.h>
#include <stdio.h>
#include <cuda_runtime.h>

#include <cutensor/types.h>

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

/**
 * \mainpage cuTENSOR: A High-Performance CUDA Library for Tensor Primitives
 *
 * \section intro Introduction
 *
 * \subsection nomen Nomenclature
 *
 * The term tensor refers to an \b order-n (a.k.a.,
 * n-dimensional) array. One can think of tensors as a generalization of
 * matrices to higher \b orders.

 * For example, scalars, vectors, and matrices are
 * order-0, order-1, and order-2 tensors, respectively.
 *
 * An order-n tensor has n \b modes. Each mode has an \b extent (a.k.a. size).
 * Each mode you can specify a \b stride s > 0. This \b stride
 * describes offset of two logically consecutive elements in physical (i.e., linearized) memory.
 * This is similar to the leading-dimension in BLAS.

 * cuTENSOR, by default, adheres to a generalized \b column-major data layout.
 * For example: \f$A_{a,b,c} \in {R}^{4\times 8 \times 12}\f$
 * is an order-3 tensor with the extent of the a-mode, b-mode, and c-mode
 * respectively being 4, 8, and 12. If not explicitly specified, the strides are
 * assumed to be: stride(a) = 1, stride(b) = extent(a), stride(c) = extent(a) *
 * extent(b).

 * For a general order-n tensor \f$A_{i_1,i_2,...,i_n}\f$ we require that the strides do
 * not lead to overlapping memory accesses; for instance, \f$stride(i_1) \geq 1\f$, and
 * \f$stride(i_l) \geq stride(i_{l-1}) * extent(i_{l-1})\f$.

 * We say that a tensor is \b packed if it is contiguously stored in memory along all
 * modes. That is, \f$ stride(i_1) = 1\f$ and \f$stride(i_l) =stride(i_{l-1}) *
 * extent(i_{l-1})\f$).
 *
 * \subsection einsum Einstein Notation
 * We adhere to the "Einstein notation": Modes that appear in the input
 * tensors, and that do not appear in the output tensor, are implicitly
 * contracted.
 *
 * \section api API Reference
 * For details on the API please refer to \ref cutensor.h and \ref types.h.
 *
 */

/**
 * \brief Initializes the cuTENSOR library and allocates the memory for the library context.
 *
 * \details The device associated with a particular cuTENSOR handle is assumed to remain
 * unchanged after the \ref cutensorCreate call. In order for the cuTENSOR library to
 * use a different device, the application must set the new device to be used by
 * calling cudaSetDevice and then create another cuTENSOR handle, which will
 * be associated with the new device, by calling \ref cutensorCreate. 
 *
 * Moreover, each handle by default has a plan cache that can store the least recently
 * used \ref cutensorPlan_t; its default capacity is 64, but it can be changed via \ref
 * cutensorHandleResizePlanCache if this is too little storage space.
 * See the <a href="../plan_cache.html">Plan Cache Guide</a> for more information.
 *
 * The user is responsible for calling  \ref cutensorDestroy to free the resources associated
 * with the handle.
 *
 * \param[out] handle Pointer to cutensorHandle_t
 *
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreate(cutensorHandle_t* handle);

/**
 * \brief Frees all resources related to the provided library handle.
 *
 * \param[in,out] handle Pointer to cutensorHandle_t
 *
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorDestroy(cutensorHandle_t handle);

/**
 * \brief Resizes the plan cache.
 *
 * This function changes the number of plans that can be stored in the plan cache 
 * of the handle.
 *
 * Resizing invalidates the cache.
 *
 * While this function is not thread-safe, the resulting cache can be shared across
 * different threads in a thread-safe manner.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context. The cache will be attached to the handle
 * \param[in] numEntries Number of entries the cache will support.
 *
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \remarks non-blocking, no reentrant, and not thread-safe
 */
cutensorStatus_t cutensorHandleResizePlanCache(cutensorHandle_t handle,
                                               const uint32_t numEntries);

/**
 * \brief Writes the Plan-Cache (that belongs to the provided handle) to file.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] filename Specifies the filename (including the absolute path) to the file
 * that should hold all the cache information. Warning: an existing file will be
 * overwritten.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if the no cache has been attached
 * \retval CUTENSOR_STATUS_IO_ERROR if the file cannot be written to
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorHandleWritePlanCacheToFile(const cutensorHandle_t handle,
                                                    const char filename[]);

/**
 * \brief Reads a Plan-Cache from file and overwrites the cachelines of the provided handle.
 *
 * A cache is only valid for the same cuTENSOR version and CUDA version; moreover, the
 * GPU architecture (incl. multiprocessor count) must match, otherwise
 * CUTENSOR_STATUS_INVALID_VALUE will be returned.
 *
 * \param[in,out] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] filename Specifies the filename (including the absolute path) to the file
 * that holds all the cache information that have previously been written by \ref cutensorHandleWritePlanCacheToFile.
 * \param[out] numCachelinesRead On exit, this variable will hold the number of
 * successfully-read cachelines, if CUTENSOR_STATUS_SUCCESS is returned. Otherwise, this
 * variable will hold the number of cachelines that are required to read all
 * cachelines associated to the cache pointed to by `filename`; in that case
 * CUTENSOR_STATUS_INSUFFICIENT_WORKSPACE is returned.
 *
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if the stored cache was created by a different
 * cuTENSOR- or CUDA-version or if the GPU architecture (incl. multiprocessor count) doesn't match
 * \retval CUTENSOR_STATUS_INSUFFICIENT_WORKSPACE if the stored cache requires more
 * cachelines than those that are currently attached to the handle
 * \retval CUTENSOR_STATUS_IO_ERROR if the file cannot be read
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorHandleReadPlanCacheFromFile(cutensorHandle_t handle,
                                                 const char filename[],
                                                 uint32_t* numCachelinesRead);

/**
 * \brief Writes the --per library-- kernel cache to file.
 *
 * Writes the just-in-time compiled kernels to the provided file (those kernels belong to
 * the library--not to the handle).
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] filename Specifies the filename (including the absolute path) to the file
 * that should hold all the cache information. Warning: an existing file will be
 * overwritten.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully or there were no kernels in the cache.
 * \retval CUTENSOR_STATUS_IO_ERROR if the file cannot be written to.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the function is not available for the operating system, CUDA Toolkit,
 * or compute capability of the device.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorWriteKernelCacheToFile(const cutensorHandle_t handle,
                                                const char filename[]);

/**
 * \brief Reads a kernel cache from file and adds all non-existing JIT compiled kernels to the kernel cache.
 *
 * A cache is only valid for the same cuTENSOR version and CUDA version; moreover, the
 * GPU architecture (incl. multiprocessor count) must match, otherwise CUTENSOR_STATUS_INVALID_VALUE will be returned.
 *
 * \param[in,out] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] filename Specifies the filename (including the absolute path) to the file
 * that holds all the cache information that have previously been written by cutensorWriteKernelCacheToFile.
 *
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully, or the file pointed to by filename was empty.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if the stored cache was created by a different
 * cuTENSOR- or CUDA-version or if the GPU architecture (incl. multiprocessor count) doesn't match.
 * \retval CUTENSOR_STATUS_IO_ERROR if the file cannot be read.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the function is not available for the operating system, CUDA Toolkit,
 * or compute capability of the device.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorReadKernelCacheFromFile(cutensorHandle_t handle,
                                                 const char filename[]);
/**
 * \brief Creates a tensor descriptor.
 *
 * \details This allocates a small amount of host-memory.
 *
 * The user is responsible for calling cutensorDestroyTensorDescriptor() to free the associated resources once the tensor descriptor is no longer used.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc Pointer to the address where the allocated tensor descriptor object will be stored.
 * \param[in] numModes Number of modes.
 * \param[in] extent Extent of each mode (must be larger than zero).
 * \param[in] stride stride[i] denotes the displacement (a.k.a. stride)--in elements of the base type--between two consecutive elements in the ith-mode.
 *            If stride is NULL, a packed generalized column-major memory
 *            layout is assumed (i.e., the strides increase monotonically from left to
 *            right). Each stride must be larger than zero; to be precise, a stride of zero can be
 *            achieved by omitting this mode entirely; for instance instead of writing
 *            C[a,b] = A[b,a] with strideA(a) = 0, you can write C[a,b] = A[b] directly;
 *            cuTENSOR will then automatically infer that the a-mode in A should be broadcasted.
 * \param[in] dataType Data type of the stored entries.
 * \param[in] alignmentRequirement Alignment (in bytes) to the base pointer that will be used in conjunction with this tensor descriptor (e.g., `cudaMalloc` has a default alignment of 256 bytes).
 *
 * \pre extent and stride arrays must each contain at least sizeof(int64_t) * numModes bytes
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the requested descriptor is not supported (e.g., due to non-supported data type).
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreateTensorDescriptor(const cutensorHandle_t handle,
                                              cutensorTensorDescriptor_t* desc,
                                              const uint32_t numModes,
                                              const int64_t extent[],
                                              const int64_t stride[],
                                              cudaDataType_t dataType,
                                              uint32_t alignmentRequirement);

/**
 * \brief Frees all resources related to the provided tensor descriptor.
 *
 * \param[in,out] desc The cutensorTensorDescriptor_t object that will be deallocated.
 *
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorDestroyTensorDescriptor(cutensorTensorDescriptor_t desc);

/**
 * \brief This function creates an operation descriptor that encodes an elementwise trinary operation.
 *
 * \details Said trinary operation has the following general form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{ABC}(\Phi_{AB}(\alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \beta op_B(B_{\Pi^B(i_0,i_1,...,i_n)})), \gamma op_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * Where
 *    - A,B,C,D are multi-mode tensors (of arbitrary data types).
 *    - \f$\Pi^A, \Pi^B, \Pi^C \f$ are permutation operators that permute the modes of A, B, and C respectively.
 *    - \f$op_{A},op_{B},op_{C}\f$ are unary element-wise operators (e.g., IDENTITY, CONJUGATE).
 *    - \f$\Phi_{ABC}, \Phi_{AB}\f$ are binary element-wise operators (e.g., ADD, MUL, MAX, MIN).
 *
 * Notice that the broadcasting (of a mode) can be achieved by simply omitting that mode from the respective tensor.
 *
 * Moreover, modes may appear in any order, giving users a greater flexibility. The only <b>restrictions</b> are:
 *    - modes that appear in A or B _must_ also appear in the output tensor; a mode that only appears in the input would be contracted and such an operation would be covered by either \ref cutensorContract or \ref cutensorReduce.
 *    - each mode may appear in each tensor at most once.
 *
 * Input tensors may be read even if the value
 * of the corresponding scalar is zero.
 *
 * Examples:
 *    - \f$ D_{a,b,c,d} = A_{b,d,a,c}\f$
 *    - \f$ D_{a,b,c,d} = 2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a}\f$
 *    - \f$ D_{a,b,c,d} = 2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a} + C_{a,b,c,d}\f$
 *    - \f$ D_{a,b,c,d} = min((2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a}), C_{a,b,c,d})\f$
 *
 * Call \ref cutensorElementwiseTrinaryExecute to perform the actual operation.
 *
 * Please use \ref cutensorDestroyOperationDescriptor to deallocated the descriptor once it is no longer used.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+---------------+----------------------------+
 * |     typeA     |     typeB     |     typeC     |  descCompute               |
 * +===============+===============+===============+============================+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_16F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_16BF|
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_32F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_64F |
 * +---------------+---------------+---------------+----------------------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_64F |
 * +---------------+---------------+---------------+----------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested elementwise operation.
 * \param[in] descA A descriptor that holds the information about the data type, modes, and strides of A.
 * \param[in] modeA Array (in host memory) of size descA->numModes that holds the names of the modes of A (e.g., if \f$A_{a,b,c}\f$ then modeA = {'a','b','c'}). The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref cutensorCreateTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB A descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array (in host memory) of size descB->numModes that holds the names of the modes of B. modeB[i] corresponds to extent[i] and stride[i] of the \ref cutensorCreateTensorDescriptor
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC A descriptor that holds information about the data type, modes, and strides of C.
 * \param[in] modeC Array (in host memory) of size descC->numModes that holds the names of the modes of C. The modeC[i] corresponds to extent[i] and stride[i] of the \ref cutensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD A descriptor that holds information about the data type, modes, and strides of D. Notice that we currently request descD and descC to be identical.
 * \param[in] modeD Array (in host memory) of size descD->numModes that holds the names of the modes of D. The modeD[i] corresponds to extent[i] and stride[i] of the \ref cutensorCreateTensorDescriptor.
 * \param[in] opAB Element-wise binary operator (see \f$\Phi_{AB}\f$ above).
 * \param[in] opABC Element-wise binary operator (see \f$\Phi_{ABC}\f$ above).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval CUTENSOR_STATUS_ARCH_MISMATCH if the device is either not ready, or the target architecture is not supported.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreateElementwiseTrinary(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descB, const int32_t modeB[], cutensorOperator_t opB,
                 const cutensorTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
                 const cutensorTensorDescriptor_t descD, const int32_t modeD[],
                 cutensorOperator_t opAB, cutensorOperator_t opABC,
                 const cutensorComputeDescriptor_t descCompute);

/**
 * \brief Performs an element-wise tensor operation for three input tensors (see \ref cutensorCreateElementwiseTrinary)
 *
 * \details This function performs a element-wise tensor operation of the form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{ABC}(\Phi_{AB}(\alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \beta op_B(B_{\Pi^B(i_0,i_1,...,i_n)})), \gamma op_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * See \ref cutensorCreateElementwiseTrinary() for details.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired elementwise operation (created by \ref cutensorCreateElementwiseTrinary followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling factor for A (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). Pointer to the host memory. If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Multi-mode tensor (described by `descA` as part of \ref cutensorCreateElementwiseTrinary). Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] beta Scaling factor for B (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). Pointer to the host memory. If beta is zero, B is not read and the corresponding unary operator is not applied.
 * \param[in] B Multi-mode tensor (described by `descB` as part of \ref cutensorCreateElementwiseTrinary). Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] gamma Scaling factor for C (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). Pointer to the host memory. If gamma is zero, C is not read and the corresponding unary operator is not applied.
 * \param[in] C Multi-mode tensor (described by `descC` as part of \ref cutensorCreateElementwiseTrinary). Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[out] D Multi-mode tensor (described by `descD` as part of \ref cutensorCreateElementwiseTrinary). Pointer to the GPU-accessible memory (`C` and `D` may be identical, if and only if `descC == descD`).
 * \param[in] stream The CUDA stream used to perform the operation.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorElementwiseTrinaryExecute(
                 const cutensorHandle_t handle, const cutensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* beta,  const void* B,
                 const void* gamma, const void* C,
                                          void* D, cudaStream_t stream);

/**
 * \brief This function creates an operation descriptor for an elementwise binary operation.
 *
 * \details The binary operation has the following general form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{AC}(\alpha \Psi_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \gamma \Psi_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * Call \ref cutensorElementwiseBinaryExecute to perform the actual operation.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+------------------------------+
 * |     typeA     |     typeC     |  descCompute                 |
 * +===============+===============+==============================+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_16F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_16BF  |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_32F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_64F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_64F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested elementwise operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes, and strides of A.
 * \param[in] modeA Array (in host memory) of size descA->numModes that holds the names of the modes of A (e.g., if A_{a,b,c} => modeA = {'a','b','c'}). The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref cutensorCreateTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC The descriptor that holds information about the data type, modes, and strides of C.
 * \param[in] modeC Array (in host memory) of size descC->numModes that holds the names of the modes of C. The modeC[i] corresponds to extent[i] and stride[i] of the \ref cutensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD The descriptor that holds information about the data type, modes, and strides of D. Notice that we currently request descD and descC to be identical.
 * \param[in] modeD Array (in host memory) of size descD->numModes that holds the names of the modes of D. The modeD[i] corresponds to extent[i] and stride[i] of the \ref cutensorCreateTensorDescriptor.
 * \param[in] opAC Element-wise binary operator (see \f$\Phi_{AC}\f$ above).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreateElementwiseBinary(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
                 const cutensorTensorDescriptor_t descD, const int32_t modeD[],
                 cutensorOperator_t opAC,
                 const cutensorComputeDescriptor_t descCompute);

/**
 * \brief Performs an element-wise tensor operation for two input tensors (see \ref cutensorCreateElementwiseBinary)
 *
 * \details This function performs a element-wise tensor operation of the form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{AC}(\alpha \Psi_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \gamma \Psi_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * See \ref cutensorCreateElementwiseBinary() for details.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired elementwise operation (created by \ref cutensorCreateElementwiseBinary followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling factor for A (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). Pointer to the host memory. If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Multi-mode tensor (described by `descA` as part of \ref cutensorCreateElementwiseBinary). Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] gamma Scaling factor for C (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). Pointer to the host memory. If gamma is zero, C is not read and the corresponding unary operator is not applied.
 * \param[in] C Multi-mode tensor (described by `descC` as part of \ref cutensorCreateElementwiseBinary). Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[out] D Multi-mode tensor (described by `descD` as part of \ref cutensorCreateElementwiseBinary). Pointer to the GPU-accessible memory (`C` and `D` may be identical, if and only if `descC == descD`).
 * \param[in] stream The CUDA stream used to perform the operation.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorElementwiseBinaryExecute(
                 const cutensorHandle_t handle, const cutensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* gamma, const void* C,
                                          void* D, cudaStream_t stream);

/**
 * \brief This function creates an operation descriptor for a tensor permutation.
 *
 * \details The tensor permutation has the following general form:
 * \f[ B_{\Pi^B(i_0,i_1,...,i_n)} = \alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}) \f]
 *
 * Consequently, this function performs an out-of-place tensor permutation and is a specialization of \ref cutensorCreateElementwiseBinary.
 *
 * Where
 *    - A and B are multi-mode tensors (of arbitrary data types),
 *    - \f$\Pi^A, \Pi^B\f$ are permutation operators that permute the modes of A, B respectively,
 *    - \f$op_A\f$ is an unary element-wise operators (e.g., IDENTITY, SQR, CONJUGATE), and
 *    - \f$\Psi\f$ is specified in the tensor descriptor descA.
 *
 * Broadcasting (of a mode) can be achieved by simply omitting that mode from the respective tensor.
 *
 * Modes may appear in any order. The only <b>restrictions</b> are:
 *    - modes that appear in A _must_ also appear in the output tensor.
 *    - each mode may appear in each tensor at most once.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+------------------------------+
 * |     typeA     |     typeB     |  descCompute                 |
 * +===============+===============+==============================+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_16F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_32F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_16BF  |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_32F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_R_64F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_32F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * |  CUDA_C_64F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_64F   |
 * +---------------+---------------+------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested permutation.
 * \param[in] descA The descriptor that holds information about the data type, modes, and strides of A.
 * \param[in] modeA Array of size descA->numModes that holds the names of the modes of A (e.g., if A_{a,b,c} => modeA = {'a','b','c'})
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB The descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array of size descB->numModes that holds the names of the modes of B
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreatePermutation(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descB, const int32_t modeB[],
                 const cutensorComputeDescriptor_t descCompute);

/**
 * \brief Performs the tensor permutation that is encoded by `plan` (see \ref cutensorCreatePermutation).
 *
 * \details This function performs an elementwise tensor operation of the form:
 * \f[ B_{\Pi^B(i_0,i_1,...,i_n)} = \alpha \Psi(A_{\Pi^A(i_0,i_1,...,i_n)}) \f]
 *
 * Consequently, this function performs an out-of-place tensor permutation.
 *
 * Where
 *    - A and B are multi-mode tensors (of arbitrary data types),
 *    - \f$\Pi^A, \Pi^B\f$ are permutation operators that permute the modes of A, B respectively,
 *    - \f$\Psi\f$ is an unary element-wise operators (e.g., IDENTITY, SQR, CONJUGATE), and
 *    - \f$\Psi\f$ is specified in the tensor descriptor descA.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired tensor reduction (created by \ref cutensorCreatePermutation followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling factor for A (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory. If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Multi-mode tensor of type typeA with nmodeA modes. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in,out] B Multi-mode tensor of type typeB with nmodeB modes. Pointer to the GPU-accessible memory.
 * \param[in] stream The CUDA stream.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorPermute(
                 const cutensorHandle_t handle, const cutensorPlan_t plan,
                 const void* alpha, const void* A,
                                          void* B, const cudaStream_t stream);



/**
 * \brief This function allocates a cutensorOperationDescriptor_t object that encodes a tensor contraction of the form \f$ D = \alpha \mathcal{A}  \mathcal{B} + \beta \mathcal{C} \f$.
 *
 * \details Allocates data for `desc` to be used to perform a tensor contraction of the form \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets \alpha op_\mathcal{A}(\mathcal{A}_{{modes}_\mathcal{A}}) op_\mathcal{B}(B_{{modes}_\mathcal{B}}) + \beta op_\mathcal{C}(\mathcal{C}_{{modes}_\mathcal{C}}). \f]
 *
 * See \ref cutensorCreatePlan (or \ref cutensorCreatePlanAutotuned) to create the plan
 * (i.e., to select the kernel) followed by a call to \ref cutensorContract to perform the
 * actual contraction.
 *
 * The user is responsible for calling \ref cutensorDestroyOperationDescriptor to free the resources associated
 * with the descriptor.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |     typeA     |     typeB     |     typeC     |        descCompute           |  typeScalar   | Tensor Core |
 * +===============+===============+===============+==============================+===============+=============+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | Volta+      |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_TF32  |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_3XTF32|  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_16BF  |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_16F   |  CUDA_R_32F   | Volta+      |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_R_64F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_64F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_C_32F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_TF32  |  CUDA_C_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_3XTF32|  CUDA_C_32F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_C_64F   | Ampere+     |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_C_64F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_C_64F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_64F   |  CUDA_R_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_C_64F   | No          |
 * +---------------+---------------+---------------+------------------------------+---------------+-------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 * the tensor contraction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes and strides of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB The descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array with 'nmodeB' entries that represent the modes of B. The modeB[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. The modeC[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] descC The escriptor that holds information about the data type, modes, and strides of C.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] modeD Array with 'nmodeD' entries that represent the modes of D (must be identical to modeC for now). The modeD[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] descD The descriptor that holds information about the data type, modes, and strides of D (must be identical to `descC` for now).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
cutensorStatus_t cutensorCreateContraction(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descB, const int32_t modeB[], cutensorOperator_t opB,
                 const cutensorTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
                 const cutensorTensorDescriptor_t descD, const int32_t modeD[],
                 const cutensorComputeDescriptor_t descCompute);

/**
 * \brief Frees all resources related to the provided descriptor.
 *
 * \param[in,out] desc The cutensorOperationDescriptor_t object that will be deallocated.
 *
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorDestroyOperationDescriptor(cutensorOperationDescriptor_t desc);

/**
 * \brief Set attribute of a cutensorOperationDescriptor_t object.
 *
 * Currently not supported for blocksparse contraction descriptors.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in,out] desc Operation descriptor that will be modified.
 * \param[in] attr Specifies the attribute that will be set.
 * \param[in] buf This buffer (of size `sizeInBytes`) determines the value to which `attr` will be set.
 * \param[in] sizeInBytes Size of buf (in bytes).
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorOperationDescriptorSetAttribute(
        const cutensorHandle_t handle,
        cutensorOperationDescriptor_t desc,
        cutensorOperationDescriptorAttribute_t attr,
        const void *buf,
        size_t sizeInBytes);

/**
 * \brief This function retrieves an attribute of the provided cutensorOperationDescriptor_t object (see \ref cutensorOperationDescriptorAttribute_t).
 *
 * Block-sparse contraction descriptors only support the attributes
 *  CUTENSOR_OPERATION_DESCRIPTOR_SCALAR_TYPE and CUTENSOR_OPERATION_DESCRIPTOR_MOVED_BYTES.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] desc The cutensorOperationDescriptor_t object whos attribute is queried.
 * \param[in] attr Specifies the attribute that will be retrieved.
 * \param[out] buf This buffer (of size sizeInBytes) will hold the requested attribute of the provided cutensorOperationDescriptor_t object.
 * \param[in] sizeInBytes Size of buf (in bytes); see \ref cutensorOperationDescriptorAttribute_t for the exact size.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorOperationDescriptorGetAttribute(
        const cutensorHandle_t handle,
        cutensorOperationDescriptor_t desc,
        cutensorOperationDescriptorAttribute_t attr,
        void *buf,
        size_t sizeInBytes);

/**
  * \brief Allocates the cutensorPlanPreference_t, enabling users to limit the applicable kernels for a given plan/operation.
  *
  * \param[in] handle Opaque handle holding cuTENSOR's library context.
  * \param[out] pref Pointer to the structure holding the \ref cutensorPlanPreference_t allocated
  * by this function. See \ref cutensorPlanPreference_t.
  * \param[in] algo Allows users to select a specific algorithm. CUTENSOR_ALGO_DEFAULT lets the heuristic choose the algorithm. Any value >= 0 selects a specific GEMM-like algorithm
  *                 and deactivates the heuristic. If a specified algorithm is not supported CUTENSOR_STATUS_NOT_SUPPORTED is returned. See \ref cutensorAlgo_t for additional choices.
  * \param[in] jitMode Determines if cuTENSOR is allowed to use JIT-compiled kernels (leading to a longer plan-creation phase); see \ref cutensorJitMode_t.
  */
cutensorStatus_t cutensorCreatePlanPreference(
                               const cutensorHandle_t handle,
                               cutensorPlanPreference_t* pref,
                               cutensorAlgo_t algo,
                               cutensorJitMode_t jitMode);

/**
 * \brief Frees all resources related to the provided preference.
 *
 * \param[in,out] pref The cutensorPlanPreference_t object that will be deallocated.
 *
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorDestroyPlanPreference(cutensorPlanPreference_t pref);

/**
 * \brief Set attribute of a cutensorPlanPreference_t object.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in,out] pref This opaque struct restricts the search space of viable candidates.
 * \param[in] attr Specifies the attribute that will be set.
 * \param[in] buf This buffer (of size sizeInBytes) determines the value to which `attr`
 * will be set.
 * \param[in] sizeInBytes Size of buf (in bytes); see \ref cutensorPlanPreferenceAttribute_t for the exact size.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorPlanPreferenceSetAttribute(
        const cutensorHandle_t handle,
        cutensorPlanPreference_t pref,
        cutensorPlanPreferenceAttribute_t attr,
        const void *buf,
        size_t sizeInBytes);

/**
 * \brief Retrieves information about an already-created plan (see \ref cutensorPlanAttribute_t)
 *
 * Block-sparse contraction plans only support CUTENSOR_PLAN_REQUIRED_WORKSPACE.
 *
 * \param[in] plan Denotes an already-created plan (e.g., via \ref cutensorCreatePlan or \ref cutensorCreatePlanAutotuned)
 * \param[in] attr Requested attribute.
 * \param[out] buf On successful exit: Holds the information of the requested attribute.
 * \param[in] sizeInBytes size of `buf` in bytes.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorPlanGetAttribute(const cutensorHandle_t handle,
        const cutensorPlan_t plan,
        cutensorPlanAttribute_t attr,
        void* buf,
        size_t sizeInBytes);

/**
 * \brief Determines the required workspaceSize for the given operation encoded by `desc`.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] desc This opaque struct encodes the operation.
 * \param[in] planPref This opaque struct restricts the space of viable candidates.
 * \param[in] workspacePref This parameter influences the size of the workspace; see \ref cutensorWorksizePreference_t for details.
 * \param[out] workspaceSizeEstimate The workspace size (in bytes) that is required for the given operation.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorEstimateWorkspaceSize(const cutensorHandle_t handle,
                                          const cutensorOperationDescriptor_t desc,
                                          const cutensorPlanPreference_t planPref,
                                          const cutensorWorksizePreference_t workspacePref,
                                          uint64_t *workspaceSizeEstimate);

/**
 * \brief This function allocates a cutensorPlan_t object, selects an appropriate kernel for a given operation (encoded by `desc`) and prepares a plan that encodes the execution.
 *
 * \details This function applies cuTENSOR's heuristic to select a candidate/kernel for a
 * given operation (created by either \ref cutensorCreateContraction, \ref cutensorCreateReduction, \ref cutensorCreatePermutation,
 * \ref * cutensorCreateElementwiseBinary, \ref cutensorCreateElementwiseTrinary, \ref cutensorCreateContractionTrinary, or 
 * \ref cutensorCreateBlockSparseContraction). The created plan can then be be passed to either \ref cutensorContract,
 * \ref cutensorReduce, \ref cutensorPermute, \ref cutensorElementwiseBinaryExecute, \ref cutensorElementwiseTrinaryExecute, or 
 * \ref cutensorContractTrinary to perform the actual operation.
 *
 * The plan is created for the active CUDA device.
 *
 * Note: \ref cutensorCreatePlan must not be captured via CUDA graphs if Just-In-Time compilation is enabled (i.e.,
 * \ref cutensorJitMode_t is not `CUTENSOR_JIT_MODE_NONE`).
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] plan Pointer to the data structure created by this function that holds all information (e.g., selected
 * kernel) necessary to perform the desired operation.
 * \param[in] desc This opaque struct encodes the given operation (see \ref cutensorCreateContraction, \ref cutensorCreateReduction, \ref cutensorCreatePermutation, \ref
 * cutensorCreateElementwiseBinary, \ref cutensorCreateElementwiseTrinary, or \ref cutensorCreateContractionTrinary).
 * \param[in] pref This opaque struct is used to restrict the space of applicable candidates/kernels (see \ref cutensorCreatePlanPreference or \ref cutensorPlanPreferenceAttribute_t).
                   May be `nullptr`, in that case default choices are assumed. Block-sparse contractions currently only support these default settings and ignore other supplied preferences.
 * \param[in] workspaceSizeLimit Denotes the maximal workspace that the corresponding operation is allowed to use (see \ref cutensorEstimateWorkspaceSize)
 *
 * \retval CUTENSOR_STATUS_SUCCESS If a viable candidate has been found.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED If no viable candidate could be found.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_INSUFFICIENT_WORKSPACE if The provided workspace was insufficient.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
cutensorStatus_t cutensorCreatePlan(
                               const cutensorHandle_t handle,
                               cutensorPlan_t* plan,
                               const cutensorOperationDescriptor_t desc,
                               const cutensorPlanPreference_t pref,
                               uint64_t workspaceSizeLimit);

/**
 * \brief Frees all resources related to the provided plan.
 *
 * \param[in,out] plan The cutensorPlan_t object that will be deallocated.
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorDestroyPlan(cutensorPlan_t plan);

/**
 * \brief This routine computes the tensor contraction \f$ D = alpha * A * B + beta * C \f$.
 *
 * \details \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets \alpha * \mathcal{A}_{{modes}_\mathcal{A}} B_{{modes}_\mathcal{B}} + \beta \mathcal{C}_{{modes}_\mathcal{C}} \f]
 *
 * The active CUDA device must match the CUDA device that was active at the time at which the plan was created.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding the contraction execution plan (created by \ref cutensorCreateContraction followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling for A*B. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] A Pointer to the data corresponding to A. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] B Pointer to the data corresponding to B. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] beta Scaling for C. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] C Pointer to the data corresponding to C. Pointer to the GPU-accessible memory.
 * \param[out] D Pointer to the data corresponding to D. Pointer to the GPU-accessible memory.
 * \param[out] workspace Optional parameter that may be NULL. This pointer provides additional workspace, in device memory, to the library for additional optimizations; the workspace must be aligned to 256 bytes (i.e., the default alignment of cudaMalloc).
 * \param[in] workspaceSize Size of the workspace array in bytes; please refer to \ref cutensorEstimateWorkspaceSize to query the required workspace. While \ref cutensorContract does not strictly require a workspace for the contraction, it is still recommended to provided some small workspace (e.g., 128 MB).
 * \param[in] stream The CUDA stream in which all the computation is performed.
 *
 * \par[Example]
 * See https://github.com/NVIDIA/CUDALibrarySamples/tree/master/cuTENSOR/contraction.cu for a concrete example.
 *
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_ARCH_MISMATCH if the plan was created for a different device than the currently active device.
 * \retval CUTENSOR_STATUS_INSUFFICIENT_DRIVER if the driver is insufficient.
 * \retval CUTENSOR_STATUS_CUDA_ERROR if some unknown CUDA error has occurred (e.g., out of memory).
 */
cutensorStatus_t cutensorContract(
                 const cutensorHandle_t handle, const cutensorPlan_t plan,
                 const void* alpha, const void *A,
                                    const void *B,
                 const void* beta,  const void *C, void *D,
                 void* workspace, uint64_t workspaceSize, cudaStream_t stream);

/**
 * \brief Creates a cutensorOperatorDescriptor_t object that encodes a tensor reduction of the form \f$ D = alpha * opReduce(opA(A)) + beta * opC(C) \f$.
 *
 * \details
 * For example this function enables users to reduce an entire tensor to a scalar: C[] = alpha * A[i,j,k];
 *
 * This function is also able to perform partial reductions; for instance: C[i,j] = alpha * A[k,j,i]; in this case only elements along the k-mode are contracted.
 *
 * The binary opReduce operator provides extra control over what kind of a reduction
 * ought to be performed. For instance, setting opReduce to `CUTENSOR_OP_ADD` reduces element of A
 * via a summation while `CUTENSOR_OP_MAX` would find the largest element in A.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+---------------+-----------------------------+
 * |     typeA     |     typeB     |     typeC     |       typeCompute           |
 * +===============+===============+===============+=============================+
 * | `CUDA_R_16F ` | `CUDA_R_16F`  | `CUDA_R_16F`  | `CUTENSOR_COMPUTE_DESC_16F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_R_16F`  | `CUDA_R_16F`  | `CUDA_R_16F`  | `CUTENSOR_COMPUTE_DESC_32F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_R_16BF` | `CUDA_R_16BF` | `CUDA_R_16BF` | `CUTENSOR_COMPUTE_DESC_16BF`|
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_R_16BF` | `CUDA_R_16BF` | `CUDA_R_16BF` | `CUTENSOR_COMPUTE_DESC_32F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_R_32F`  | `CUDA_R_32F`  | `CUDA_R_32F`  | `CUTENSOR_COMPUTE_DESC_32F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_R_64F`  | `CUDA_R_64F`  | `CUDA_R_64F`  | `CUTENSOR_COMPUTE_DESC_64F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_C_32F`  | `CUDA_C_32F`  | `CUDA_C_32F`  | `CUTENSOR_COMPUTE_DESC_32F` |
 * +---------------+---------------+---------------+-----------------------------+
 * | `CUDA_C_64F`  | `CUDA_C_64F`  | `CUDA_C_64F`  | `CUTENSOR_COMPUTE_DESC_64F` |
 * +---------------+---------------+---------------+-----------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 * the requested tensor reduction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes and strides of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref cutensorCreateTensorDescriptor. Modes that only appear in modeA but not in modeC are reduced (contracted).
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC The descriptor that holds the information about the data type, modes and strides of C.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. modeC[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref cutensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD Must be identical to descC for now.
 * \param[in] modeD Must be identical to modeC for now.
 * \param[in] opReduce binary operator used to reduce elements of A.
 * \param[in] typeCompute All arithmetic is performed using this data type (i.e., it affects the accuracy and performance).
 *
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
cutensorStatus_t cutensorCreateReduction(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
                 const cutensorTensorDescriptor_t descD, const int32_t modeD[],
                 cutensorOperator_t opReduce, const cutensorComputeDescriptor_t descCompute);


/**
 * \brief Performs the tensor reduction that is encoded by `plan` (see \ref cutensorCreateReduction).
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding the reduction execution plan (created by \ref cutensorCreateReduction followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling for A. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] A Pointer to the data corresponding to A in device memory. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to D.
 * \param[in] beta Scaling for C. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] C Pointer to the data corresponding to C in device memory. Pointer to the GPU-accessible memory.
 * \param[out] D Pointer to the data corresponding to C in device memory. Pointer to the GPU-accessible memory.
 * \param[out] workspace Scratchpad (device) memory of size --at least-- `workspaceSize` bytes; the workspace must be aligned to 256 bytes (i.e., the default alignment of cudaMalloc).
 * \param[in] workspaceSize Please use \ref cutensorEstimateWorkspaceSize() to query the required workspace.
 * \param[in] stream The CUDA stream in which all the computation is performed.
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 */
cutensorStatus_t cutensorReduce(
                 const cutensorHandle_t handle, const cutensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* beta,  const void* C,
                                          void* D,
                 void* workspace, uint64_t workspaceSize,
                 cudaStream_t stream);

/**
 * \brief This function allocates a cutensorOperationDescriptor_t object that encodes a tensor contraction of the form \f$ \mathcal{E} = \alpha \mathcal{A} \mathcal{B} \mathcal{C} + \beta \mathcal{D} \f$.
 *
 * \details Allocates data for `desc` to be used to perform a tensor contraction of the form \f[ \mathcal{E}_{{modes}_\mathcal{E}} \gets \alpha op_\mathcal{A}(\mathcal{A}_{{modes}_\mathcal{A}}) op_\mathcal{B}(\mathcal{B}_{{modes}_\mathcal{B}}) op_\mathcal{C}(\mathcal{C}_{{modes}_\mathcal{C}}) + \beta op_\mathcal{D}(\mathcal{D}_{{modes}_\mathcal{D}}). \f]
 *
 * See \ref cutensorCreatePlan (or \ref cutensorCreatePlanAutotuned) to create the plan
 * (i.e., to select the kernel) followed by a call to \ref cutensorContractTrinary to perform the
 * actual contraction.
 *
 * The user is responsible for calling \ref cutensorDestroyOperationDescriptor to free the resources associated
 * with the descriptor.
 *
 * The performance improvements due to this API are currently especially high if your data resides on the host (i.e. out-of-core), targeting Grace-based systems.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |     typeA     |     typeB     |     typeC     |     typeD     |        descCompute           |  typeScalar   | Tensor Core |
 * +===============+===============+===============+===============+==============================+===============+=============+
 * |  CUDA_R_16F   |  CUDA_R_16F   |  CUDA_R_16F   |  CUDA_R_16F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | Volta+      |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUDA_R_16BF  |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   | No          |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_TF32  |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_3XTF32|  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_16BF  |  CUDA_R_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_16F   |  CUDA_R_32F   | Volta+      |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_R_64F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_64F   | No          |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_C_32F   | No          |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_TF32  |  CUDA_C_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_3XTF32|  CUDA_C_32F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_C_64F   | Ampere+     |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_C_64F   | No          |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+-------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 * the tensor contraction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes and strides of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB The descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array with 'nmodeB' entries that represent the modes of B. The modeB[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC The escriptor that holds information about the data type, modes, and strides of C.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. The modeC[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD The escriptor that holds information about the data type, modes, and strides of D.
 * \param[in] modeD Array with 'nmodeD' entries that represent the modes of D. The modeD[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] opD Unary operator that will be applied to each element of D before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] modeE Array with 'nmodeE' entries that represent the modes of E (must be identical to modeD for now). The modeE[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to cutensorInitTensorDescriptor.
 * \param[in] descE The descriptor that holds information about the data type, modes, and strides of E (must be identical to `descD` for now).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
cutensorStatus_t cutensorCreateContractionTrinary(
                 const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
                 const cutensorTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
                 const cutensorTensorDescriptor_t descB, const int32_t modeB[], cutensorOperator_t opB,
                 const cutensorTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
                 const cutensorTensorDescriptor_t descD, const int32_t modeD[], cutensorOperator_t opD,
                 const cutensorTensorDescriptor_t descE, const int32_t modeE[],
                 const cutensorComputeDescriptor_t descCompute);

/**
 * \brief This routine computes the tensor contraction \f$ E = alpha * A * B * C + beta * D \f$.
 *
 * \details \f[ \mathcal{E}_{{modes}_\mathcal{E}} \gets \alpha * \mathcal{A}_{{modes}_\mathcal{A}} \mathcal{B}_{{modes}_\mathcal{B}} \mathcal{C}_{{modes}_\mathcal{C}} + \beta \mathcal{D}_{{modes}_\mathcal{D}} \f]
 *
 * The active CUDA device must match the CUDA device that was active at the time at which the plan was created.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding the contraction execution plan (created by \ref cutensorCreateContractionTrinary followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling for A*B*C. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] A Pointer to the data corresponding to A. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to E.
 * \param[in] B Pointer to the data corresponding to B. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to E.
 * \param[in] C Pointer to the data corresponding to C. Pointer to the GPU-accessible memory. The data accessed via this pointer must not overlap with the elements written to E.
 * \param[in] beta Scaling for D. Its data type is determined by 'descCompute' (see \ref cutensorOperationDescriptorGetAttribute(desc, CUTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] D Pointer to the data corresponding to D. Pointer to the GPU-accessible memory.
 * \param[out] E Pointer to the data corresponding to E. Pointer to the GPU-accessible memory.
 * \param[out] workspace Optional parameter that may be NULL. This pointer provides additional workspace, in device memory, to the library for additional optimizations; the workspace must be aligned to 256 bytes (i.e., the default alignment of cudaMalloc).
 * \param[in] workspaceSize Size of the workspace array in bytes; please refer to \ref cutensorEstimateWorkspaceSize to query the required workspace. While \ref cutensorContract does not strictly require a workspace for the contraction, it is still recommended to provided some small workspace (e.g., 128 MB).
 * \param[in] stream The CUDA stream in which all the computation is performed.
 *
 * \par[Example]
 * See https://github.com/NVIDIA/CUDALibrarySamples/tree/master/cuTENSOR/contraction_trinary.cu for a concrete example.
 *
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_ARCH_MISMATCH if the plan was created for a different device than the currently active device.
 * \retval CUTENSOR_STATUS_INSUFFICIENT_DRIVER if the driver is insufficient.
 * \retval CUTENSOR_STATUS_CUDA_ERROR if some unknown CUDA error has occurred (e.g., out of memory).
 */
cutensorStatus_t cutensorContractTrinary(const cutensorHandle_t handle, const cutensorPlan_t plan,
                                         const void* alpha, const void* A,
                                                            const void* B,
                                                            const void* C,
                                         const void* beta,  const void* D,
                                                                  void* E,
                                         void* workspace, uint64_t workspaceSize,
                                         cudaStream_t stream);


/*
 * PUBLIC BETA: Block-sparse tensor contractions. USE AT YOUR OWN RISK.
 *
 * cuTENSOR's block-sparse functionality is a public beta feature. The current
 * block-sparse backend is not as feature-rich as cuTENSOR's dense counterpart 
 * (e.g., only support a limited set of data types, no conjugate support, only 
 * tensors up to 8D) and we are aware of some performance improvements that we 
 * are planning to provide as part of follow-up releases. While we intend to 
 * keep the API stable from one release to the next, we cannot guarantee this 
 * at this point due to the experimental nature of this API.
 *
 * We would much appreciate your feedback to guide this development process and
 * steer these future optimizations in the right direction.
 */

/**
 * \brief Create a block-sparse tensor descriptor
 *
 * \details A block-sparse tensor descriptor fully specifies the data layout of a 
 *  block-sparse tensor (currently limited to up to 8 modes).
 *
 * Let us consider an example for a block-sparse tensor of order 2, i.e.,
 * a block-sparse matrix `A`.  Its first mode (`rows`) is subdivided
 * into 5 sections (with extents 4, 2, 3, 4, 5, respectively), and its 
 * second mode (`columns`) is subdivided into 3 sections 
 * (with extents 2, 3, 7). The matrix has 8 non-zero blocks:
 *
 * \verbatim embed:rst:leading-asterisk
 * +-------+-------+-------+
 * | 4 x 2 |       | 4 x 7 |
 * +-------+-------+-------+
 * |       | 2 x 3 |       |
 * +-------+-------+-------+
 * |       | 3 x 3 | 3 x 7 |
 * +-------+-------+-------+
 * | 4 x 2 |       |       |
 * +-------+-------+-------+
 * |       | 5 x 3 | 5 x 7 |
 * +-------+-------+-------+
 * \endverbatim
 * 
 * Notice that we require the same extent of each sub section across the entire mode, i.e., 
 * every block within the same section of a mode has the same extent. For example, in the
 * above picture every block on the right has 7 colums, and all blocks on the bottom 
 * have 5 rows.
 *
 * Moreover, we only store the non-zero blocks (blocks that are zero are left blank in
 * the above representation).
 *
 * To be precise, the above block-sparse tensor could be created via:
 *
 * \code{.cpp}
 * uint32_t numModes = 2;
 * uint64_t numNonZeroBlocks = 8;
 * const uint32_t sectionsPerMode[] = {5, 3}; // Array of size numModes
 * const int64_t extent[] =                   // Array of size Sum(sectionsPerMode)
 * {
 *      4, 2, 3, 4, 5, // extents of sections of first  mode
 *      2, 3, 7        // extents of sections of second mode
 * };
 *
 * const int32_t nonZeroCoordinates[] = // Array of size numModes x numNonZeroBlocks
 * {
 *      0, 0, // Block 0.     List of non-zero blocks in the block-sparse tensor.
 *      3, 0, // Block 1.     Blocks may be listed in an arbitrary order, however,
 *      1, 1, // Block 2.     this order must remain the same for every subsequent 
 *      2, 1, // Block 3.     operation.
 *      4, 1, // Block 4.     For example, when calling cutensorBlockSparseContract,
 *      0, 2, // Block 5.     pointers to the blocks need to be given in this order.
 *      2, 2, // Block 6.     The strides of the blocks in the stride[] array also     
 *      4, 2  // Block 7.     need to be given the same order as in this list. 
 * };
 *      ^  ^
 *      |  |
 *      |  \--- Section number of second mode,  block-column number
 *      \------ Section number of first  mode,  block-row number
 *
 *
 * const int64_t stride[] = // Either nullptr or an array of size numModes x numNonZeroBlocks
 * {
 *      1, 4,  // Block 0.   Strides for each block, given in the same order as in
 *      1, 4,  // Block 1.   the array nonZeroCoordinates.  
 *      1, 2,  // Block 2.   
 *      1, 3,  // Block 3.   In this example, each block is stored contiguously in
 *      1, 5,  // Block 4.   column-major order; this is equivalent to passing stride=nullptr.
 *      1, 4,  // Block 5.   
 *      1, 3,  // Block 6.   However, other memory layouts are also allowed, see documentation
 *      1, 5   // Block 7.   below.
 * };
 *
 * cudaDataType_t dataType = CUDA_C_64F; // For example: complex-valued double-precision.
 * \endcode
 *
 * \param[in] handle The library handle.
 * \param[out] desc The resulting block-sparse tensor descriptor.
 * \param[in] numModes The number of modes. Currently, a maximum of 8 modes is supported.
 * \param[in] numNonZeroBlocks The number of non-zero blocks in the block-sparse tensor.
 * \param[in] numSectionsePerMode The number of sections of each mode (host array of size `numModes`).
 * \param[in] extent The extents of the sections of each mode (host array of size `\sum_i^numModes(numSectionsPerMode[i])`).
 *            First come the extents of the sections of the first mode, then the extents of the sections of the second mode, and so forth.
 * \param[in] nonZeroCoordinates Block-coordinates of each non-zero block (host array of size `numModes` x `numNonZeroBlocks`
 *            Blocks can be specified in any order, however, that order must be consistent with stride and alignmentRequirement arrays.            
 * \param[in] stride The strides of each dense block (either nullptr or a host array of size `numModes` x `numNonZeroBlocks`). 
 *            First the strides of the first block, then the strides of the second block, with the blocks in the same order as in
 *            nonZeroCoordinates. Passing nullptr means contiguous column-major order for each block.
 *            Moreover, the strides need to be compatible in the following sense: Suppose you sort the strides of the first block, such
 *            that they are ascending; this sorting results in a permutation. If you apply this 
 *            permutation to the strides of any other block, the result needs to be sorted as well.
 *
 *            As an example:
 *             - strides of block #0: 5, 1, 10, 20. Sorted strides would be: 1, 5, 10, 20.
 *               The permutation to sort the strides in this case is to swap the first two elements.
 *             - strides of block #1: 10, 1, 30, 60. Applying the permutation would result in: 1, 10, 30, 60.
 *               The result is sorted in ascending order, this is allowed.
 *             - strides of block #2: 1, 5, 50, 100. Applying permuation would result in: 5, 1, 50, 100.
 *               The result is _not_ sorted in ascending order, this is _not_ allowed.
 * \param[in] dataType Data type of the stored entries. We assume the same datatype for each block.
 *            Currently, the only supported values are CUDA_C_64F, CUDA_C_32F, CUDA_R_64F, and CUDA_R_32F.
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t cutensorCreateBlockSparseTensorDescriptor
(
    cutensorHandle_t handle,
    cutensorBlockSparseTensorDescriptor_t* desc,
    const uint32_t     numModes,
    const uint64_t     numNonZeroBlocks,
    const uint32_t     numSectionsPerMode[],
    const  int64_t     extent[],
    const  int32_t     nonZeroCoordinates[],
    const  int64_t     stride[],
    cudaDataType_t     dataType
);

/**
 * \brief Frees all resources related to the provided block-sparse tensor descriptor.
 *
 * \param[in,out] desc The cutensorBlockSparseTensorDescrptor_t object that will be deallocated.
 * \retval CUTENSOR_STATUS_SUCCESS on success and an error code otherwise.
 * \remarks blocking, no reentrant, and thread-safe.
 */
cutensorStatus_t cutensorDestroyBlockSparseTensorDescriptor(cutensorBlockSparseTensorDescriptor_t desc);

/**
 * \brief This function allocates a cutensorOperationDescriptor_t object that encodes a block-sparse tensor contraction of the form \f$ D = \alpha \mathcal{A}  \mathcal{B} + \beta \mathcal{C} \f$.
 *
 * \details 
 * Allocates data for `desc` to be used to perform a block-sparse tensor 
 * contraction of the form 
 * \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets 
 *     \alpha op_\mathcal{A}(\mathcal{A}_{{modes}_\mathcal{A}}) 
 *            op_\mathcal{B}(B_{{modes}_\mathcal{B}}) + 
 *     \beta  op_\mathcal{C}(\mathcal{C}_{{modes}_\mathcal{C}}). \f] 
 * 
 * Only the predefined non-zero blocks of \f$\mathcal{D}\f$ that were specified
 * in cutensorCreateBlockSparseTensorDescriptor() are actually computed. The 
 * other blocks are omitted, even if the true result of the contraction would 
 * be non-zero. Conversely, if a predefined non-zero block of \f$\mathcal{D}\f$ 
 * is present, but the result of the contraction is zero for this block, 
 * explicit zeros will be stored.
 *
 * Currently, the data-types for the tensors `A`, `B`, `C`, and `D`, as well as
 * the scalars \f$ \alpha \f$ and \f$ \beta \f$ must all be identical, and the
 * only supported types are CUDA_C_64F, CUDA_C_32F, CUDA_R_64F, and CUDA_R_32F.
 * The compute-type needs to match as well, that is, we currently only support:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+
 * |     typeA     |     typeB     |     typeC     |     typeD     |        descCompute           |  typeScalar   |
 * +===============+===============+===============+===============+==============================+===============+
 * |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUDA_R_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_R_32F   |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+
 * |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUDA_R_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_R_64F   |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+
 * |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUDA_C_32F   |  CUTENSOR_COMPUTE_DESC_32F   |  CUDA_C_32F   |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+
 * |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUDA_C_64F   |  CUTENSOR_COMPUTE_DESC_64F   |  CUDA_C_64F   |
 * +---------------+---------------+---------------+---------------+------------------------------+---------------+
 * \endverbatim
 *
 * For every mode, the segmentation of that mode must be identical in all
 * tensors that it occurs in. For example, if modeA[i] = modeB[j] for some i
 * and j, then numSectionsPerMode[i] of tensor A must have the same value as
 * numSectionsPerMode[j] of tensor B, and the corresponding section extents 
 * must be identical.
 *
 * For example, let A, B, and C be block matrices and consider the ordinary 
 * matrix-matrix product \f$C_{mn}=A_{mk}B_{kn}\f$. Then:
 *      - Mode 'm': C and A need to have the same number of block-rows, and 
 *        each block-row of C needs to contain the same number of rows as the 
 *        corresponding block-row of A.
 *      - Mode 'n': C and B need to have the same number of block-columns of 
 *        matching size
 *      - Mode 'k': A needs to have the same number of block-columns as B has
 *        block-rows, and each block-column of A needs to consist of the same 
 *        number of columns as the number of rows in the corresponding 
 *        block-row of B.
 *
 * At the moment, descC and descD must be identical, i.e., the same opaque
 * pointer needs to be passed and the layouts of the C and the D tensors need 
 * to be identical.
 *
 * See \ref cutensorCreatePlan to create the plan, 
 * \ref cutensorEstimateWorkspaceSize to compute the required workspace, and 
 * finally \ref cutensorBlockSparseContract to perform the actual contraction.
 *
 * The user is responsible for calling \ref cutensorDestroyOperationDescriptor
 * to free the resources associated with the descriptor.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 *                  the tensor contraction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes, sections, section extents, strides, and non-zero blocks of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. Sections, i.e., block-sizes, must match among the involved block-sparse tensors.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 *                Currently, only CUTENSOR_OP_IDENTITY is supported.
 * \param[in] descB The descriptor that holds information about the the data type, modes, sections, section extents, strides, and non-zero blocks of B.
 * \param[in] modeB Array with 'nmodeB' entries that represent the modes of B. Sections, i.e., block-sizes, must match among the involved block-sparse tensors.
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 *                Currently, only CUTENSOR_OP_IDENTITY is supported.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. Sections, i.e., block-sizes, must match among the involved block-sparse tensors.
 * \param[in] descC The descriptor that holds information about the data type, modes, sections, section extents, strides, and non-zero blocks of C.
 *                  Note that the block-sparsity pattern of C (the nonZeroCoordinates[] array used to create the decriptor) of C must be identical to that of D;
 *                  and it is this block-sparsity pattern that determines which parts of the results are computed; no fill-in is allocated or computed.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 *                  Currently, only CUTENSOR_OP_IDENTITY is supported.
 * \param[in] descD For now, this must be the same opaque pointer as descC, and the layouts of C and D must be identical.
 * \param[in] modeD Array with 'nmodeD' entries that represent the modes of D (must be identical to modeC for now). 
 * \param[in] typeCompute Datatype of for the intermediate computation of typeCompute T = A * B.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval CUTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes or section sizes have an illegal value
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
cutensorStatus_t cutensorCreateBlockSparseContraction
(
    const cutensorHandle_t handle, cutensorOperationDescriptor_t* desc,
    const cutensorBlockSparseTensorDescriptor_t descA, const int32_t modeA[], cutensorOperator_t opA,
    const cutensorBlockSparseTensorDescriptor_t descB, const int32_t modeB[], cutensorOperator_t opB,
    const cutensorBlockSparseTensorDescriptor_t descC, const int32_t modeC[], cutensorOperator_t opC,
    const cutensorBlockSparseTensorDescriptor_t descD, const int32_t modeD[],
    const cutensorComputeDescriptor_t descCompute
);

/**
 * \brief This routine computes the block-sparse tensor contraction \f$ D = alpha * A * B + beta * C \f$.
 *
 * \details \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets \alpha * \mathcal{A}_{{modes}_\mathcal{A}} B_{{modes}_\mathcal{B}} + \beta \mathcal{C}_{{modes}_\mathcal{C}} \f]
 *
 * The active CUDA device must match the CUDA device that was active at the time at which the plan was created.
 *
 * The array-parameters `A`, `B`, `C`, and `D` are host-arrays containing pointers to GPU-accessible memory. For example,
 * `A` is a host-array whose size equals the number of non-zero blocks in tensor \f$\mathcal{A}\f$. `A[i]` is a pointer to the 
 * GPU-accessible memory location of block number `i` of \f$\mathcal{A}\f$. The blocks are numbered in the same way as in the 
 * construction of \f$\mathcal{A}\f$'s block-sparse tensor descriptor. The same analogously holds for the other 
 * array-parameters `B`, `C`, and `D`.
 *
 * \param[in] handle Opaque handle holding cuTENSOR's library context.
 * \param[in] plan Opaque handle holding the contraction execution plan (created by \ref cutensorCreateBlockSparseContraction followed by \ref cutensorCreatePlan).
 * \param[in] alpha Scaling for A*B. Its data type is determined by 'descCompute' (see \ref cutensorCreateBlockSparseContraction). Pointer to host memory.
 * \param[in] A Host-array of size numNonZeroBlocks(A), containing pointers to GPU-accessible memory, corresponding the blocks of A.
 *            The data accessed via these pointers must not overlap with the elements written to D.
 * \param[in] B Host-array of size numNonZeroBlocks(B), containing pointers to GPU-accessible memory, corresponding the blocks of B.
 *            The data accessed via these pointers must not overlap with the elements written to D.
 * \param[in] beta Scaling for C. Its data type is determined by 'descCompute' (see \ref cutensorCreateBlockSparseContraction). Pointer to host memory.
 * \param[in]  C Host-array of size numNonZeroBlocks(C), containing pointers to GPU-accessible memory, corresponding the blocks of C.
 * \param[out] D Host-array of size numNonZeroBlocks(D), containing pointers to GPU-accessible memory, corresponding the blocks of D.
 * \param[out] workspace This pointer provides the required workspace in device memory. The workspace must be aligned to 256 bytes (i.e., the default alignment of cudaMalloc).
 * \param[in] workspaceSize Size of the workspace array in bytes; please refer to \ref cutensorEstimateWorkspaceSize to query the required workspace.
 *                          For block-sparse contractions, this estimate is exact.
 * \param[in] stream The CUDA stream to which all of the computation is synchronised. 
 *
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval CUTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval CUTENSOR_STATUS_ARCH_MISMATCH if the plan was created for a different device than the currently active device.
 * \retval CUTENSOR_STATUS_INSUFFICIENT_DRIVER if the driver is insufficient.
 * \retval CUTENSOR_STATUS_CUDA_ERROR if some unknown CUDA error has occurred (e.g., out of memory).
 */
cutensorStatus_t cutensorBlockSparseContract
(
    const cutensorHandle_t handle, const cutensorPlan_t plan,
    const void* alpha, const void *const A[],
                       const void *const B[],
    const void* beta,  const void *const C[], void *const D[],
    void* workspace, uint64_t workspaceSize, cudaStream_t stream
);


/**
 * \brief Returns the description string for an error code
 * \param[in] error Error code to convert to string.
 * \retval The null-terminated error string.
 * \remarks non-blocking, no reentrant, and thread-safe
 */
const char* cutensorGetErrorString(const cutensorStatus_t error);

/**
 * \brief Returns Version number of the CUTENSOR library
 */
size_t cutensorGetVersion();

/**
 * \brief Returns version number of the CUDA runtime that cuTENSOR was compiled against
 * \details Can be compared against the CUDA runtime version from cudaRuntimeGetVersion().
 */
size_t cutensorGetCudartVersion();

/**
 * \brief This function sets the logging callback routine.
 * \param[in] callback Pointer to a callback function. Check cutensorLoggerCallback_t.
 */
cutensorStatus_t cutensorLoggerSetCallback(cutensorLoggerCallback_t callback);

/**
 * \brief This function sets the logging output file.
 * \param[in] file An open file with write permission.
 */
cutensorStatus_t cutensorLoggerSetFile(FILE* file);

/**
 * \brief This function opens a logging output file in the given path.
 * \param[in] logFile Path to the logging output file.
 */
cutensorStatus_t cutensorLoggerOpenFile(const char* logFile);

/**
 * \brief This function sets the value of the logging level.
 * \param[in] level Log level, should be one of the following:
 * <ul>
 *                  <li>0.  Off</li>
 *                  <li>1.  Errors</li>
 *                  <li>2.  Performance Trace</li>
 *                  <li>3.  Performance Hints</li>
 *                  <li>4.  Heuristics Trace</li>
 *                  <li>5.  API Trace</li>
 * </ul>
 */
cutensorStatus_t cutensorLoggerSetLevel(int32_t level);

/**
 * \brief This function sets the value of the log mask.
 * \param[in] mask Log mask, the bitwise OR of the following:
 * <ul>
 *                 <li>0.  Off</li>
 *                 <li>1.  Errors</li>
 *                 <li>2.  Performance Trace</li>
 *                 <li>4.  Performance Hints</li>
 *                 <li>8.  Heuristics Trace</li>
 *                 <li>16. API Trace</li>
 * </ul>
 */
cutensorStatus_t cutensorLoggerSetMask(int32_t mask);

/**
 * \brief This function disables logging for the entire run.
 */
cutensorStatus_t cutensorLoggerForceDisable();

#ifdef _MSC_VER
#define CUTENSOR_DEPRECATED(new_func) __declspec(deprecated("please use " #new_func " instead."))
#elif defined(__GNUC__)
#define CUTENSOR_DEPRECATED(new_func) __attribute__((deprecated("please use " #new_func " instead.")))
#else
#define CUTENSOR_DEPRECATED(new_func)
#endif


#if defined(__cplusplus)
}
#endif /* __cplusplus */
