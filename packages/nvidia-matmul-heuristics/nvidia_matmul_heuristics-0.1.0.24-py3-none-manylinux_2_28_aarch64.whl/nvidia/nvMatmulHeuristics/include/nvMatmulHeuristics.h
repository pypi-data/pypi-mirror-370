/*
* Copyright 2025 NVIDIA Corporation. All rights reserved.
*
* NOTICE TO LICENSEE:
*
* This source code and/or documentation ("Licensed Deliverables") are
* subject to NVIDIA intellectual property rights under U.S. and
* international Copyright laws.
*
* These Licensed Deliverables contained herein is PROPRIETARY and
* CONFIDENTIAL to NVIDIA and is being provided under the terms and
* conditions of a form of NVIDIA software license agreement by and
* between NVIDIA and Licensee ("License Agreement") or electronically
* accepted by Licensee.  Notwithstanding any terms or conditions to
* the contrary in the License Agreement, reproduction or disclosure
* of the Licensed Deliverables to any third party without the express
* written consent of NVIDIA is prohibited.
*
* NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
* LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
* SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
* PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
* NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
* DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
* NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
* NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
* LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
* SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
* DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
* WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
* ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
* OF THESE LICENSED DELIVERABLES.
*
* U.S. Government End Users.  These Licensed Deliverables are a
* "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
* 1995), consisting of "commercial computer software" and "commercial
* computer software documentation" as such terms are used in 48
* C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
* only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
* 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
* U.S. Government End Users acquire the Licensed Deliverables with
* only those rights set forth herein.
*
* Any use of the Licensed Deliverables in individual and commercial
* software must include, in the user documentation and internal
* comments to the code, the above Disclaimer and U.S. Government End
* Users Notice.
*/

/** @file 
 * nvMatmulHeuristics public API
 **/

#pragma once

#ifdef __cplusplus
#    include <cstdint>
#else
#    include <stdint.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif


#define NVMMH_VERSION_MAJOR 0 /**< Library major version */
#define NVMMH_VERSION_MINOR 1 /**< Library minor version */
#define NVMMH_VERSION_PATCH 0 /**< Library patch version */

/*
 * Macros for improved diagnostics when using clang.
 */
#ifdef __clang__
/** Denotes that the argument CAN be NULL */
#    ifndef NVMMH_NULLABLE
#        define NVMMH_NULLABLE _Nullable
#    endif
/** Denotes that the argument should NEVER be NULL */
#    ifndef NVMMH_NONNULL
#        define NVMMH_NONNULL _Nonnull
#    endif
#else
/** Denotes that the argument CAN be NULL */
#    ifndef NVMMH_NULLABLE
#        define NVMMH_NULLABLE
#    endif
/** Denotes that the argument should NEVER be NULL */
#    ifndef NVMMH_NONNULL
#        define NVMMH_NONNULL
#    endif
#endif

#ifndef _WIN32
/** Denotes that the argument CAN be unused */
#    define NVMMH_MAYBE_UNUSED __attribute__((unused))
#else
#    define NVMMH_MAYBE_UNUSED
#endif

/** Denotes that the argument should NOT be ignored */
#if defined(__cplusplus)
#    if __has_cpp_attribute(nodiscard)
#        define NVMMH_NODISCARD [[nodiscard]]
#    else
#        define NVMMH_NODISCARD
#    endif
#else
#    define NVMMH_NODISCARD
#endif

/** On Windows, indicates the function follows the __stdcall calling convention */
#ifndef NVMMH_WINAPI
#    ifdef _WIN32
#        define NVMMH_WINAPI __stdcall
#    else
#        define NVMMH_WINAPI
#    endif
#endif


/**
 * Return status
 */
typedef enum {
    NVMMH_STATUS_ERROR = 0,                             /**< Error */
    NVMMH_STATUS_SUCCESS = 1,                           /**< Success */
    NVMMH_STATUS_PROFILE_NOT_ENTIRELY_LOADED = 2,       /**< Everything is in order besides that some or all of the internal profile data was missing. */
    NVMMH_STATUS_INVALID_INPUT = 3,                     /**< Invalid input passed into the function */
    NVMMH_STATUS_INVALID_ENUM_INPUT = 4,                /**< Invalid enum input passed into the function */
    NVMMH_STATUS_INVALID_DESCRIPTOR = 5,                /**< Invalid descriptor used. */
    NVMMH_STATUS_DRIVER_ALREADY_INITIALIZED = 6,        /**< CUDA Driver was already loaded by nvMatmulHeuristics */
    NVMMH_STATUS_UNSUPPORTED_FEATURE = 7,               /**< Attempt to use something that is not supported */
    NVMMH_STATUS_MISSING_RUNTIME_DISCOVERY_PROFILE = 8, /**< The operation requires runtime discovery to be present, but turns out it's not */
    NVMMH_STATUS_EXECUTION_FAILED = 9,                  /**< nvMatmulHeuristics cannot accept the current inputs for some reason */
    NVMMH_STATUS_BUFFER_TOO_SMALL = 10,                 /**< Some buffer is too small */
    NVMMH_STATUS_INVALID_HANDLE = 11,                   /**< Input handle is invalid */
    NVMMH_STATUS_END = 12,                              /**< End */
} nvmmhStatus_t;

/**
 * An opaque handle to a nvMatmulHeuristics instance.
 */
typedef void* nvmmhHandle_t;


/**
 * Create a new nvMatmulHeuristics thread-safe handle. 
 * Handles created using this API must be destroyed using @ref nvMatmulHeuristicsDestroy.
 * Multiple host threads may manipulate a given handle through various API calls without explicit synchronization, except for 
 * @ref nvMatmulHeuristicsDestroy.
 *
 * @param handle A pointer to a handle.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsCreate(NVMMH_NONNULL nvmmhHandle_t* NVMMH_NONNULL handle);


/**
 * Destroys a handle created using @ref nvMatmulHeuristicsCreate. 
 * A single host thread must be be calling this API for a given `handle`.
 *
 * @param handle A pointer to the handle to destroy.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsDestroy(NVMMH_NONNULL nvmmhHandle_t* NVMMH_NONNULL handle);


/**
 * Returns a pointer to a null-terminated string constant describing the status.
 * @param status The status to describe.
 * @return A pointer to a constant null-terminated string. The string should not be freed by the caller.
 */
NVMMH_NODISCARD const char* NVMMH_WINAPI NVMMH_NONNULL nvMatmulHeuristicsGetStatusString(const nvmmhStatus_t status);

/**
 * Returns the last error log for the current handle. Writes up to bufferSize bytes including the NULL terminator. 
 * If buffer == NULL and bufferSize == 0, then the required buffer size is returned.
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param buffer output buffer.
 * @param bufferSize output buffer size.
 * @return bytes written or required buffer size including NULL terminator.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetLastErrorLog(NVMMH_NULLABLE nvmmhHandle_t handle, char* NVMMH_NULLABLE buffer, unsigned bufferSize);

/**
 * @brief Dependency configuration.
 * Describes the state of a potential nvMatmulHeuristics dependency. It also allows to detect enabled features. 
 * For example this allows to know if nvMatmulHeuristics was built with CUDA support. 
 */
