/*
 * Copyright (c) 2021-2022, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 *
 *
 * cuTENSORMg uses github.com/springer13/hptt
 * ------------------------------------------
 *
 * Copyright 2018 Paul Springer
 * 
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * 
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#pragma once

#include <stdint.h>
#include <cutensor.h>

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

/**
 * \brief Encodes cuTENSOR's compute type (see "User Guide - Accuracy Guarantees" for details).
 */
typedef enum
{
    CUTENSOR_COMPUTE_16F    = (1U<< 0U),  ///< floating-point: 5-bit exponent and 10-bit mantissa (aka half)
    CUTENSOR_COMPUTE_16BF   = (1U<< 10U), ///< floating-point: 8-bit exponent and 7-bit mantissa (aka bfloat)
    CUTENSOR_COMPUTE_TF32   = (1U<< 12U), ///< floating-point: 8-bit exponent and 10-bit mantissa (aka tensor-float-32)
    CUTENSOR_COMPUTE_3XTF32 = (1U<< 13U), ///< floating-point: More precise than TF32, but less precise than float
    CUTENSOR_COMPUTE_32F    = (1U<< 2U),  ///< floating-point: 8-bit exponent and 23-bit mantissa (aka float)
    CUTENSOR_COMPUTE_64F    = (1U<< 4U),  ///< floating-point: 11-bit exponent and 52-bit mantissa (aka double)
    CUTENSOR_COMPUTE_8U     = (1U<< 6U),  ///< 8-bit unsigned integer
    CUTENSOR_COMPUTE_8I     = (1U<< 8U),  ///< 8-bit signed integer
    CUTENSOR_COMPUTE_32U    = (1U<< 7U),  ///< 32-bit unsigned integer
    CUTENSOR_COMPUTE_32I    = (1U<< 9U),  ///< 32-bit signed integer
} cutensorComputeType_t;

/**
 * \brief Enumerated device codes for host-side tensors
 */
enum cutensorMgHostDevice_t
{
    /// The memory is located on the host in regular memory
    CUTENSOR_MG_DEVICE_HOST = -1,
    /// The memory is located on the host in pinned memory
    CUTENSOR_MG_DEVICE_HOST_PINNED = -2
};

struct cutensorMgHandle_s;
/**
 * \brief Encodes the devices that participate in operations
 *
 * \details The handle contains information about each device that participates in
 *     operations as well as host threads to orchestrate host-to-device operations.
 *
 */
typedef struct cutensorMgHandle_s* cutensorMgHandle_t;

struct cutensorMgTensorDescriptor_s;
/**
 * \brief Represents a tensor that may be distributed
 *
 * \details The tensor is laid out in a block-cyclic fashion across devices.
 *     It may either be fully located on the host, or distributed across multiple
 *     devices.
 *
 */
typedef struct cutensorMgTensorDescriptor_s* cutensorMgTensorDescriptor_t;

struct cutensorMgCopyDescriptor_s;
/**
 * \brief Describes the copy of a tensor from one data layout to another
 *
 * \details It may describe the full cartesion product of copy from and to
 *     host, single device, and multiple devices, as well as permutations and
 *     layout changes.
 *
 */
typedef struct cutensorMgCopyDescriptor_s* cutensorMgCopyDescriptor_t;

struct cutensorMgCopyPlan_s;
/**
 * \brief Describes a specific way to implement the copy operation
 *
 * \details It encodes blockings and other implementation details, and may be
 *     reused to reduce planning overhead.
 *
 */
typedef struct cutensorMgCopyPlan_s* cutensorMgCopyPlan_t;

struct cutensorMgContractionDescriptor_s;
/**
 * \brief Describes the contraction of two tensors into a third tensor with an optional source
 *
 * \details Only supports device-side tensors.
 *
 */
typedef struct cutensorMgContractionDescriptor_s* cutensorMgContractionDescriptor_t;

struct cutensorMgContractionFind_s;
/**
 * \brief Describes the algorithmic details of implementing a tensor contraction
 *
 */
typedef struct cutensorMgContractionFind_s* cutensorMgContractionFind_t;

