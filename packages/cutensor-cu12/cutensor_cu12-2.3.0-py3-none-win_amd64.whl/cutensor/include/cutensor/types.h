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
 * @brief This file defines the types provided by the cuTENSOR library.
 */
#pragma once

#if defined(__CUDACC_RTC__)
#include <cstdint>
#else
#include <stdint.h>
#endif



typedef cudaDataType_t cutensorDataType_t;
const cutensorDataType_t CUTENSOR_R_16F  = CUDA_R_16F ; ///< real as a half
const cutensorDataType_t CUTENSOR_C_16F  = CUDA_C_16F ; ///< complex as a pair of half numbers
const cutensorDataType_t CUTENSOR_R_16BF = CUDA_R_16BF; ///< real as a nv_bfloat16
const cutensorDataType_t CUTENSOR_C_16BF = CUDA_C_16BF; ///< complex as a pair of nv_bfloat16 numbers
const cutensorDataType_t CUTENSOR_R_32F  = CUDA_R_32F ; ///< real as a float
const cutensorDataType_t CUTENSOR_C_32F  = CUDA_C_32F ; ///< complex as a pair of float numbers
const cutensorDataType_t CUTENSOR_R_64F  = CUDA_R_64F ; ///< real as a double
const cutensorDataType_t CUTENSOR_C_64F  = CUDA_C_64F ; ///< complex as a pair of double numbers
const cutensorDataType_t CUTENSOR_R_4I   = CUDA_R_4I  ; ///< real as a signed 4-bit int
const cutensorDataType_t CUTENSOR_C_4I   = CUDA_C_4I  ; ///< complex as a pair of signed 4-bit int numbers
const cutensorDataType_t CUTENSOR_R_4U   = CUDA_R_4U  ; ///< real as a unsigned 4-bit int
const cutensorDataType_t CUTENSOR_C_4U   = CUDA_C_4U  ; ///< complex as a pair of unsigned 4-bit int numbers
const cutensorDataType_t CUTENSOR_R_8I   = CUDA_R_8I  ; ///< real as a signed 8-bit int
const cutensorDataType_t CUTENSOR_C_8I   = CUDA_C_8I  ; ///< complex as a pair of signed 8-bit int numbers
const cutensorDataType_t CUTENSOR_R_8U   = CUDA_R_8U  ; ///< real as a unsigned 8-bit int
const cutensorDataType_t CUTENSOR_C_8U   = CUDA_C_8U  ; ///< complex as a pair of unsigned 8-bit int numbers
const cutensorDataType_t CUTENSOR_R_16I  = CUDA_R_16I ; ///< real as a signed 16-bit int
const cutensorDataType_t CUTENSOR_C_16I  = CUDA_C_16I ; ///< complex as a pair of signed 16-bit int numbers
const cutensorDataType_t CUTENSOR_R_16U  = CUDA_R_16U ; ///< real as a unsigned 16-bit int
const cutensorDataType_t CUTENSOR_C_16U  = CUDA_C_16U ; ///< complex as a pair of unsigned 16-bit int numbers
const cutensorDataType_t CUTENSOR_R_32I  = CUDA_R_32I ; ///< real as a signed 32-bit int
const cutensorDataType_t CUTENSOR_C_32I  = CUDA_C_32I ; ///< complex as a pair of signed 32-bit int numbers
const cutensorDataType_t CUTENSOR_R_32U  = CUDA_R_32U ; ///< real as a unsigned 32-bit int
const cutensorDataType_t CUTENSOR_C_32U  = CUDA_C_32U ; ///< complex as a pair of unsigned 32-bit int numbers
const cutensorDataType_t CUTENSOR_R_64I  = CUDA_R_64I ; ///< real as a signed 64-bit int
const cutensorDataType_t CUTENSOR_C_64I  = CUDA_C_64I ; ///< complex as a pair of signed 64-bit int numbers
const cutensorDataType_t CUTENSOR_R_64U  = CUDA_R_64U ; ///< real as a unsigned 64-bit int
const cutensorDataType_t CUTENSOR_C_64U  = CUDA_C_64U ; ///< complex as a pair of unsigned 64-bit int numbers

/**
 * \brief This enum captures all unary and binary element-wise operations supported by the cuTENSOR library.
 */