typedef enum {
    NVMMH_DEP_NONE = 0,         /**< The dependency is absent and not required */
    NVMMH_DEP_STATIC_LINK = 1,  /**< The dependency is statically linked into the shared library. */
    NVMMH_DEP_DYNAMIC_LINK = 2, /**< The dependency is dynamically linked (i.e. shared library) with the library. */
    NVMMH_DEP_RUNTIME_LOAD = 3, /**< The dependency loaded at runtime. */
} nvmmhDependencyConfiguration_t;


/**
 * Returns the shared library version major
 * @return Version major.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetVersionMajor();

/**
 * Returns the shared library version minor
 * @return Version minor.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetVersionMinor();


/**
 * Returns the shared library version patch.
 * @return Version patch.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetVersionPatch();

/**
 * Returns build and runtime info.
 * @param hasCUDA indicates if nvMatmulHeuristics was built to support CUDA, if so, it indicates how nvMatmulHeuristics uses libcuda.so: either dynamic linking or runtime loading
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsGetDependencyConfiguration(nvmmhDependencyConfiguration_t* NVMMH_NULLABLE hasCUDA);

/**
 * Allows to specify the path to NVIDIA CUDA Driver libcuda.so/nvcuda.dll that nvMatmulHeuristics will use.
 * 
 * nvMatmulHeuristics looks for the driver in the following order:
 * 1 - Path explicitly set using this API
 * 2 - Path set using nvMatmulHeuristics_CUDA_PATH environment variable
 * 3 - Default system lookup (so LD_PRELOAD, LD_LIBRARY_PATH, ...)
 * 
 * Must be called before any other API call, or it will fail with NVMMH_STATUS_DRIVER_ALREADY_INITIALIZED
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param path The path to the CUDA drive `libcuda.so` or `nvcuda.dll`.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsSetCudaDriverPath(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NULLABLE path);

/**
 * Writes version string into a buffer. Write up to bufferSize bytes including the NULL terminator. 
 * If buffer == NULL and bufferSize == 0, then the required buffer size is returned.
 * @param buffer output buffer.
 * @param bufferSize output buffer size.
 * @return bytes written or required buffer size including NULL terminator.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetVersionString(char* NVMMH_NULLABLE buffer, unsigned bufferSize);

/**
 * Clears nvMatmulHeuristics internal caches and states.
 * This is not thread-safe and must be called by a single host thread.
* @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsClearInternalState();


/**
 * Defines the layout of the matmul.
 */
typedef enum {
    NVMMH_MATMUL_LAYOUT_NN_ROW_MAJOR = 0, /**< No transpose. Row Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_NT_ROW_MAJOR = 1, /**< Transposing B while loading. Row Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_TN_ROW_MAJOR = 2, /**< Transposing A while loading. Row Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_TT_ROW_MAJOR = 3, /**< Transposing A and B while loading. Row Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_NN_COL_MAJOR = 4, /**< No transpose. Col Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_NT_COL_MAJOR = 5, /**< Transposing B while loading. Col Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_TN_COL_MAJOR = 6, /**< Transposing A while loading. Col Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_TT_COL_MAJOR = 7, /**< Transposing A and B while loading. Col Major memory layouts. */
    NVMMH_MATMUL_LAYOUT_END = 8,          /**< End Marker */
} nvmmhMatmulLayout_t;


/**
 * Defines the beta mode, aka if beta is statically known to be 0, 1 or can take any value.
 */
typedef enum { LH_BETA_DEFAULT, LH_BETA_ZERO, LH_BETA_ONE, LH_BETA_ANY } nvmmhBetaMode_t;


/****************************************************************************************************************
 *                                                                                                              
 *                                          nvMatmulHeuristics Data Types                                            
 *                                                                                                                                                                         
 ****************************************************************************************************************/

/**
 * Describes a matmul problem
 */
typedef struct {
    uint32_t M;           /**< M: output matrix height */
    uint32_t N;           /**< N: output matrix width */
    uint32_t K;           /**< K: reduced dimension */
    uint32_t batchSize;   /**< Batch size */
    uint8_t matmulLayout; /**< Memory layout. @ref nvmmhMatmulLayout_t */
} nvmmhMatmulProblem_t;


/**
 * Holds the result of the matmul heuristic, aka the kernel configuration.
 */
typedef struct {
    uint16_t cta[3];     /**< CTA tile configuration. M, N and K. */
    uint16_t warp[3];    /**< Warp tile configuration. M, N and K. */
    uint16_t instr[3];   /**< Instruction tile configuration  (the MMA op). M, N and K. */
    uint16_t splitK;     /**< Split-k factor to be used. 1 means no split-k. */
    uint8_t loadStages;  /**< Number of memory load stages. 1 means no staging. 2 means that we have two buffers, and we alternate between them. */
    uint8_t gridSwizzle; /**< Grid/CTA swizzling factor used to increase L2 hit rate. Matches CUTLASS, nvFuser and Triton definition. */
    uint8_t ctaOrder;    /**< Rasterization order of the CTAs onto the CUDA Grid. 0=row major. 1=col major. Row major means that `TilesN` is mapped onto gridDim.x */
    uint8_t cluster[2];  /**< Thread block cluster configuration. Maps to clusterDim.x and clusterDim.y */
} nvmmhKernelConfiguration_t;


/****************************************************************************************************************
 *                                                                                                                                                                         
 *                                 nvMatmulHeuristics Hardware Descriptor                                                                      
 *                                                                                                                                                                         
 * nvmmhHardwareDescriptor_t allows the user to specify a target GPU configuration. The module provides
 * two ways to configure the hardware:
 * 
 * 1. Using predefined GPU configurations via nvMatmulHeuristicsHardwareDescriptorSetPredefinedGpu()
 * 2. Automatic hardware detection when passing nullptr to APIs that accept a hardware descriptor
 *                                                                                                                                                                         
****************************************************************************************************************/


/** 
 * @typedef nvmmhHardwareDescriptor_t
 * Opaque handle to the nvMatmulHeuristics hardware descriptor. 
 */
typedef struct nvmmhHardwareDescriptor* nvmmhHardwareDescriptor_t;