struct cutensorMgContractionPlan_s;
/**
 * \brief Describes a specific way to implement a contraction operation
 *
 * \details It encodes blockings, permutations and other implementation details,
 *     and may be reused to reduce planning overhead.
 *
 */
typedef struct cutensorMgContractionPlan_s* cutensorMgContractionPlan_t;

/**
 * \brief Represents the selected algorithm when planning for a contraction operation
 */
typedef enum
{
    CUTENSORMG_ALGO_DEFAULT           = -1, ///< Lets the internal heuristic choose
} cutensorMgAlgo_t;

/**
 * \brief Represents various attributes for the contraction find
 *
 * \details While empty for now, future attributes will allow for a more
 *     fine-grained tuning of the distributed tensor contraction.
 */
typedef enum
{
    CUTENSORMG_CONTRACTION_FIND_ATTRIBUTE_MAX = 0xFFFF  ///< Not an actual attribute, but the maximum value that the enum takes on
} cutensorMgContractionFindAttribute_t;

/**
 * \brief Create a library handle
 *
 * \details The handle contains information about the devices that should be participating in
 *     calculations. All devices that hold any tensor data or participate in any of cuTENSORMg's operations should also be included in the
 *     handle. Each device may only occur once in the list.
 *     It is advisable that all devices are identical (i.e., have the same peak performance) to avoid load-balancing
 *     issues, and are connected via NVLink to avoid costly device-host-device
 *     transfers. This call will enable peering between all devices that have
 *     been passed to it, if possible.
 *
 * \param[out] handle The resulting library handle.
 * \param[in] numDevices The number of devices participating in all subsequent computations.
 * \param[in] devices The devices that participate in all computations.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreate(
    cutensorMgHandle_t* handle,
    uint32_t numDevices,
    const int32_t devices[]
);

/**
 * \brief Destroy a library handle
 *
 * \details All outstanding operations must be completed before calling this function.
 *     Frees all associated resources. Any descriptors or plans created with
 *     the handle become invalid and may only be destructed.
 *
 * \param[in] handle The handle to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroy(
    cutensorMgHandle_t handle
);

/**
 * \brief Create a tensor descriptor
 *
 * \details A tensor descriptor fully specifies the data layout of a (potentially)
 *     distributed tensor. It does so mainly through five pieces of data:
 *     The extent, the element stride, the block size, the block stride, and the
 *     device count.
 *
 *     The extent describes the total size of each tensor mode.
 *     For example, an 9 by 9 matrix would have an extent of 9 and 9.
 *
 *     The block size describes how the data is blocked. For example, with a
 *     block size of 4 by 2, there would be three blocks in the first and five
 *     blocks in the second mode.
 *
 *     \verbatim embed:rst:leading-asterisk
 *     +-------+-------+-------+
 *     | 4 x 2 | 4 x 2 | 1 x 2 |
 *     +-------+-------+-------+
 *     | 4 x 2 | 4 x 2 | 1 x 2 |
 *     +-------+-------+-------+
 *     | 4 x 2 | 4 x 2 | 1 x 2 |
 *     +-------+-------+-------+
 *     | 4 x 2 | 4 x 2 | 1 x 2 |
 *     +-------+-------+-------+
 *     | 4 x 1 | 4 x 1 | 1 x 1 |
 *     +-------+-------+-------+
 *     \endverbatim
 *
 *     The device count then describes how many
 *     devices the blocks are distributed across in that mode. A device count of
 *     2 by 2, for example, would mean that the blocks are distributed across
 *     two devices in each mode, i.e., four devices total. The devices are aranged
 *     first along the first and then the second mode as follows:
 *
 *     \verbatim embed:rst:leading-asterisk
 *     +--------+--------+
 *     | Dev. 0 | Dev. 2 |
 *     +--------+--------+
 *     | Dev. 1 | Dev. 3 |
 *     +--------+--------+
 *     \endverbatim
 *
 *     In particular, device 0 would own the first, and third block in the first
 *     dimension, the first, third, and fifth block in the second dimension (so a total of
 *     six blocks), device 1 would own the first and third block in the first dimension,
 *     and the second and fourth block in the second dimension (four blocks total), device
 *     2 would own the second block in the first dimension, and the first, third, and
 *     fifth block in the second dimension (for a total of three blocks), and, finally,
 *     device 3 would own the second block in the first dimension and the second and
 *     fourth block in the second dimension (for a total of two blocks).
 *
 *     \verbatim embed:rst:leading-asterisk
 *     +--------+--------+--------+
 *     | Dev. 0 | Dev. 2 | Dev. 0 |
 *     +--------+--------+--------+
 *     | Dev. 1 | Dev. 3 | Dev. 1 |
 *     +--------+--------+--------+
 *     | Dev. 0 | Dev. 2 | Dev. 0 |
 *     +--------+--------+--------+
 *     | Dev. 1 | Dev. 3 | Dev. 1 |
 *     +--------+--------+--------+
 *     | Dev. 0 | Dev. 2 | Dev. 0 |
 *     +--------+--------+--------+
 *     \endverbatim
 *
 *     The element stride and block stride then describe how the blocks are laid
 *     out on the individual devices, i.e. the distance between elements and blocks
 *     in that mode. Finally, the devices array describes which device the blocks
 *     are mapped to. Here, it is permissible to specify `CUTENSOR_MG_DEVICE_HOST`
 *     to express that those blocks are located on the host.
 *     A tensor must either be located fully on-device or fully on-host.
 *
 *     Tensors may also be replicated, where the same tensor data is distributed
 *     across devices, or a mixture of replicated and distributed. Replication is
 *     expressed by setting numDevices to a value that is a multiple of the
 *     product of deviceCounts. At that point, the devices tensor is assumed
 *     to have an extra final mode across which the tensor is replicated.
 *     Replicated tensors can be used everywhere except as outputs for contractions.
 *.    Particularly, passing replicated tensors can unlock new optimizations that
 *.    are advantageous for problems that benefit from reduced communication.
 *
 *     For instance, with devices = {0,1,2,3, 4,5,6,7} the tensor would be replicated
 *.    as follows:
 *
 *     \verbatim embed:rst:leading-asterisk
 *     +------------+------------+------------+
 *     | Dev. 0 & 4 | Dev. 2 & 6 | Dev. 0 & 4 |
 *     +------------+------------+------------+
 *     | Dev. 1 & 5 | Dev. 3 & 7 | Dev. 1 & 5 |
 *     +------------+------------+------------+
 *     | Dev. 0 & 4 | Dev. 2 & 6 | Dev. 0 & 4 |
 *     +------------+------------+------------+
 *     | Dev. 1 & 5 | Dev. 3 & 7 | Dev. 1 & 5 |
 *     +------------+------------+------------+
 *     | Dev. 0 & 4 | Dev. 2 & 6 | Dev. 0 & 4 |
 *     +------------+------------+------------+
 *     \endverbatim
 *
 * \param[in] handle The library handle.
 * \param[out] desc The resulting tensor descriptor.
 * \param[in] numModes The number of modes.
 * \param[in] extent The extent of the tensor in each mode (array of size `numModes`).
 * \param[in] elementStride The offset (in linear memory) between two adjacent elements in each mode (array of size `numModes`), may be `NULL` for a dense tensor.
 * \param[in] blockSize The size of a block in each mode (array of size `numModes`), may be `NULL` for an unblocked tensor (i.e., each mode only has a single block that is equal to its extent).
 * \param[in] blockStride The offset (in linear memory) between two adjacent blocks in each mode (array of size `numModes`), may be `NULL` for a dense block-interleaved layout.
 * \param[in] deviceCount The number of devices that each mode is distributed across in a block-cyclic fashion (array of size `numModes`), may be `NULL` for a non-distributed tensor.
 * \param[in] numDevices The total number of devices that the tensor is distributed across  (i.e., the product of all elements in `deviceCount` times how many devices it is replicated across).
 * \param[in] devices The devices that the blocks are distributed across, in column-major order, i.e., stride 1 first (array of size `numDevices`).
 * \param[in] type The data type of the tensor.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED This layout or data type is not supported.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateTensorDescriptor(
    cutensorMgHandle_t handle,
    cutensorMgTensorDescriptor_t* desc,
    uint32_t numModes,
    const int64_t extent[],
    const int64_t elementStride[], // NULL -> dense
    const int64_t blockSize[], // NULL -> extent
    const int64_t blockStride[], // NULL -> elementStride
    const int32_t deviceCount[], // NULL -> 1
    uint32_t numDevices, const int32_t devices[],
    cudaDataType_t type
);

/**
 * \brief Destroy a tensor descriptor
 *
 * \param[in] desc The descriptor to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyTensorDescriptor(
    cutensorMgTensorDescriptor_t desc
);

/**
 * \brief Create a copy descriptor
 *
 * \details A copy descriptor encodes the source and the destination for a copy
 *     operation. The copy operation supports tensors on host, single, or multiple
 *     devices. It also supports layout changes and mode permutations.
 *     The only restriction is that the extents of the corresponding modes (in the input and output tensors) must match.
 *     
 *
 * \param[in] handle The library handle.
 * \param[out] desc The resulting copy descriptor.
 * \param[in] descDst The destination tensor descriptor.
 * \param[in] modesDst The destination tensor modes.
 * \param[in] descSrc The source tensor descriptor.
 * \param[in] modesSrc The source tensor modes.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED This tensor layout or precision combination is not supported.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateCopyDescriptor(
    const cutensorMgHandle_t handle,
    cutensorMgCopyDescriptor_t *desc,
    const cutensorMgTensorDescriptor_t descDst, const int32_t modesDst[],
    const cutensorMgTensorDescriptor_t descSrc, const int32_t modesSrc[]);

/**
 * \brief Destroy a copy descriptor and free all its previously-allocated resources.
 *
 * \param[in] desc The descriptor to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyCopyDescriptor(
    cutensorMgCopyDescriptor_t desc
);

/**
 * \brief Computes the workspace that is needed for the copy
 *
 * \details The function calculates the minimum workspace required for the 
 *     copy operation to succeed. It returns the device workspace size in
 *     the same order as the devices are passed to the library handle.
 *
 * \param[in] handle The library handle.
 * \param[in] desc The copy descriptor.
 * \param[out] deviceWorkspaceSize The workspace size in bytes, for each device in the handle.
 * \param[out] hostWorkspaceSize The workspace size in bytes for pinned host memory.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCopyGetWorkspace(
    const cutensorMgHandle_t handle,
    const cutensorMgCopyDescriptor_t desc,
    int64_t deviceWorkspaceSize[],
    int64_t* hostWorkspaceSize
);

/**
 * \brief Create a copy plan
 *
 * \details A copy plan implements the copy operation expressed through the
 *     copy descriptor. It contains all the information needed to execute
 *     a copy operation. Planning may fail if insufficient workspace is provided.
 *
 * \param[in] handle The library handle.
 * \param[out] plan The resulting copy plan.
 * \param[in] desc The copy descriptor.
 * \param[in] deviceWorkspaceSize The amount of workspace that will be provided, for each device in the handle.
 * \param[in] hostWorkspaceSize The amount of pinned host workspace that will be provided.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateCopyPlan(
    const cutensorMgHandle_t handle,
    cutensorMgCopyPlan_t* plan,
    const cutensorMgCopyDescriptor_t desc,
    const int64_t deviceWorkspaceSize[],
    int64_t hostWorkspaceSize
);

/**
 * \brief Destroy a copy plan
 *
 * \details When called, all outstanding operations must be completed.
 *     Frees all associated resources.
 *
 * \param[in] plan The plan to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyCopyPlan(
    cutensorMgCopyPlan_t plan
);

/**
 * \brief Execute a copy operation
 *
 * \details Executes a copy operation according to the given plan. It receives
 *     the source and destination pointers in the order prescribed by the
 *     `devices` parameter of the respective tensor descriptor and the
 *     device workspace and streams in the order prescribed by the `devices` 
 *     parameter of the handle. If host transfers are involved in the execution
 *     the function will block until those host transfers have been completed.
 *     The function is thread safe as long as concurrent threads use different
 *     library handles.
 *
 * \param[in] handle The library handle.
 * \param[in] plan The copy plan.
 * \param[out] ptrDst The destination tensor pointers.
 * \param[in] ptrSrc The source tensor pointers.
 * \param[out] deviceWorkspace The device workspace.
 * \param[out] hostWorkspace The host pinned memory workspace.
 * \param[in] streams The execution streams.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_CUDA_ERROR An issue interacting with the CUDA runtime occurred.
 *
 * \remarks calls asynchronous functions, conditionally blocking, no reentrant, and conditionally thread-safe
 */