typedef enum 
{
    /* Unary */
    CUTENSOR_OP_IDENTITY = 1,  ///< Identity operator (i.e., elements are not changed)
    CUTENSOR_OP_SQRT = 2,      ///< Square root
    CUTENSOR_OP_RELU = 8,      ///< Rectified linear unit
    CUTENSOR_OP_CONJ = 9,      ///< Complex conjugate
    CUTENSOR_OP_RCP = 10,      ///< Reciprocal
    CUTENSOR_OP_SIGMOID = 11,  ///< y=1/(1+exp(-x))
    CUTENSOR_OP_TANH = 12,     ///< y=tanh(x)
    CUTENSOR_OP_EXP = 22,      ///< Exponentiation.
    CUTENSOR_OP_LOG = 23,      ///< Log (base e).
    CUTENSOR_OP_ABS = 24,      ///< Absolute value.
    CUTENSOR_OP_NEG = 25,      ///< Negation.
    CUTENSOR_OP_SIN = 26,      ///< Sine.
    CUTENSOR_OP_COS = 27,      ///< Cosine.
    CUTENSOR_OP_TAN = 28,      ///< Tangent.
    CUTENSOR_OP_SINH = 29,     ///< Hyperbolic sine.
    CUTENSOR_OP_COSH = 30,     ///< Hyperbolic cosine.
    CUTENSOR_OP_ASIN = 31,     ///< Inverse sine.
    CUTENSOR_OP_ACOS = 32,     ///< Inverse cosine.
    CUTENSOR_OP_ATAN = 33,     ///< Inverse tangent.
    CUTENSOR_OP_ASINH = 34,    ///< Inverse hyperbolic sine.
    CUTENSOR_OP_ACOSH = 35,    ///< Inverse hyperbolic cosine.
    CUTENSOR_OP_ATANH = 36,    ///< Inverse hyperbolic tangent.
    CUTENSOR_OP_CEIL = 37,     ///< Ceiling.
    CUTENSOR_OP_FLOOR = 38,    ///< Floor.
    CUTENSOR_OP_MISH = 39,     ///< Mish y=x*tanh(softplus(x)).
    CUTENSOR_OP_SWISH = 40,    ///< Swish y=x*sigmoid(x).
    CUTENSOR_OP_SOFT_PLUS = 41, ///< Softplus y=log(exp(x)+1).
    CUTENSOR_OP_SOFT_SIGN = 42, ///< Softsign y=x/(abs(x)+1).
    /* Binary */
    CUTENSOR_OP_ADD = 3,       ///< Addition of two elements
    CUTENSOR_OP_MUL = 5,       ///< Multiplication of two elements
    CUTENSOR_OP_MAX = 6,       ///< Maximum of two elements
    CUTENSOR_OP_MIN = 7,       ///< Minimum of two elements

    CUTENSOR_OP_UNKNOWN = 126, ///< reserved for internal use only

} cutensorOperator_t;

/**
 * \brief cuTENSOR status type returns
 *
 * \details The type is used for function status returns. All cuTENSOR library functions return their status, which can have the following values.
 */
typedef enum 
{
    /** The operation completed successfully.*/
    CUTENSOR_STATUS_SUCCESS                = 0,
    /** The opaque data structure was not initialized.*/
    CUTENSOR_STATUS_NOT_INITIALIZED        = 1,
    /** Resource allocation failed inside the cuTENSOR library.*/
    CUTENSOR_STATUS_ALLOC_FAILED           = 3,
    /** An unsupported value or parameter was passed to the function (indicates an user error).*/
    CUTENSOR_STATUS_INVALID_VALUE          = 7,
    /** Indicates that the device is either not ready, or the target architecture is not supported.*/
    CUTENSOR_STATUS_ARCH_MISMATCH          = 8,
    /** An access to GPU memory space failed, which is usually caused by a failure to bind a texture.*/
    CUTENSOR_STATUS_MAPPING_ERROR          = 11,
    /** The GPU program failed to execute. This is often caused by a launch failure of the kernel on the GPU, which can be caused by multiple reasons.*/
    CUTENSOR_STATUS_EXECUTION_FAILED       = 13,
    /** An internal cuTENSOR error has occurred.*/
    CUTENSOR_STATUS_INTERNAL_ERROR         = 14,
    /** The requested operation is not supported.*/
    CUTENSOR_STATUS_NOT_SUPPORTED          = 15,
    /** The functionality requested requires some license and an error was detected when trying to check the current licensing.*/
    CUTENSOR_STATUS_LICENSE_ERROR          = 16,
    /** A call to CUBLAS did not succeed.*/
    CUTENSOR_STATUS_CUBLAS_ERROR           = 17,
    /** Some unknown CUDA error has occurred.*/
    CUTENSOR_STATUS_CUDA_ERROR             = 18,
    /** The provided workspace was insufficient.*/
    CUTENSOR_STATUS_INSUFFICIENT_WORKSPACE = 19,
    /** Indicates that the driver version is insufficient.*/
    CUTENSOR_STATUS_INSUFFICIENT_DRIVER    = 20,
    /** Indicates an error related to file I/O.*/
    CUTENSOR_STATUS_IO_ERROR               = 21,
} cutensorStatus_t;

/**
 * \brief Allows users to specify the algorithm to be used for performing the desired
 * tensor operation.
 */