/**
 * Creates a hardware descriptor and allocates memory. Handles created using this API must be destroyed using @ref nvMatmulHeuristicsHardwareDescriptorDestroy.
 * @param descr Pointer to the descriptor to create.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsHardwareDescriptorCreate(nvmmhHardwareDescriptor_t NVMMH_NULLABLE* NVMMH_NONNULL descr);

/**
 * Destroys the descriptor and frees memory.
 * Handle is set to nullptr to prevent crash if API is called twice
 * @param descr Pointer to the descriptor to destroy. Set to NULL on output.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsHardwareDescriptorDestroy(nvmmhHardwareDescriptor_t NVMMH_NONNULL* NVMMH_NONNULL descr);

/**
 * @brief List of predefined supported NVIDIA GPUs.
 *
 * @warning The list of devices included in this enum is subject to change.
 * The library authors make no commitment to maintain this list in any specific shape or form.
 * 
 * For devices not listed here, it is strongly recommended to use the automatic hardware detection mode
 * (by passing nullptr to APIs that accept a hardware descriptor) which is the preferred way of using
 * the library. This mode provides better adaptability and future compatibility.
 * 
 * Even for listed devices, using automatic hardware detection is recommended as it ensures the hardware
 * descriptor exactly matches your specific GPU variant/SKU, which may differ from the base model in
 * terms of memory, clock speeds, or other characteristics that can affect performance.
 */
typedef enum {
    /* Ampere */
    NVMMH_NVGPU_A100_SXM_80GB = 8000,
    NVMMH_NVGPU_A100_PCIE_80GB = 8001,
    NVMMH_NVGPU_A30_PCIE = 8002,
    NVMMH_NVGPU_A10_PCIE = 8003,
    NVMMH_NVGPU_A40_PCIE = 8600,
    NVMMH_NVGPU_RTX_3090 = 8601,
    NVMMH_NVGPU_RTX_A6000 = 8602,

    /* Ada */
    NVMMH_NVGPU_L20 = 8900,
    NVMMH_NVGPU_L40 = 8901,
    NVMMH_NVGPU_L40S = 8902,
    NVMMH_NVGPU_L4 = 8903,
    NVMMH_NVGPU_RTX_4090 = 8904,
    NVMMH_NVGPU_RTX_6000_ADA = 8905,

    /* Hopper */
    NVMMH_NVGPU_H100_SXM = 9000,
    NVMMH_NVGPU_H100_PCIE = 9001,
    NVMMH_NVGPU_H100_NVL = 9002,
    NVMMH_NVGPU_H200_SXM = 9003,
    NVMMH_NVGPU_H20_SXM = 9004,

    /* Blackwell */

    NVMMH_NVGPU_B200 = 10000,
    NVMMH_NVGPU_GB200_NVL = 10001,
    NVMMH_NVGPU_GB300_NVL = 10300,
    NVMMH_NVGPU_RTX_5080 = 12000,
    NVMMH_NVGPU_RTX_5090 = 12001,
    NVMMH_NVGPU_RTX_PRO_6000 = 12002,

    NVMMH_NVGPU_END = 0xFFFFFFFF
} nvmmhNvidiaGpu_t;

/**
 * Sets the hardware descriptor to a predefined GPU configuration.
 * @param descr Descriptor to set.
 * @param gpu GPU to set the descriptor to.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsHardwareDescriptorSetPredefinedGpu(nvmmhHardwareDescriptor_t NVMMH_NONNULL descr, nvmmhNvidiaGpu_t gpu);


/****************************************************************************************************************
 * 
 *                                     nvMatmulHeuristics Backend definition                                                        
 *                                                                                                                                                                         
 * nvmmhBackend_t allows the user to customize the target kernel generator/backend that nvMatmulHeuristics 
 * is generating kernels for.                                   
 *                                                                                                                                                                        
 ****************************************************************************************************************/


/**
 * nvMatmulHeuristics matmul targets. 
 */
typedef enum {
    NVMMH_TARGET_GENERIC =
            0, /**< Targets some abstract gemm implementation. Returns a configuration, but there's no guarantee that there exists a backend that can implement this configuration */
    NVMMH_TARGET_NVFUSER = 1,    /**< Targets nvFuser */
    NVMMH_TARGET_CUTLASS = 2,    /**< Targets CUTLASS */
    NVMMH_TARGET_TRITON = 3,     /**< Targets Triton */
    NVMMH_TARGET_CUTLASS3 = 4,   /**< Targets CUTLASS3 */
    NVMMH_TARGET_RESERVED_1 = 5, /**< Reserved target */
    NVMMH_TARGET_RESERVED_2 = 6, /**< Reserved target */
    NVMMH_TARGET_END = 7,        /**< End Marker */
} nvmmhTarget_t;


/**
 * @struct nvmmhBackend
 * Opaque structure describing a matmul backend.
 */
struct nvmmhBackend;

/**
 * @typedef nvmmhBackend_t
 * Opaque handle describing a matmul backend.
 */
typedef struct nvmmhBackend* nvmmhBackend_t;


/**
 * @param backend Pointer to the backend handle to create. Must be destroyed using @ref nvMatmulHeuristicsBackendDestroy.
 * @param target @ref nvmmhTarget_t target to create the backend for.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendCreate(nvmmhBackend_t NVMMH_NULLABLE* NVMMH_NONNULL backend, nvmmhTarget_t target);

/**
 * Destroys the backend handle and frees associated memory. 
 * Sets the opaque pointer to NULL to prevent double free.
 * @param backend Pointer to the backend handle to destroy. Set to NULL on output.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendDestroy(nvmmhBackend_t NVMMH_NONNULL* NVMMH_NONNULL backend);


/**
 * Various K-dimension reduction methods.
 */
typedef enum {
    NVMMH_SPLIT_K_NONE,         /**< No support for parallelization on the reduced dimension */
    NVMMH_SPLIT_K_IN_PLACE,     /**< In-place split-k. */
    NVMMH_SPLIT_K_OUT_OF_PLACE, /**< Out-of-place split-k  */
    NVMMH_SPLIT_K_STREAM_K,     /**< Stream-k */
    NVMMH_SPLIT_K_SEGMENT_K,    /**< Segment-k */
    NVMMH_SPLIT_K_END,          /**< End Marker */
} nvmmhSplitKKind_t;


/**
 * Defines an internal swizzling method. These swizzlers will be overridden by @ref nvMatmulHeuristicsBackendSetSwizzler
 */
typedef enum {
    NVMMH_SWIZZLER_GENERIC, /**< Some unspecified and generic CTA swizzling method. */
    NVMMH_SWIZZLER_NVFUSER, /**< CTA swizzling method used in nvFuser */
    NVMMH_SWIZZLER_CUTLASS, /**< CTA swizzling method used in CUTLASS */
    NVMMH_SWIZZLER_TRITON,  /**< CTA swizzling method used in Triton */
    NVMMH_SWIZZLER_END,     /**< End Marker */
} nvmmhSwizzlerKind_t;


/**
 * Allows to specify the backend property to read or write.
 */