cutensorStatus_t
cutensorMgCopy(
    const cutensorMgHandle_t handle,
    const cutensorMgCopyPlan_t plan,
    void* ptrDst[], // order from dst descriptor
    const void* ptrSrc[], // order from source descriptor
    void* deviceWorkspace[], // order from handle
    void* hostWorkspace,
    cudaStream_t streams[] // order from handle
);

/**
 * \brief Create a contraction find
 *
 * \details The contraction find contains all the algorithmic options to execute
 *     a tensor contraction. For now, its only parameter is an algorithm, which
 *     currently only has one default value. It may gain additional options in
 *     the future.
 *
 * \param[in] handle The library handle.
 * \param[out] find The resulting find.
 * \param[in] algo The desired algorithm.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateContractionFind(
    const cutensorMgHandle_t handle,
    cutensorMgContractionFind_t* find,
    const cutensorMgAlgo_t algo
);

/**
 * \brief Destroy a contraction find
 *
 * \param[in] find The find to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyContractionFind(
    cutensorMgContractionFind_t find
);

/**
 * \brief Set a contraction find attribute
 *
 * \param[in] handle The library handle.
 * \param[in,out] find The contraction find.
 * \param[in] attr The attribute to be set.
 * \param[in] value The value to set the attribute to.
 * \param[in] size The size of the value in bytes.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgContractionFindSetAttribute(
    const cutensorMgHandle_t handle,
    cutensorMgContractionFind_t find,
    cutensorMgContractionFindAttribute_t attr,
    const void* value,
    int64_t size
);

/**
 * \brief Create a contraction descriptor
 *
 * \details A contraction descriptor encodes the operands for a contraction
 *     operation of the form \f[ D = \alpha \mathcal{A}  \mathcal{B} + \beta \mathcal{C} \f]. 
 *     The contraction operation presently supports tensors that are either on
 *     one or multiple devices, but does not support tensors stored on the host
 *     (for now). It uses the einstein notation, i.e., modes shared between only modesA
 *     and modesB are contracted. Currently, descC and descD as well as modesC
 *     and modesD must be identical. The compute type represents the lowest precision
 *     that may be used in the course of the calculation.
 *
 * \param[in] handle The library handle.
 * \param[out] desc The resulting tensor contraction descriptor.
 * \param[in] descA The tensor descriptor for operand A.
 * \param[in] modesA The modes for operand A.
 * \param[in] descB The tensor descriptor for operand B.
 * \param[in] modesB The modes for operand B.
 * \param[in] descC The tensor descriptor for operand C.
 * \param[in] modesC The modes for operand C.
 * \param[in] descD The tensor descriptor for operand D.
 * \param[in] modesD The modes for operand D.
 * \param[in] compute The compute type for the operation.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED This tensor layout or precision combination is not supported.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateContractionDescriptor(
    const cutensorMgHandle_t handle,
    cutensorMgContractionDescriptor_t* desc,
    const cutensorMgTensorDescriptor_t descA, const int32_t modesA[],
    const cutensorMgTensorDescriptor_t descB, const int32_t modesB[],
    const cutensorMgTensorDescriptor_t descC, const int32_t modesC[],
    const cutensorMgTensorDescriptor_t descD, const int32_t modesD[],
    cutensorComputeType_t compute);

/**
 * \brief Destroy a contraction descriptor
 *
 * \param[in] desc The descriptor to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyContractionDescriptor(
    cutensorMgContractionDescriptor_t desc
);

/**
 * \brief Computes the workspace that is needed for the contraction
 *
 * \details The function calculates the workspace required for the 
 *     contraction operation to succeed. It takes a workspace preference, which can tune
 *     how much workspace is needed. It returns the device workspace size in
 *     the same order as the devices are passed to the library handle.
 *
 * \param[in] handle The library handle.
 * \param[in] desc The contraction descriptor.
 * \param[in] find The contraction find.
 * \param[in] preference The workspace preference.
 * \param[out] deviceWorkspaceSize The amount of workspace in bytes, for each device in the handle.
 * \param[out] hostWorkspaceSize The amount of pinned host memory in bytes.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED This tensor layout or precision combination is not supported.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgContractionGetWorkspace(
    const cutensorMgHandle_t handle,
    const cutensorMgContractionDescriptor_t desc,
    const cutensorMgContractionFind_t find,
    cutensorWorksizePreference_t preference,
    int64_t deviceWorkspaceSize[],
    int64_t* hostWorkspaceSize
);

/**
 * \brief Create a contraction plan
 *
 * \details A contraction plan implements the contraction operation expressed 
 *     through the contraction descriptor in accordance to the options specified
 *     in the contraction find. It contains all the information needed to execute
 *     a contraction operation. Planning may fail if insufficient workspace is
 *     provided.
 *
 * \param[in] handle The library handle.
 * \param[out] plan The resulting contraction plan.
 * \param[in] desc The contraction descriptor.
 * \param[in] find The contraction find.
 * \param[in] deviceWorkspaceSize The amount of workspace in bytes, for each device in the handle.
 * \param[in] hostWorkspaceSize The amount of pinned host memory in bytes.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_NOT_SUPPORTED This tensor layout or precision combination is not supported.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgCreateContractionPlan(
    const cutensorMgHandle_t handle,
    cutensorMgContractionPlan_t* plan,
    const cutensorMgContractionDescriptor_t desc,
    const cutensorMgContractionFind_t find,
    const int64_t deviceWorkspaceSize[],
    int64_t hostWorkspaceSize
);

/**
 * \brief Destroy a contraction plan
 *
 * \details When called, all outstanding operations must be completed.
 *     Frees all associated resources.
 *
 * \param[in] plan The plan to be destroyed.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 *
 * \remarks non-blocking, no reentrant, and thread-safe
 */