typedef enum
{
    CUTENSOR_ALGO_DEFAULT_PATIENT   = -6, ///< More time-consuming than CUTENSOR_DEFAULT, but typically provides a more accurate kernel selection
    CUTENSOR_ALGO_GETT              = -4, ///< Choose the GETT algorithm (only applicable to contractions)
    CUTENSOR_ALGO_TGETT             = -3, ///< Transpose (A or B) + GETT (only applicable to contractions)
    CUTENSOR_ALGO_TTGT              = -2, ///< Transpose-Transpose-GEMM-Transpose (requires additional memory) (only applicable to contractions)
    CUTENSOR_ALGO_DEFAULT           = -1, ///< A performance model chooses the appropriate algorithm and kernel
} cutensorAlgo_t;

/**
 * \brief This enum gives users finer control over the suggested workspace
 *
 * \details This enum gives users finer control over the amount of workspace that is
 * suggested by \ref cutensorEstimateWorkspaceSize
 */
typedef enum
{
    CUTENSOR_WORKSPACE_MIN = 1,     ///< Least memory requirement; at least one algorithm will be available
    CUTENSOR_WORKSPACE_DEFAULT = 2, ///< Aims to attain high performance while also reducing the workspace requirement.
    CUTENSOR_WORKSPACE_MAX = 3,     ///< Highest memory requirement; all algorithms will be available (choose this option if memory footprint is not a concern)
} cutensorWorksizePreference_t;

/**
 * \brief Opaque structure representing a compute descriptor.
 */
typedef struct cutensorComputeDescriptor *cutensorComputeDescriptor_t;

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */
#ifndef CUTENSOR_EXTERN
#  ifdef _MSC_VER
#    define CUTENSOR_EXTERN __declspec(dllimport) extern
#  else
#    define CUTENSOR_EXTERN extern
#  endif
#endif
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_16F;   ///< floating-point: 5-bit exponent and 10-bit mantissa (aka half)
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_16BF;  ///< floating-point: 8-bit exponent and 7-bit mantissa (aka bfloat)
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_TF32;  ///< floating-point: 8-bit exponent and 10-bit mantissa (aka tensor-float-32)
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_3XTF32;///< floating-point: More precise than TF32, but less precise than float
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_32F;   ///< floating-point: 8-bit exponent and 23-bit mantissa (aka float)
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_64F;   ///< floating-point: 11-bit exponent and 52-bit mantissa (aka double)
CUTENSOR_EXTERN const cutensorComputeDescriptor_t CUTENSOR_COMPUTE_DESC_9X16BF; ///< floating-point composed of 3xbf16 for a total of 23 mantissa bits.

#if defined(__cplusplus)
}
#endif /* __cplusplus */
/**
 * This enum lists all attributes of a \ref cutensorOperationDescriptor_t that can be modified (see \ref cutensorOperationDescriptorSetAttribute and \ref cutensorOperationDescriptorGetAttribute).
 */
typedef enum
{
    CUTENSOR_OPERATION_DESCRIPTOR_TAG = 0,                  ///< int32_t: enables users to distinguish two identical problems w.r.t. the sw-managed plan-cache. (default value: 0)
    CUTENSOR_OPERATION_DESCRIPTOR_SCALAR_TYPE = 1,                     ///< cudaDataType_t: data type of the scaling factors
    CUTENSOR_OPERATION_DESCRIPTOR_FLOPS = 2,                ///< float: number of floating-point operations necessary to perform this operation (assuming all scalar are not equal to zero, unless otherwise specified)
    CUTENSOR_OPERATION_DESCRIPTOR_MOVED_BYTES = 3,          ///< float: minimal number of bytes transferred from/to global-memory  (assuming all scalar are not equal to zero, unless otherwise specified)
    CUTENSOR_OPERATION_DESCRIPTOR_PADDING_LEFT = 4,         ///< uint32_t[] (of size descOut->numModes): Each entry i holds the number of padded values that should be padded to the left of the ith dimension
    CUTENSOR_OPERATION_DESCRIPTOR_PADDING_RIGHT = 5,        ///< uint32_t[] (of size descOut->numModes): Each entry i holds the number of padded values that should be padded to the right of the ith dimension
    CUTENSOR_OPERATION_DESCRIPTOR_PADDING_VALUE = 6,        ///< host-side pointer to element of the same type as the output tensor: Constant padding value
} cutensorOperationDescriptorAttribute_t;

/**
 * This enum lists all attributes of a \ref cutensorPlanPreference_t object that can be modified.
 */