typedef enum {
    NVMMH_BACKEND_PROP_HAS_SLICE_K = 0, /**< Boolean, int32_t. Indicates whether the backend supports slice-k. If there's no slice-k, then Cta.K must be equal to Warp.k. */
    NVMMH_BACKEND_PROP_HAS_COL_MAJOR_RASTER = 1, /**< Boolean, int32_t. Indicates whether the backend supports col-major rasterization order. */
    NVMMH_BACKEND_PROP_REQUIRES_WARP_CONFIG =
            2, /**< Boolean, int32_t. Indicates whether the backend takes into account the specific warp configuration, Otherwise we assume it only requires a number of warp.*/
    NVMMH_BACKEND_PROP_SUPPORTS_CLUSTER_CONFIG = 3, /**< Boolean, int32_t. Indicates whether the backend supports thread block clusters. sm90+. */
    NVMMH_BACKEND_PROP_HIGH_SMEM_ALIGNMENT = 4,     /**< Boolean, int32_t. Indicates whether nvMatmulHeuristics needs to assume high alignment for shared memory allocations. */
    NVMMH_BACKEND_PROP_SMEM_EPILOGUE = 5,           /**< Boolean, int32_t. Indicates whether the backend has a shared-memory epilogue. This is for nvFuser. */
    NVMMH_BACKEND_PROP_SPLIT_K_KIND = 6,            /**< @ref nvmmhSplitKKind_t, int32_t. Indicates the backends' split-k kind, */
    NVMMH_BACKEND_PROP_CTA_SWIZZLER_BUILTIN_KIND =
            7, /**< @ref nvmmhSwizzlerKind_t, int32_t. Indicates which swizzling method nvMatmulHeuristics must choose. This setting will be overridden by the use of @ref nvMatmulHeuristicsBackendSetSwizzler. */
    NVMMH_BACKEND_PROP_WORKSPACE_SIZE = 8,           /**< int32_t workspace size for parallel split-k and such */
    NVMMH_BACKEND_PROP_DISABLE_FAST_ACC_FOR_FP8 = 9, /**< int32_t If set, disable fast accumulation for FP8 kernels */
    NVMMH_BACKEND_PROP_SUPPORTS_FALLBACK_CLUSTER =
            10,                                     /**< int32_t Whether the kernel supports fallback thread block cluster, when used in combination with preferred cluster sizes */
    NVMMH_BACKEND_PROP_SUPPORTS_ODD_CLUSTER_N = 11, /**< int32_t Whether the kernel supports odd cluster n value */
    NVMMH_BACKEND_PROP_EPILOGUE_REGISTERS = 12,     /**< int32_t A positive integer that represents how many registers are used by the epilogue part of the kernel */
    NVMMH_BACKEND_PROP_CTA_TILE_M_DIV_REQUIREMENT = 13, /**< int32_t A positive integer that specifies that CTA tile M dimension must be divisible by a provided number */
    NVMMH_BACKEND_PROP_CTA_TILE_N_DIV_REQUIREMENT = 14, /**< int32_t A positive integer that specifies that CTA tile N dimension must be divisible by a provided number */
    NVMMH_BACKEND_PROP_SMEM_CARVEOUT_SIZE =
            15, /**< int32_t A positive integer that specifies the size of the SMEM carveout in bytes (e.g. to specify SMEM requirement for epilogue). */

    NVMMH_BACKEND_PROP_END = 16, /**< End Marker */
    //NVMMH_BACKEND_PROP_OUT_OF_PLACE_BETA = 9,              /**< Boolean, int32_t */
} nvmmhBackendProperty_t;


/**
 * Sets a backend property.
 * @param backend Pointer to the backend configuration.
 * @param property @ref nvmmhBackendProperty_t The property to set.
 * @param inputBuffer Pointer to the input value that we want to set.
 * @param bufferSize Size of the input value, in bytes.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendSetValueProperty(nvmmhBackend_t NVMMH_NONNULL backend, nvmmhBackendProperty_t property,
                                                                                     const void* NVMMH_NONNULL inputBuffer, unsigned bufferSize);


/**
 * Reads a backend property.
 * @param backend Pointer to the backend configuration.
 * @param property @ref nvmmhBackendProperty_t The property to read.
 * @param inputBuffer Pointer to the buffer where to store the read value.
 * @param bufferSize Size of the buffer, in bytes.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendGetProperty(nvmmhBackend_t NVMMH_NONNULL backend, nvmmhBackendProperty_t property,
                                                                                void* NVMMH_NONNULL inputBuffer, unsigned bufferSize);

/**
 * Callback kind.
 */
typedef enum {
    NVMMH_CALLBACK_KERNEL_ADDITIONAL_VALIDITY_CHECK = 0, /**< Extra kernel validity check that that will be called by nvMatmulHeuristics when required */
    NVMMH_CALLBACK_SHARED_MEMORY_USAGE = 1,              /**< Callback that returns the amount of shared memory used by the block, in bytes */
    NVMMH_CALLBACK_CONCURRENT_CTAS =
            2, /**< Callback that returns the number of concurrent CTAs that can be scheduled on an SM. The goal of this is to capture the register and shared memory pressure. */
    NVMMH_CALLBACK_END = 3, /**< End Marker */
} nvmmhBackendPropertyCallbackKind_t;

/**
 * Callback called by nvMatmulHeuristics.
 * @param kernelConfig The kernel configuration.
 * @return An `int` whose meaning depends on the @ref nvmmhBackendPropertyCallbackKind_t property.
 */
typedef int (*nvmmhPropertyCallback_t)(const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfig);

/**
 * Sets a callback property for the backend. 
 * This can be used for example to supply custom methods such as validity checks.
 * @param backend Pointer to the backend configuration.
 * @param property @ref nvmmhBackendPropertyCallbackKind_t Callback that we want to define.
 * @param callback Function pointer of type @ref nvmmhPropertyCallback_t.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendSetCallbackProperty(nvmmhBackend_t NVMMH_NONNULL backend, nvmmhBackendPropertyCallbackKind_t property,
                                                                                        nvmmhPropertyCallback_t NVMMH_NULLABLE callback);


/**
 * A tuple of three int32_t elements.
 */
typedef struct {
    int32_t x; /**< x */
    int32_t y; /**< y */
    int32_t z; /**< z */
} nvmmhDim3_t;

/**
 * Description of the CTA swizzling mode.
 */
typedef struct {
    uint32_t ctaOrder : 8;     /**< ctaOrder */
    uint32_t ctaSwizzling : 8; /**< ctaSwizzling */
} nvmmhSwizzling_t;


/**
 * A callback describing the CTA swizzling mode.
 * @param blockIdx Current block index on the GPU.
 * @param timestamp Iteration of the main loop. Used to figure out which tiles across K dimension are processed.
 * @param problem Problem.
 * @param kernelConfig Kernel configuration.
 * @return Coordinates of the processed output tile and the "depth" of the reduction. depth refers to the K position. Return {-1,-1,-1} to indicate end of gpu block.
 */