cutensorStatus_t
cutensorMgDestroyContractionPlan(
    cutensorMgContractionPlan_t plan
);

/**
 * \brief Execute a contraction operation
 *
 * \details Executes a contraction operation according to the provided plan. It
 *     receives all the operands as arrays of pointers that are ordered according
 *     to their tensor descriptors' `devices` parameter. The device workspace
 *     and streams are ordered according to the library handle's `devices`
 *     parameter. The function is thread safe as long as concurrent threads use
 *     different library handles.
 *
 * \param[in] handle The library handle.
 * \param[in] plan The copy plan.
 * \param[in] alpha The alpha scaling factor (host pointer).
 * \param[in] ptrA The A operand tensor pointers.
 * \param[in] ptrB The B operand tensor pointers.
 * \param[in] beta The beta scaling factor (host pointer).
 * \param[in] ptrC The operand C tensor pointers.
 * \param[out] ptrD The operand D tensor pointers.
 * \param[out] deviceWorkspace The device workspace.
 * \param[out] hostWorkspace The host pinned memory workspace.
 * \param[in] streams The execution streams.
 *
 * \returns A status code indicating the success or failure of the operation
 * \retval CUTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval CUTENSOR_STATUS_INVALID_VALUE Some input parameters were invalid.
 * \retval CUTENSOR_STATUS_CUDA_ERROR An issue interacting with the CUDA runtime occurred.
 *
 * \remarks calls asynchronous functions, non-blocking, no reentrant, and conditionally thread-safe
 */
cutensorStatus_t
cutensorMgContraction(
    const cutensorMgHandle_t handle,
    const cutensorMgContractionPlan_t plan,
    const void* alpha,
    const void* ptrA[],
    const void* ptrB[],
    const void* beta,
    const void* ptrC[],
    void* ptrD[],
    void* deviceWorkspace[], void* hostWorkspace,
    cudaStream_t streams[]
);

#if defined(__cplusplus)
}
#endif /* __cplusplus */