typedef enum
{
    CUTENSOR_PLAN_PREFERENCE_AUTOTUNE_MODE = 0,    ///< cutensorAutotuneMode_t: Determines if recurrent executions of the plan (e.g., via cutensorContract, cutensorPermute) should autotune (i.e., try different kernels); see section "Plan Cache" for details.
    CUTENSOR_PLAN_PREFERENCE_CACHE_MODE = 1,       ///< cutensorCacheMode_t: Determines if the corresponding algorithm/kernel for this plan should be cached and it gives fine control over what is considered a cachehit.
    CUTENSOR_PLAN_PREFERENCE_INCREMENTAL_COUNT = 2,///< int32_t: Only applicable if CUTENSOR_PLAN_PREFERENCE_CACHE_MODE is set to CUTENSOR_AUTOTUNE_MODE_INCREMENTAL
    CUTENSOR_PLAN_PREFERENCE_ALGO = 3,             ///< cutensorAlgo_t: Fixes a certain \ref cutensorAlgo_t
    CUTENSOR_PLAN_PREFERENCE_KERNEL_RANK = 4,      ///< int32_t: Fixes a kernel (a sub variant of an algo; e.g., kernel_rank==1 while algo == CUTENSOR_ALGO_TGETT would select the second-best GETT kernel/variant according to cuTENSOR's performance model; kernel_rank==2 would select the third-best)
    CUTENSOR_PLAN_PREFERENCE_JIT = 5,              ///< cutensorJitMode_t: determines if just-in-time compilation is enabled or disabled (default: CUTENSOR_JIT_MODE_NONE)
} cutensorPlanPreferenceAttribute_t;

/**
 * This enum determines the mode w.r.t. cuTENSOR's auto-tuning capability.
 */
typedef enum
{
    CUTENSOR_AUTOTUNE_MODE_NONE = 0,        ///< Indicates no autotuning (default); in this case the cache will help to reduce the plan-creation overhead. In the case of a cachehit: the cached plan will be reused, otherwise the plancache will be neglected.
    CUTENSOR_AUTOTUNE_MODE_INCREMENTAL = 1, ///< Indicates an incremental autotuning (i.e., each invocation of corresponding cutensorCreatePlan() will create a plan based on a different algorithm/kernel; the maximum number of kernels that will be tested is defined by the CUTENSOR_PLAN_PREFERENCE_INCREMENTAL_COUNT of \ref cutensorPlanPreferenceAttribute_t). WARNING: If this autotuning mode is selected, then we cannot guarantee bit-wise identical results (since different algorithms could be executed).
} cutensorAutotuneMode_t;

/**
 * This enum determines the mode w.r.t. cuTENSOR's just-in-time compilation capability.
 */
typedef enum
{
    CUTENSOR_JIT_MODE_NONE = 0,    ///< Indicates that no kernel will be just-in-time compiled.
    CUTENSOR_JIT_MODE_DEFAULT = 1, ///< Indicates that the corresponding plan will try to compile a dedicated kernel for the given operation. Only supported for GPUs with compute capability >= 8.0 (Ampere or newer).
} cutensorJitMode_t;

/**
 * This enum defines what is considered a cache hit.
 */
typedef enum
{
    CUTENSOR_CACHE_MODE_NONE = 0,     ///< Plan will not be cached
    CUTENSOR_CACHE_MODE_PEDANTIC = 1, ///< All parameters of the corresponding descriptor must be identical to the cached plan (default).
} cutensorCacheMode_t;

/**
 * This enum lists all attributes of a \ref cutensorPlan_t object that can be retrieved via \ref cutensorPlanGetAttribute.
 *
 */
typedef enum
{
    CUTENSOR_PLAN_REQUIRED_WORKSPACE = 0, ///< uint64_t: exact required workspace in bytes that is needed to execute the plan
} cutensorPlanAttribute_t;

/**
 * \brief Opaque structure representing any type of problem descriptor (e.g., contraction, reduction, elementwise).
 */
typedef struct cutensorOperationDescriptor *cutensorOperationDescriptor_t;

/**
 * \brief Opaque structure representing a plan (e.g, contraction, reduction, elementwise).
 */
typedef struct cutensorPlan *cutensorPlan_t;

/**
 * \brief Opaque structure that narrows down the space of applicable
 * algorithms/variants/kernels.
 */
typedef struct cutensorPlanPreference *cutensorPlanPreference_t;

/**
 * \brief Opaque structure holding cuTENSOR's library context.
 */
typedef struct cutensorHandle *cutensorHandle_t;

/**
 * \brief Opaque structure representing a tensor descriptor.
 */
typedef struct cutensorTensorDescriptor *cutensorTensorDescriptor_t;

/**
 * \brief Opaque structure representing a block-sparse tensor descriptor.
 */
typedef struct cutensorBlockSparseTensorDescriptor    *cutensorBlockSparseTensorDescriptor_t;

/**
 * \brief A function pointer type for logging.
 */
typedef void (*cutensorLoggerCallback_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message
);