typedef nvmmhDim3_t (*nvmmhSwizzler_t)(nvmmhDim3_t blockIdx, int timestamp, const nvmmhMatmulProblem_t* NVMMH_NONNULL problem,
                                       const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfig);

/**
 * A callback computing the dimensions of the grid launched on the GPU.
 * @param problem Problem.
 * @param kernelConfig Kernel configuration.
 * @return The dimensions of the grid launched on the GPU.
 */
typedef nvmmhDim3_t (*nvmmhGridLauncher_t)(const nvmmhMatmulProblem_t* NVMMH_NONNULL problem, const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfig);


/**
 * Sets a callback to override the default swizzling method or method defined using @ref NVMMH_BACKEND_PROP_CTA_SWIZZLER_BUILTIN_KIND.
 * @param backend Pointer to the backend configuration.
 * @param swizzler Pointer to the swizzler callback.
 * @param gridLauncher Pointer to the grid launcher callback.
 * @param supportedConfigs Pointer to an array of @ref nvmmhSwizzling_t.
 * @param supportedConfigsCount Number of elements in the supportedConfigs array.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendSetSwizzler(nvmmhBackend_t NVMMH_NONNULL backend, nvmmhSwizzler_t NVMMH_NULLABLE swizzler,
                                                                                nvmmhGridLauncher_t NVMMH_NULLABLE gridLauncher,
                                                                                const nvmmhSwizzling_t* NVMMH_NULLABLE supportedConfigs, unsigned supportedConfigsCount);


/**
 * Callback to override the internal performance model estimates in a few select places, primarily for perf-model based auto-tuning and split-k computation.
 * 
 * @param problem The matmul problem
 * @param kernelConfig Pointer to the currently tested kernel configuration.
 * @param nvMatmulHeuristics_internal_timing_model_prediction Expected timing by nvMatmulHeuristics in seconds.
 * @return Timing in seconds.
 */
typedef double (*nvmmhPerformanceModel_t)(const nvmmhMatmulProblem_t* NVMMH_NONNULL problem, const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfig,
                                          double nvMatmulHeuristics_internal_timing_model_prediction);

/**
 * Sets a performance model callback on the current backend. 
 * @param backend The backend to set the performance model callback on.
 * @param model_ptr A ptr to the performance model callback or NULL to disable the callback.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsBackendSetPerformanceModel(nvmmhBackend_t NVMMH_NONNULL backend, nvmmhPerformanceModel_t NVMMH_NULLABLE model_ptr);

/**
 * Flags to control heuristics behavior.
 */
typedef enum {
    NVMMH_FLAG_NONE = 0,                                      /**< No flag */
    NVMMH_FLAG_DISABLE_OPT_PIPELINE = 1 << 0,                 /**< Disables internal optimization pipeline */
    NVMMH_FLAG_REDUCE_OUTPUT_SPACE = 1 << 1,                  /**< Tries to reduce the number of different kernels generated */
    NVMMH_FLAG_REFINE_CANDIDATES_USING_TIMING_MODEL = 1 << 2, /**< Sorts and/or prune candidates using a perf */
    NVMMH_FLAG_PERF_MODEL_BASED_AUTO_TUNING =
            1
            << 3, /**< Generates A LOT of candidates internally and reorders them using the perf model, and returns only the top N requested. Should be enabled only when discovery is used. */
    NVMMH_FLAG_AUTO_TUNE_THE_PERF_MODEL = 1 << 4, /**< Secret mode that tunes the perf model to the results using extra runtimes values. Very expensive. */
    NVMMH_FLAG_MAFI_SEEDS = 1 << 5,               /**< Shmoos the CTA tiles sizes seeds in the opt pipeline */
    NVMMH_FLAG_END = 1 << 6,                      /**< End Marker. */
} nvmmhFlags_t;


/**
 * Bitmasks that can be used to select some properties of a kernel configuration. 
 */
typedef enum {
    NVMMH_KERNEL_CONFIG_PROPERTY_NONE = 0,                /**< No property */
    NVMMH_KERNEL_CONFIG_PROPERTY_CTA_TILE = 1 << 0,       /**< Refers to @ref nvmmhKernelConfiguration_t.cta */
    NVMMH_KERNEL_CONFIG_PROPERTY_WARP_TILE = 1 << 1,      /**< Refers to @ref nvmmhKernelConfiguration_t.warp */
    NVMMH_KERNEL_CONFIG_PROPERTY_INSTR_TILE = 1 << 2,     /**< Refers to @ref nvmmhKernelConfiguration_t.instr */
    NVMMH_KERNEL_CONFIG_PROPERTY_SPLIT_K = 1 << 3,        /**< Refers to @ref nvmmhKernelConfiguration_t.splitK */
    NVMMH_KERNEL_CONFIG_PROPERTY_GRID_SWIZZLE = 1 << 4,   /**< Refers to @ref nvmmhKernelConfiguration_t.gridSwizzle */
    NVMMH_KERNEL_CONFIG_PROPERTY_CTA_ORDER = 1 << 5,      /**< Refers to @ref nvmmhKernelConfiguration_t.ctaOrder */
    NVMMH_KERNEL_CONFIG_PROPERTY_CLUSTER_CONFIG = 1 << 6, /**< Refers to @ref nvmmhKernelConfiguration_t.clusterConfig */
    NVMMH_KERNEL_CONFIG_PROPERTY_LOAD_STAGES = 1 << 7,    /**< Refers to @ref nvmmhKernelConfiguration_t.loadStages */
    NVMMH_KERNEL_CONFIG_PROPERTY_SPLIT_K_MODE = 1 << 8,   /**< Refers to @ref nvmmhSplitKKind_t */
    NVMMH_KERNEL_CONFIG_PROPERTY_ALL = (1 << 9) - 1,      /**< All properties */
    NVMMH_KERNEL_CONFIG_PROPERTY_END = 1 << 9,            /**< End Marker */
    NVMMH_KERNEL_CONFIG_PROPERTY_CTA_SCHEDULING = NVMMH_KERNEL_CONFIG_PROPERTY_GRID_SWIZZLE | NVMMH_KERNEL_CONFIG_PROPERTY_CTA_ORDER |
                                                  NVMMH_KERNEL_CONFIG_PROPERTY_CLUSTER_CONFIG, /**< Compound flag to select all CTA scheduling properties */
} nvmmhKernelConfigurationPropertyMask_t;

/**
 * Heuristics entry point. 
 * If CUDA is present, the current device is used to gather device info. 
 * @warning This might initialize the CUDA context on the default device, if nvMatmulHeuristics is called before CUDA is initialized.
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param flags One or more flags from @ref nvmmhFlags_t or-ed together. 
 * @param target Gemm implementation targeted by the heuristic. 
 * @param problemIn Input problem.
 * @param kernelConfigOut Buffer where the heuristic will write its results. 
 * @param requestedConfigurations size of the output buffer. This is also used to request a certain number of kernel candidates from the heuristic (for auto-tuning, etc.).
 * @param hardwareDescriptor  Set to NULL to ignore.
 * @return Number of kernel configuration written into the buffer.
 *
 * @anchor supportedPrecisions
 * @par Supported precisions.
 * nvMatmulHeuristics APIs take as input a string describing the problem precision.
 * Each letter in the precision string corresponds to a specific data type:
 * - `H`: 16-bit real half precision floating-point
 * - `T`: 16-bit real bfloat16 floating-point
 * - `S`: 32-bit real single precision floating-point
 * - `C`: 64-bit complex number (two single precision floats)
 * - `D`: 64-bit real double precision floating-point
 * - `Z`: 128-bit complex number (two double precision floats)
 * - `B`: 8-bit real unsigned integer
 * - `I`: 32-bit real signed integer
 * - `Q`: 8-bit real floating point in E4M3 format
 * - `R`: 8-bit real floating point in E5M2 format
 * - `O`: 4-bit floating data type (FP4)
 * - `F`: Tensor Cores with TF32 compute precision
 * @par 
 * Three-letter precision strings for D += A * B + C:
 * - First letter: Precision of A & B matrix
 * - Second letter: Compute precision
 * - Third letter: Precision of C & D matrix
 * @par 
 * Five-letter precision strings for D += A * B + C)
 * - First letter: Precision of A matrix
 * - Second letter: Precision of B matrix
 * - Third letter: Precision of C matrix
 * - Fourth letter: Compute precision
 * - Fifth letter: Precision of D matrix
 * @par 
 * The following list shows some examples of supported precisions:
 * - "BSS"
 * - "BSB"
 * - "BII"
 * - "HSS"
 * - "HSH"
 * - "HHH"
 * - "TST"
 * - "TSS"
 * - "SFS"
 * - "SSS"
 * - "DDD"
 * - "CCC"
 * - "ZZZ"
 * - "QQTST"
 * - "QQTSQ"
 * - "QQSSS"
 * - "QRTST"
 * - "QRTSQ"
 * - "QRTSR"
 * - "RQTSR"
 * - "RQSSS"
 * - "QQHSH"
 * - "QRHSH"
 * - "RQHSH"
 * - "QQHSQ"
 * - "QRHSQ"
 * - "QRHSR"
 * - "RQHSQ"
 * - "RQHSR"
 * - "QRSSS"
 * - "RQTST"
 * - "RQTSQ"
 * - "RQTSR"
 * - "RQSSS"
 * - "QQHSH"
 * - "QRHSH"
 * - "RQHSH"
 * - "QQHSQ"
 * - "QRHSQ"
 * - "QRHSR"
 * - "RQHSQ"
 * - "RQHSR"
 * - "OOTST"
 * - "OOTSO"
 * - "OOHSH"
 * - "OOHSO"
 * - "OOSSS"
 *
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetGemmConfig(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision, unsigned flags,
                                                                      nvmmhTarget_t target, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                      nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigOut, unsigned requestedConfigurations,
                                                                      nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * Heuristics entry point. 
 * If CUDA is present, the current device is used to gather device info. 
 * @warning This might initialize the CUDA context on the default device, if nvMatmulHeuristics is called before CUDA is initialized
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param flags One or more flags from @ref nvmmhFlags_t or-ed together. 
 * @param backend User-defined backend.
 * @param problemIn Input problem.
 * @param kernelConfigOut Buffer where the heuristic will write its results. 
 * @param requestedConfigurations size of the output buffer. This is also used to request a certain number of kernel candidates from the heuristic (for auto-tuning, etc.).
 * @param hardwareDescriptor  Set to NULL to ignore.
 * @return Number of kernel configuration written into the buffer. 
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetGemmConfigEx(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision, unsigned flags,
                                                                        nvmmhBackend_t NVMMH_NONNULL backend, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                        nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigOut, unsigned requestedConfigurations,
                                                                        nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * @warning Experimental.
 *
 * Runs the heuristic and finds the closest kernel from the allow list 
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions". 
 * @param flags One or more flags from @ref nvmmhFlags_t or-ed together. 
 * @param target Gemm implementation targeted by the heuristic. 
 * @param problemsIn Input problems.
 * @param kernelConfigAllowListIn Pointer to an array of @ref nvmmhKernelConfiguration_t.
 * @param allowListEltCount Number of elements in the kernelConfigAllowListIn array.
 * @param selectedKernelConfigIndicesOut Pointer to an array of indices of the selected kernel configurations.
 * @param reqConfigCount Number of kernel configurations to select.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsGetGemmConfigWithBounds(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision, unsigned flags,
                                                                                     nvmmhTarget_t target, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemsIn,
                                                                                     const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigAllowListIn,
                                                                                     unsigned allowListEltCount, int* NVMMH_NONNULL selectedKernelConfigIndicesOut,
                                                                                     unsigned reqConfigCount, nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * @warning Experimental.
 *
 * Starts the heuristics with the user-supplied kernel configuration. 
 * @see nvMatmulHeuristicsGetGemmConfig
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions". 
 * @param flags One or more flags from @ref nvmmhFlags_t or-ed together. 
 * @param target Gemm implementation targeted by the heuristic. 
 * @param problemIn Input problem.
 * @param kernelConfigInOut Buffer where the heuristic will write its results. 
 * @param propertyAllowMask XOR-ed nvMatmulHeuristicsKernelConfigurationPropertyMasks that indicate which kernel config settings can be optimized.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsOptimizeGemmConfig(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision, unsigned flags,
                                                                                nvmmhTarget_t target, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                                nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigInOut, unsigned propertyAllowMask,
                                                                                nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * @warning Experimental.
 *
 * Starts the heuristics with the user-supplied kernel configuration. 
 * @see nvMatmulHeuristicsGetGemmConfig
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions". 
 * @param flags One or more flags from @ref nvmmhFlags_t or-ed together. 
 * @param backend Backend.
 * @param problemIn Input problem.
 * @param kernelConfigInOut Buffer where the heuristic will write its results. 
 * @param propertyAllowMask XOR-ed nvMatmulHeuristicsKernelConfigurationPropertyMasks that indicate which kernel config settings can be optimized.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsOptimizeGemmConfigEx(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr, unsigned flags,
                                                                                  nvmmhBackend_t NVMMH_NONNULL backend, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                                  nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigInOut, unsigned propertyAllowMask,
                                                                                  nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);


/**
 * Formats the kernel configuration into a null-terminated string and writes it into the output buffer. 
 * Writes up to bufferSize bytes (null terminator included).
 * If buffer is NULL and `bufferSize == 0`, the function returns the required buffer size including the null terminator.
 * @param kernelConfiguration List of configurations to convert.
 * @param outputBuffer Output buffer. 
 * @param bufferSize Buffer size, in bytes.
 * @return Number of bytes written into buffer or the required buffer length if buffer and bufferSize are NULL.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsKernelConfigurationGetString(const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfiguration,
                                                                                     char* NVMMH_NULLABLE outputBuffer, unsigned bufferSize);


/**
 * Formats the matmul problem into a null-terminated string and writes it into the output buffer. 
 * Writes up to bufferSize bytes (null terminator included).
 * If buffer is NULL and `bufferSize == 0`, the function returns the required buffer size including the null terminator.
 * @param matmulProblem List of problems to convert.
 * @param outputBuffer Output buffer.
 * @param bufferSize Buffer size, in bytes.
 * @return number of bytes written into buffer OR the required buffer length if buffer and bufferSize are NULL.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsMatmulProblemGetString(const nvmmhMatmulProblem_t* NVMMH_NONNULL matmulProblem, char* NVMMH_NULLABLE outputBuffer,
                                                                               unsigned bufferSize);


/**
 * Generates a "Constructor String" that can be used to emit nvMatmulHeuristics  API calls.
 * Output is a null-terminated string and writes it into the output buffer. 
 * Writes up to bufferSize bytes (null terminator included).
 * If buffer is NULL and `bufferSize == 0`, the function returns the required buffer size including the null terminator.
 * @param kernelConfiguration List of configurations to convert.
 * @param outputBuffer Output buffer.
 * @param bufferSize Buffer size, in bytes.
 * @return Number of bytes written into buffer or the required buffer length if buffer and bufferSize are NULL.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsKernelConfigurationToConstructorString(const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfiguration,
                                                                                               char* NVMMH_NULLABLE outputBuffer, unsigned bufferSize);


/**
 * Generates a "Constructor String" that can be used to emit nvMatmulHeuristics API calls.
 * Output is a null-terminated string and writes it into the output buffer. 
 * Writes up to bufferSize bytes (null terminator included).
 * If buffer is NULL and `bufferSize == 0`, the function returns the required buffer size including the null terminator.
 * @param matmulProblem List of problems to convert.
 * @param outputBuffer Output buffer.
 * @param bufferSize Buffer size, in bytes.
 * @return Number of bytes written into buffer or the required buffer length if buffer and bufferSize are NULL.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsMatmulProblemToConstructorString(const nvmmhMatmulProblem_t* NVMMH_NONNULL matmulProblem, char* NVMMH_NULLABLE outputBuffer,
                                                                                         unsigned bufferSize);

/**
 * Returns a set of problems and kernels to be executed by the target implementation. 
 * Each problem must be executed with the matching kernel. 
 * The benchmark must be re-done on each kernel implementation, backend, GPU and clocks. 
 * This is optional. 
 * 
 * On multi-device systems, this needs to be executed on each device. The device used is the one returned by `cudaGetDevice()`.
 * 
 * If outConfigs, outProblems and bufferSize are NULL, then the required buffer size is returned.
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param target Gemm implementation targeted by the heuristic.
 * @param matmulLayout Layout of the matmul problem.
 * @param problemsOut Pointer to an array of @ref nvmmhMatmulProblem_t.
 * @param kernelConfigsOut Pointer to an array of @ref nvmmhKernelConfiguration_t.
 * @param bufferSize Number of elements in the output arrays.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return The size of the discovery set.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetDiscoverySet(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr, nvmmhTarget_t target,
                                                                        nvmmhMatmulLayout_t matmulLayout, nvmmhMatmulProblem_t* NVMMH_NULLABLE problemsOut,
                                                                        nvmmhKernelConfiguration_t* NVMMH_NULLABLE kernelConfigsOut, unsigned bufferSize,
                                                                        nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * Returns a discovery set for energy estimation.
 *
 * If outConfigs, outProblems and bufferSize are NULL, then the required buffer size is returned.
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param target Gemm implementation targeted by the heuristic.
 * @param matmulLayout Layout of the matmul problem.
 * @param problemsOut Pointer to an array of @ref nvmmhMatmulProblem_t.
 * @param kernelConfigsOut Pointer to an array of @ref nvmmhKernelConfiguration_t.
 * @param bufferSize Number of elements in the output arrays.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return The size of the discovery set.
 */
NVMMH_NODISCARD unsigned NVMMH_WINAPI nvMatmulHeuristicsGetEnergyDiscoverySet(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr, nvmmhTarget_t target,
                                                                              nvmmhMatmulLayout_t matmulLayout, nvmmhMatmulProblem_t* NVMMH_NULLABLE problemsOut,
                                                                              nvmmhKernelConfiguration_t* NVMMH_NULLABLE kernelConfigsOut, unsigned bufferSize,
                                                                              nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);


/**
 * Send the results back to nvMatmulHeuristics for processing. 
 * On multi-device systems, this needs to be executed on each device. The device used is the one returned by cudaGetDevice().
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param target will set the profile for the given target globally.
 * @param matmulLayout Layout of the matmul problem.
 * @param problemsIn Pointer to an array of @ref nvmmhMatmulProblem_t.
 * @param kernelConfigsIn Pointer to an array of @ref nvmmhKernelConfiguration_t.
 * @param runtimesIn Config runtimes. Cases where the runtime <=0 are skipped.
 * @param bufferSize Number of elements in the input arrays.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsCommitDiscoveryResults(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr,
                                                                                    nvmmhTarget_t target, nvmmhMatmulLayout_t matmulLayout,
                                                                                    const nvmmhMatmulProblem_t* NVMMH_NONNULL problemsIn,
                                                                                    const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigsIn,
                                                                                    const float* NVMMH_NONNULL runtimesIn, unsigned bufferSize,
                                                                                    nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * Send the energy discovery results back to nvMatmulHeuristics for processing and internal weights tuning.
 * On multi-device systems, this needs to be executed on each device. The device used is the one returned by cudaGetDevice().
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param target will set the profile for the given target globally.
 * @param matmulLayout Layout of the matmul problem.
 * @param problemsIn Pointer to an array of @ref nvmmhMatmulProblem_t.
 * @param kernelConfigsIn Pointer to an array of @ref nvmmhKernelConfiguration_t.
 * @param energy_joules Config energy in Joules. Cases where the energy <=0 are skipped.
 * @param bufferSize Number of elements in the input arrays.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsCommitEnergyDiscoveryResults(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision,
                                                                                          nvmmhTarget_t target, nvmmhMatmulLayout_t matmulLayout,
                                                                                          const nvmmhMatmulProblem_t* NVMMH_NONNULL problemsIn,
                                                                                          const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigsIn,
                                                                                          const float* NVMMH_NONNULL energy_joules, unsigned bufferSize,
                                                                                          nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);


/**
 * Loads internal discovery results to improve heuristics result. 
 * Needs to be called once, manually, and for each used configuration.
 * Behavior is equivalent to @ref nvMatmulHeuristicsGetDiscoverySet followed by @ref nvMatmulHeuristicsCommitDiscoveryResults, but this variant uses internal data to avoid having to run silicon benchmarks.
 * On multi-device systems, this needs to be executed on each device. The device used is the one returned by cudaGetDevice().
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param target will load and set the profile for the given target globally
 * @param matmulLayout Layout of the matmul problem.
 * @param hardwareDescriptor Set to NULL to ignore.
 * @return @ref NVMMH_STATUS_SUCCESS on success. Otherwise @ref NVMMH_STATUS_ERROR or @ref NVMMH_STATUS_PROFILE_NOT_ENTIRELY_LOADED.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsLoadInternalDiscoverySet(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr,
                                                                                      nvmmhTarget_t target, nvmmhMatmulLayout_t matmulLayout,
                                                                                      nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * Returns expected runtime in seconds.
 * Uses an internal perf-model that relies on:
 * 1 - Discovery Process
 * 2 - Runtime CUDA info
 * 3 - Internal defaults. 
 * 4 - Target/Backend information
 * 
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precision Gemm Precision. See @ref supportedPrecisions "Supported precisions". 
 * @param target Required so nvMatmulHeuristics can match the request to one of the internal profiles if the Discovery Process was used.
 * @param problemIn Input problem.
 * @param kernelConfigIn Input kernel configuration.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return Expected runtime in seconds.
 */
NVMMH_NODISCARD double NVMMH_WINAPI nvMatmulHeuristicsEstimateRuntime(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precision, nvmmhTarget_t target,
                                                                      const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                      const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigIn,
                                                                      nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);


/**
 * Silicon metrics that nvMatmulHeuristics can estimate.
 *
 * @warning These metrics are estimates used internally by the performance model and should not be 
 * treated as exact measurements of real hardware behavior. They are primarily designed for relative
 * comparisons and internal decision-making.
 * 
 * For comparing kernel performance, @ref NVMMH_METRIC_RUNTIME_RELATIVE_FAST_S is recommended over
 * @ref NVMMH_METRIC_RUNTIME_S as it is specifically tuned for relative ordering of kernels rather
 * than absolute runtime prediction. This can provide more reliable results when the goal is to 
 * determine which kernel configuration might perform better than another.
 */
typedef enum {
    NVMMH_METRIC_RUNTIME_S = 0,                /**< Runtime in seconds */
    NVMMH_METRIC_L2_HIT_RATE = 1,              /**< L2 HitRate */
    NVMMH_METRIC_COMPUTE_S = 2,                /**< Compute time */
    NVMMH_METRIC_LOAD_S = 3,                   /**< Memory load time */
    NVMMH_METRIC_STORE_S = 4,                  /**< Memory store time */
    NVMMH_METRIC_GMEM_LOAD_BYTES = 5,          /**< Bytes read from global memory */
    NVMMH_METRIC_GMEM_STORE_BYTES = 6,         /**< Bytes stored to global memory */
    NVMMH_METRIC_L2_LOAD_BYTES = 7,            /**< Bytes read from L2 */
    NVMMH_METRIC_STATIC_LATENCIES_S = 8,       /**< Static latencies (kernel launch, split-k, etc) */
    NVMMH_METRIC_SMEM_LOAD_BYTES = 9,          /**< Smem load bytes latencies  */
    NVMMH_METRIC_SMEM_STORE_BYTES = 10,        /**< Smem store bytes latencies  */
    NVMMH_METRIC_ENERGY_JOULES = 11,           /**< Gemm Energy  */
    NVMMH_METRIC_L2_FAR_LOAD_BYTES = 12,       /**< Bytes read from L2 */
    NVMMH_METRIC_EDP = 13,                     /**< EDP (NVMMH_METRIC_ENERGY_JOULES * NVMMH_METRIC_RUNTIME_S) */
    NVMMH_METRIC_RUNTIME_RELATIVE_FAST_S = 14, /**< Runtime tuned for relative comparison */
    NVMMH_METRIC_END = 15,                     /**< End Marker */
} nvmmhSiliconMetric_t;

/**
 * Estimate a silicon metric.
 * @see @ref nvMatmulHeuristicsEstimateRuntime
 * @param handle A handle output from @ref nvMatmulHeuristicsCreate.
 * @param precisionStr Gemm Precision. See @ref supportedPrecisions "Supported precisions".
 * @param backend The backend.
 * @param problemIn Input matmul problem.
 * @param kernelConfigIn Input kernel configuration.
 * @param metric What metric to estimate.
 * @param hardwareDescriptor Hardware descriptor. Set to NULL to use the current device.
 * @return The estimated metric. 0 on error.
 */
NVMMH_NODISCARD double NVMMH_WINAPI nvMatmulHeuristicsEstimateSiliconMetricEx(NVMMH_NULLABLE nvmmhHandle_t handle, const char* NVMMH_NONNULL precisionStr,
                                                                              nvmmhBackend_t NVMMH_NONNULL backend, const nvmmhMatmulProblem_t* NVMMH_NONNULL problemIn,
                                                                              const nvmmhKernelConfiguration_t* NVMMH_NONNULL kernelConfigIn, nvmmhSiliconMetric_t metric,
                                                                              nvmmhHardwareDescriptor_t NVMMH_NULLABLE hardwareDescriptor);

/**
 * Get a pointer to a symbol in the nvMatmulHeuristics shared library.
 * @param symbolName Name of the symbol to get.
 * @param pointer Pointer to the symbol.
 * @return @ref NVMMH_STATUS_SUCCESS if the operation was successful, an error code otherwise.
 */
NVMMH_NODISCARD nvmmhStatus_t NVMMH_WINAPI nvMatmulHeuristicsGetSymbolPointer(const char* NVMMH_NONNULL symbolName, void* NVMMH_NULLABLE* NVMMH_NONNULL pointer);

#ifdef __cplusplus
}
#endif

#if defined(__cplusplus) && !defined(NVMMH_NO_EXCEPTIONS)
#    include <cassert>
#    include <iostream>
namespace nvMatmulHeuristics::internal {
[[maybe_unused]] static inline void handleStatus(const nvmmhStatus_t status, char const* NVMMH_NONNULL name, char const* NVMMH_NONNULL file, const int line) {
    if (status != NVMMH_STATUS_SUCCESS) {

        std::cerr << "nvMatmulHeuristics API failed with status: " << status
#    ifndef NVMMH_RUNTIME_LOAD
                  << ", reason: " << nvMatmulHeuristicsGetStatusString(status)
#    else
                  << ", reason unavailable (you must resolve the symbol 'nvMatmulHeuristicsGetStatusString' yourself) "
#    endif
                  << ", in " << file << ':' << line << ", call: '" << name << "\'." << std::endl;
        abort();
    }
}
}   // namespace nvMatmulHeuristics::internal

#    define NVMMH_CHECK(x)                                                                                                                                                         \
        do { nvMatmulHeuristics::internal::handleStatus(x, #x, __FILE__, __LINE__); } while (0)

#endif
