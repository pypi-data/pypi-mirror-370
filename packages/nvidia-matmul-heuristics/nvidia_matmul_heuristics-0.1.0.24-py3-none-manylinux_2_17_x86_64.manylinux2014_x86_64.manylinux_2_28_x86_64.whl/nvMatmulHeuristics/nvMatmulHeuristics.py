# Copyright 2025 NVIDIA Corporation. All rights reserved.
#
# NOTICE TO LICENSEE:
#
# This source code and/or documentation ("Licensed Deliverables") are
# subject to NVIDIA intellectual property rights under U.S. and
# international Copyright laws.
#
# These Licensed Deliverables contained herein is PROPRIETARY and
# CONFIDENTIAL to NVIDIA and is being provided under the terms and
# conditions of a form of NVIDIA software license agreement by and
# between NVIDIA and Licensee ("License Agreement") or electronically
# accepted by Licensee.  Notwithstanding any terms or conditions to
# the contrary in the License Agreement, reproduction or disclosure
# of the Licensed Deliverables to any third party without the express
# written consent of NVIDIA is prohibited.
#
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
# SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
# PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
# NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
# DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
# NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
# SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THESE LICENSED DELIVERABLES.
#
# U.S. Government End Users.  These Licensed Deliverables are a
# "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
# 1995), consisting of "commercial computer software" and "commercial
# computer software documentation" as such terms are used in 48
# C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
# only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
# 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
# U.S. Government End Users acquire the Licensed Deliverables with
#     only those rights set forth herein.
#
# Any use of the Licensed Deliverables in individual and commercial
# software must include, in the user documentation and internal
# comments to the code, the above Disclaimer and U.S. Government End
# Users Notice.

import ctypes
import enum
import os


class GemmConfig:
    """A GEMM kernel configuration."""

    def __init__(self):
        self.layout = None
        self.stages = None
        self.split_k = None
        self.precision = None
        self.cta_tile_m = None
        self.cta_tile_n = None
        self.cta_tile_k = None
        self.warp_tile_m = None
        self.warp_tile_n = None
        self.warp_tile_k = None
        self.instr_tile_m = None
        self.instr_tile_n = None
        self.instr_tile_k = None
        self.cluster_m = 1
        self.cluster_n = 1
        self.swizzle_factor = 1
        self.cta_order = None
        self.split_k = 1

    def __hash__(self):
        return hash((
            self.layout, self.stages, self.split_k, self.precision,  #
            self.cta_tile_m, self.cta_tile_n, self.cta_tile_k,  #
            self.warp_tile_m, self.warp_tile_n, self.warp_tile_k,  #
            self.instr_tile_m, self.instr_tile_n, self.instr_tile_k,  #
            self.cluster_m, self.cluster_n
        ))

    def __eq__(self, other):
        return (
            self.layout, self.stages, self.split_k, self.precision,  #
            self.cta_tile_m, self.cta_tile_n, self.cta_tile_k,  #
            self.warp_tile_m, self.warp_tile_n, self.warp_tile_k,  #
            self.instr_tile_m, self.instr_tile_n, self.instr_tile_k,  #
            self.cta_order, self.swizzle_factor, self.cluster_m, self.cluster_n
        ) == (
            other.layout, other.stages, other.split_k, other.precision,  #
            other.cta_tile_m, other.cta_tile_n, other.cta_tile_k,  #
            other.warp_tile_m, other.warp_tile_n, other.warp_tile_k,  #
            other.instr_tile_m, other.instr_tile_n, other.instr_tile_k,  #
            other.cta_order, other.swizzle_factor, self.cluster_m, self.cluster_n
        )

    def __str__(self):
        return f'layout({self.layout}) ' \
               f'stages({self.stages}) ' \
               f'cta({self.cta_tile_m} {self.cta_tile_n} {self.cta_tile_k}) ' \
               f'warp({self.warp_tile_m} {self.warp_tile_n} {self.warp_tile_k}) ' \
               f'instr({self.instr_tile_m} {self.instr_tile_n} {self.instr_tile_k}) ' \
               f'splitK({self.split_k}) ' \
               f'swizz({self.swizzle_factor}) ' \
               f'ctaOrder({self.cta_order}) ' \
               f'cluster({self.cluster_m} {self.cluster_n})'

    def __ne__(self, other):
        return not (self == other)


class MatmulProblem:
    """Description of a matrix multiplication problem."""

    def __init__(self):
        self.transA = False
        self.transB = False
        self.M = None
        self.N = None
        self.K = None
        self.batchSize = 1


class NvMatmulHeuristicsTarget(enum.IntEnum):
    """Enumeration of supported heuristic target libraries and frameworks."""
    GENERIC = 0
    NVFUSER = 1
    CUTLASS = 2
    TRITON = 3
    CUTLASS3 = 4
    RESERVED_1 = 5
    RESERVED_2 = 6
    END = 7


class NvMatmulHeuristicsFlags(enum.IntEnum):
    """Bit-flag options controlling nvMatmulHeuristics behavior."""
    NONE = 0
    DISABLE_OPT_PIPELINE = 1 << 0
    REDUCE_OUTPUT_SPACE = 1 << 1
    REFINE_CANDIDATES_USING_TIMING_MODEL = 1 << 2
    PERF_MODEL_BASED_AUTO_TUNING = 1 << 3
    AUTO_TUNE_THE_PERF_MODEL = 1 << 4
    MAFI_SEEDS = 1 << 5
    END = 1 << 6


class NvMatmulHeuristicsMatmulLayout(enum.IntEnum):
    """Matrix memory layout combinations for the A, B, and C operands."""
    NN_ROW_MAJOR = 0
    NT_ROW_MAJOR = 1
    TN_ROW_MAJOR = 2
    TT_ROW_MAJOR = 3
    NN_COL_MAJOR = 4
    NT_COL_MAJOR = 5
    TN_COL_MAJOR = 6
    TT_COL_MAJOR = 7
    END = 8


class NvMatmulHeuristicsSiliconMetric(enum.IntEnum):
    """Metrics that can be estimated for a given kernel/problem pair."""
    RUNTIME_S = 0
    L2_HIT_RATE = 1
    COMPUTE_S = 2
    LOAD_S = 3
    STORE_S = 4
    GMEM_LOAD_BYTES = 5
    GMEM_STORE_BYTES = 6
    L2_LOAD_BYTES = 7
    STATIC_LATENCIES_S = 8
    SMEM_LOAD_BYTES = 9
    SMEM_STORE_BYTES = 10
    ENERGY_JOULES = 11
    L2_FAR_LOAD_BYTES = 12
    EDP = 13
    RUNTIME_RELATIVE_FAST_S = 14
    END = 15


class NvMatmulHeuristicsDependencyConfiguration(enum.IntEnum):
    """How nvMatmulHeuristics links to CUDA."""
    NONE = 0
    STATIC_LINK = 1
    DYNAMIC_LINK = 2
    RUNTIME_LOAD = 3


class NvMatmulHeuristicsNvidiaGpu(enum.IntEnum):
    """Pre-defined NVIDIA GPU targets"""
    # Ampere
    A100_SXM_80GB = 8000
    A100_PCIE_80GB = 8001
    A30_PCIE = 8002
    A10_PCIE = 8003
    A40_PCIE = 8600
    RTX_3090 = 8601
    RTX_A6000 = 8602

    # Ada
    L20 = 8900
    L40 = 8901
    L40S = 8902
    L4 = 8903
    RTX_4090 = 8904
    RTX_6000_ADA = 8905

    # Hopper
    H100_SXM = 9000
    H100_PCIE = 9001
    H100_NVL = 9002
    H200_SXM = 9003
    H20_SXM = 9004

    # Blackwell
    B200 = 10000
    GB200_NVL = 10001
    GB300_NVL = 10300
    RTX_5080 = 12000
    RTX_5090 = 12001
    RTX_PRO_6000 = 12002

    END = 0xFFFFFFFF


class NvMatmulHeuristicsBackendProperty(enum.IntEnum):
    """Tunable backend properties that influence kernel selection."""
    HAS_SLICE_K = 0
    HAS_COL_MAJOR_RASTER = 1
    REQUIRES_WARP_CONFIG = 2
    SUPPORTS_CLUSTER_CONFIG = 3
    HIGH_SMEM_ALIGNMENT = 4
    SMEM_EPILOGUE = 5
    SPLIT_K_KIND = 6
    CTA_SWIZZLER_BUILTIN_KIND = 7
    WORKSPACE_SIZE = 8
    DISABLE_FAST_ACC_FOR_FP8 = 9
    SUPPORTS_FALLBACK_CLUSTER = 10
    SUPPORTS_ODD_CLUSTER_N = 11
    EPILOGUE_REGISTERS = 12
    CTA_TILE_M_DIV_REQUIREMENT = 13
    CTA_TILE_N_DIV_REQUIREMENT = 14
    SMEM_CARVEOUT_SIZE = 15
    END = 16


class NvMatmulHeuristicsBackendPropertyCallbackKind(enum.IntEnum):
    """Kinds of callback hooks a backend can expose."""
    KERNEL_ADDITIONAL_VALIDITY_CHECK = 0
    SHARED_MEMORY_USAGE = 1
    CONCURRENT_CTAS = 2
    END = 3


class NvMatmulHeuristicsSplitKKind(enum.IntEnum):
    """Split-K kind enum."""
    NONE = 0  # No support for parallelization on the reduced dimension
    IN_PLACE = 1  # In-place split-k
    OUT_OF_PLACE = 2  # Out-of-place split-k
    STREAM_K = 3  # Stream-k
    SEGMENT_K = 4  # Segment-k
    END = 5  # End Marker


WHEEL_LIB_PATH_ = os.path.join(os.path.dirname(__file__), "../nvidia/nvMatmulHeuristics/lib/libnvMatmulHeuristics.so.0")


def layoutToStr(matmulLayout: NvMatmulHeuristicsMatmulLayout):
    """Return the short string identifier corresponding to *matmulLayout*."""
    layouts = {
        NvMatmulHeuristicsMatmulLayout.NN_ROW_MAJOR: 'NN_ROW',
        NvMatmulHeuristicsMatmulLayout.NT_ROW_MAJOR: 'NT_ROW',
        NvMatmulHeuristicsMatmulLayout.TN_ROW_MAJOR: 'TN_ROW',
        NvMatmulHeuristicsMatmulLayout.TT_ROW_MAJOR: 'TT_ROW',
        NvMatmulHeuristicsMatmulLayout.NN_COL_MAJOR: 'NN_COL',
        NvMatmulHeuristicsMatmulLayout.NT_COL_MAJOR: 'NT_COL',
        NvMatmulHeuristicsMatmulLayout.TN_COL_MAJOR: 'TN_COL',
        NvMatmulHeuristicsMatmulLayout.TT_COL_MAJOR: 'TT_COL'
    }
    return layouts.get(matmulLayout)


def boolsToNvMatmulHeuristicsLayout(trans_a: bool, trans_b: bool):
    """Map boolean transpose flags to a `NvMatmulHeuristicsMatmulLayout` value."""
    if trans_a and trans_b:
        return NvMatmulHeuristicsMatmulLayout.TT_ROW_MAJOR
    elif trans_a:
        return NvMatmulHeuristicsMatmulLayout.TN_ROW_MAJOR
    elif trans_b:
        return NvMatmulHeuristicsMatmulLayout.NT_ROW_MAJOR
    else:
        return NvMatmulHeuristicsMatmulLayout.NN_ROW_MAJOR


class NvMatmulHeuristicsInterface:
    """Python wrapper of the nvMatmulHeuristics C API."""

    class nvmmhKernelConfiguration(ctypes.Structure):
        _fields_ = [
            ("cta", ctypes.c_uint16 * 3),
            ("warp", ctypes.c_uint16 * 3),
            ("instr", ctypes.c_uint16 * 3),
            ("splitK", ctypes.c_uint16),
            ("loadStages", ctypes.c_uint8),
            ("gridSwizzle", ctypes.c_uint8),
            ("ctaOrder", ctypes.c_uint8),
            ("cluster", ctypes.c_uint8 * 2)
        ]

    class nvmmhMatmulProblem(ctypes.Structure):
        _fields_ = [
            ("M", ctypes.c_uint32),
            ("N", ctypes.c_uint32),
            ("K", ctypes.c_uint32),
            ("batchSize", ctypes.c_uint32),
            ("matmulLayout", ctypes.c_uint8),
        ]

        def asGemmProblem(self):
            problem = MatmulProblem()
            problem.M = self.M
            problem.N = self.N
            problem.K = self.K
            problem.transA = self.matmulLayout == NvMatmulHeuristicsMatmulLayout.TN_ROW_MAJOR or self.matmulLayout == NvMatmulHeuristicsMatmulLayout.TT_ROW_MAJOR
            problem.transB = self.matmulLayout == NvMatmulHeuristicsMatmulLayout.NT_ROW_MAJOR or self.matmulLayout == NvMatmulHeuristicsMatmulLayout.TT_ROW_MAJOR
            problem.batchSize = self.batchSize
            return problem

        def __str__(self):
            return f"M: {self.M}, N: {self.N}, K: {self.K}, batchSize: {self.batchSize}, matmulLayout: {layoutToStr(self.matmulLayout)}"

    class nvmmhHardwareDescriptor(ctypes.Structure):
        _fields_ = [("data", ctypes.c_uint64 * 8)]  # Opaque structure

    class nvmmhBackend(ctypes.Structure):
        _fields_ = [("data", ctypes.c_uint64 * 8)]  # Opaque structure

    def __init__(self, backend: NvMatmulHeuristicsTarget = NvMatmulHeuristicsTarget.GENERIC, precision: str = 'HSS', path: str = None,
                 flags: NvMatmulHeuristicsFlags = NvMatmulHeuristicsFlags.NONE):
        lib = ctypes.CDLL(path if path is not None else WHEEL_LIB_PATH_, mode=ctypes.RTLD_GLOBAL)

        major = lib.nvMatmulHeuristicsGetVersionMajor()
        minor = lib.nvMatmulHeuristicsGetVersionMinor()
        patch = lib.nvMatmulHeuristicsGetVersionPatch()
        assert major == 0
        assert minor == 1
        assert patch == 0

        self.nvMatmulHeuristicsCreate = lib.nvMatmulHeuristicsCreate
        self.nvMatmulHeuristicsDestroy = lib.nvMatmulHeuristicsDestroy

        self.nvMatmulHeuristicsGetGemmConfig = lib.nvMatmulHeuristicsGetGemmConfig
        self.nvMatmulHeuristicsGetGemmConfigEx = lib.nvMatmulHeuristicsGetGemmConfigEx

        self.nvMatmulHeuristicsEstimateSiliconMetricEx = lib.nvMatmulHeuristicsEstimateSiliconMetricEx
        self.nvMatmulHeuristicsEstimateSiliconMetricEx.restype = ctypes.c_double

        self.nvMatmulHeuristicsGetDiscoverySet = lib.nvMatmulHeuristicsGetDiscoverySet
        self.nvMatmulHeuristicsCommitDiscoveryResults = lib.nvMatmulHeuristicsCommitDiscoveryResults
        self.nvMatmulHeuristicsLoadInternalDiscoverySet = lib.nvMatmulHeuristicsLoadInternalDiscoverySet

        self.nvMatmulHeuristicsEstimateRuntime = lib.nvMatmulHeuristicsEstimateRuntime
        self.nvMatmulHeuristicsEstimateRuntime.restype = ctypes.c_double

        self.nvMatmulHeuristicsClearInternalState = lib.nvMatmulHeuristicsClearInternalState

        self.nvMatmulHeuristicsGetDependencyConfiguration = lib.nvMatmulHeuristicsGetDependencyConfiguration
        self.nvMatmulHeuristicsHardwareDescriptorCreate = lib.nvMatmulHeuristicsHardwareDescriptorCreate
        self.nvMatmulHeuristicsHardwareDescriptorDestroy = lib.nvMatmulHeuristicsHardwareDescriptorDestroy
        self.nvMatmulHeuristicsHardwareDescriptorSetPredefinedGpu = lib.nvMatmulHeuristicsHardwareDescriptorSetPredefinedGpu

        self.nvMatmulHeuristicsBackendSetValueProperty = lib.nvMatmulHeuristicsBackendSetValueProperty
        self.nvMatmulHeuristicsBackendGetProperty = lib.nvMatmulHeuristicsBackendGetProperty
        self.nvMatmulHeuristicsBackendSetCallbackProperty = lib.nvMatmulHeuristicsBackendSetCallbackProperty

        self.nvMatmulHeuristicsBackendCreate = lib.nvMatmulHeuristicsBackendCreate
        self.nvMatmulHeuristicsBackendDestroy = lib.nvMatmulHeuristicsBackendDestroy

        self.precision = precision
        self.target = backend
        self.flags = flags
        self.lib = lib

        self.nullptr = ctypes.POINTER(ctypes.c_long)()
        self.handle = ctypes.c_void_p()

        self.nvMatmulHeuristicsCreate(ctypes.byref(self.handle))

    def __del__(self):
        if self.handle:
            self.nvMatmulHeuristicsDestroy(ctypes.byref(self.handle))

    def resetLibraryState(self):
        """Reset the library state and create a new handle."""
        if self.handle:
            self.nvMatmulHeuristicsDestroy(ctypes.byref(self.handle))
        self.nvMatmulHeuristicsCreate(ctypes.byref(self.handle))

    def get(self, problem: nvmmhMatmulProblem, count: int,
            hardware_descriptor=None):
        """Get GEMM configurations using a problem object.
        
        Args:
            - problem: nvmmhMatmulProblem object
            - count: Number of configurations to retrieve
            - hardware_descriptor: Optional hardware descriptor
        """
        flags = ctypes.c_int(self.flags)
        target = ctypes.c_int(self.target)
        output_type = self.nvmmhKernelConfiguration * count
        output = output_type()

        returned_count = self.nvMatmulHeuristicsGetGemmConfig(
            self.handle,
            self.precision.encode('ascii'),
            flags,
            target,
            ctypes.byref(problem),
            output,
            count,
            hardware_descriptor if hardware_descriptor else self.nullptr
        )

        output_configs = list()
        for i in range(returned_count):
            kernelConfig = self.unpackGemmConfig(output[i])
            kernelConfig.layout = layoutToStr(problem.matmulLayout)
            try:
                estimatedRuntime = self.nvMatmulHeuristicsEstimateRuntime(
                    self.handle,
                    self.precision.encode('ascii'),
                    target,
                    ctypes.byref(problem),
                    ctypes.byref(output[i]),
                    hardware_descriptor if hardware_descriptor else self.nullptr
                )
            except Exception as e:
                print(f"Error estimating runtime: {e}")
                estimatedRuntime = 0.0
            output_configs.append({
                "kernel": kernelConfig,
                "problem": problem.asGemmProblem(),
                "nvmmhMatmulProblem": problem,
                "runtime": estimatedRuntime,
                "nvmmhKernelConfiguration": output[i]
            })
        return output_configs

    def get_with_mnk(self, m: int, n: int, k: int, matmulLayout: NvMatmulHeuristicsMatmulLayout,
                     count: int, hardware_descriptor=None):
        """Get GEMM configurations using problem dimensions.
        
        Args:
            - m: Output matrix height
            - n: Output matrix width
            - k: Reduced dimension
            - matmulLayout: Matrix layout
            - count: Number of configurations to retrieve
            - hardware_descriptor: Optional hardware descriptor
        """
        problem = self.makeNvMatmulHeuristicsProblem(m, n, k, matmulLayout)
        return self.get(problem, count, hardware_descriptor)

    def unpackGemmConfig(self, output: nvmmhKernelConfiguration):
        """Convert a C kernel-configuration struct into a Python `GemmConfig`."""
        kernelConfig = GemmConfig()
        kernelConfig.split_k = output.splitK
        kernelConfig.swizzle_factor = output.gridSwizzle
        kernelConfig.cta_order = output.ctaOrder
        kernelConfig.stages = output.loadStages
        kernelConfig.precision = self.precision
        kernelConfig.cta_tile_m = output.cta[0]
        kernelConfig.cta_tile_n = output.cta[1]
        kernelConfig.cta_tile_k = output.cta[2]
        kernelConfig.warp_tile_m = output.warp[0]
        kernelConfig.warp_tile_n = output.warp[1]
        kernelConfig.warp_tile_k = output.warp[2]
        kernelConfig.instr_tile_m = output.instr[0]
        kernelConfig.instr_tile_n = output.instr[1]
        kernelConfig.instr_tile_k = output.instr[2]
        kernelConfig.cluster_m = output.cluster[0]
        kernelConfig.cluster_n = output.cluster[1]
        return kernelConfig

    def getDiscoverySet(self, matmulLayout: NvMatmulHeuristicsMatmulLayout):
        """Return the discovery set for the requested matrix layout."""
        target = ctypes.c_int(self.target)
        layout = ctypes.c_int(matmulLayout)
        setSize = self.nvMatmulHeuristicsGetDiscoverySet(self.handle, self.precision.encode('ascii'), target, layout, self.nullptr, self.nullptr, 0, self.nullptr)
        kernelConfigs = (self.nvmmhKernelConfiguration * setSize)()
        problems = (self.nvmmhMatmulProblem * setSize)()
        returned_count = self.nvMatmulHeuristicsGetDiscoverySet(self.handle, self.precision.encode('ascii'), target, layout, problems, kernelConfigs, setSize, self.nullptr)
        output_configs = list()

        for i in range(returned_count):
            kernelConfig = self.unpackGemmConfig(kernelConfigs[i])
            kernelConfig.layout = layoutToStr(matmulLayout)
            output_configs.append(
                {"kernel": kernelConfig, "problem": problems[i].asGemmProblem(), "nvmmhMatmulProblem": problems[i], "runtime": 0.0, "nvmmhKernelConfiguration": kernelConfigs[i]})
        return output_configs

    def commitDiscoverySet(self, dicts, matmulLayout: NvMatmulHeuristicsMatmulLayout):
        """Upload measured discovery-set runtimes to refine heuristics."""
        setSize = len(dicts)

        kernelConfigs = (self.nvmmhKernelConfiguration * setSize)()
        problems = (self.nvmmhMatmulProblem * setSize)()
        runtimes = (ctypes.c_float * setSize)()
        target = ctypes.c_int(self.target)
        layout = ctypes.c_int(matmulLayout)

        for i in range(setSize):
            kernelConfigs[i] = dicts[i]["nvmmhKernelConfiguration"]
            problems[i] = dicts[i]["nvmmhMatmulProblem"]
            runtimes[i] = dicts[i]["runtime"]

        self.nvMatmulHeuristicsCommitDiscoveryResults(self.handle, self.precision.encode('ascii'), target, layout, problems, kernelConfigs, runtimes, setSize, self.nullptr)

    def loadInternalDiscoverySet(self, matmulLayout: NvMatmulHeuristicsMatmulLayout, hardware_descriptor=None) -> bool:
        """Load internal discovery set for a specific matrix multiplication layout.
        
        Args:
            - matmulLayout: The matrix multiplication layout to load discovery set for
            - hardware_descriptor: Optional hardware descriptor
            
        Returns:
            True if the discovery set was successfully loaded, False otherwise
        """
        target = ctypes.c_int(self.target)
        layout = ctypes.c_int(matmulLayout)
        res = self.nvMatmulHeuristicsLoadInternalDiscoverySet(
            self.handle,
            self.precision.encode('ascii'),
            target,
            layout,
            hardware_descriptor if hardware_descriptor else self.nullptr
        )
        return res != 0

    def estimateSiliconMetric(self, problem, kernel_config, metric: NvMatmulHeuristicsSiliconMetric,
                              hardware_descriptor=None):
        """Estimate silicon metrics for a given problem and kernel configuration.
        
        Args:
            - problem: Problem configuration
            - kernel_config: Kernel configuration
            - metric: Silicon metric to estimate
            - hardware_descriptor: Optional hardware descriptor
        """
        target = ctypes.c_int(self.target)
        metric_val = ctypes.c_int(metric)
        return self.nvMatmulHeuristicsEstimateSiliconMetricEx(
            self.handle,
            self.precision.encode('ascii'),
            target,
            ctypes.byref(problem),
            ctypes.byref(kernel_config),
            metric_val,
            hardware_descriptor if hardware_descriptor else self.nullptr
        )

    def createHardwareDescriptor(self):
        """Creates a hardware descriptor"""
        descriptor = ctypes.POINTER(self.nvmmhHardwareDescriptor)()
        status = self.nvMatmulHeuristicsHardwareDescriptorCreate(ctypes.byref(descriptor))
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to create hardware descriptor, status: {status}")
        return descriptor

    def destroyHardwareDescriptor(self, descriptor):
        """Destroys a hardware descriptor"""
        if descriptor:
            self.nvMatmulHeuristicsHardwareDescriptorDestroy(ctypes.byref(descriptor))

    def setHardwarePredefinedGpu(self, descriptor, gpu: NvMatmulHeuristicsNvidiaGpu):
        """Sets the hardware descriptor to a predefined GPU configuration"""
        status = self.nvMatmulHeuristicsHardwareDescriptorSetPredefinedGpu(descriptor, ctypes.c_int(gpu))
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to set predefined GPU, status: {status}")

    def getDependencyConfiguration(self) -> NvMatmulHeuristicsDependencyConfiguration:
        """Gets CUDA and cuBLAS dependency configuration"""
        has_cuda = ctypes.c_int()
        status = self.nvMatmulHeuristicsGetDependencyConfiguration(ctypes.byref(has_cuda))
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to get dependency configuration, status: {status}")
        return NvMatmulHeuristicsDependencyConfiguration(has_cuda.value)

    def makeNvMatmulHeuristicsProblem(self, m: int, n: int, k: int, matmulLayout: NvMatmulHeuristicsMatmulLayout, batch_size: int = 1):
        """Create a C problem struct from Python dimension arguments."""
        problem = self.nvmmhMatmulProblem()
        problem.M = ctypes.c_uint32(m)
        problem.N = ctypes.c_uint32(n)
        problem.K = ctypes.c_uint32(k)
        problem.batchSize = ctypes.c_uint32(batch_size)
        problem.matmulLayout = ctypes.c_uint8(matmulLayout)
        return problem

    def setBackendValueProperty(self, backend, property: NvMatmulHeuristicsBackendProperty,
                                value: bytes, value_size: int) -> bool:
        """
        Sets a backend value property.
    
        Args:
            - backend: Backend object (ctypes.POINTER(self.nvmmhBackend))
            - property: Property to set
            - value: Value to set
            - value_size: Size of the value
        """
        status = self.nvMatmulHeuristicsBackendSetValueProperty(
            backend,  # Already a pointer, no need for byref
            ctypes.c_int(property),
            value,
            ctypes.c_uint(value_size)
        )
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to set backend property, status: {status}")
        return True

    def getBackendProperty(self, backend,
                           property: NvMatmulHeuristicsBackendProperty,
                           buffer: bytes,
                           buffer_size: int) -> int:
        """Gets a backend property.
        
        Args:
            - backend: Backend object (ctypes.POINTER(self.nvmmhBackend))
            - property: Property to get
            - buffer: Buffer to store the property value
            - buffer_size: Size of the buffer
            
        Returns:
            Status code
        """
        return self.nvMatmulHeuristicsBackendGetProperty(
            backend,
            ctypes.c_int(property),
            buffer,
            ctypes.c_uint(buffer_size)
        )

    def setBackendCallbackProperty(self, backend: nvmmhBackend,
                                   callback_kind: NvMatmulHeuristicsBackendPropertyCallbackKind,
                                   callback) -> bool:
        """Sets a backend callback property.
        
        Args:
            - backend: Backend object
            - callback_kind: Type of callback
            - callback: Callback function
            
        Returns:
            True if successful
        """
        # Create C-compatible callback
        CALLBACK_TYPE = ctypes.CFUNCTYPE(
            ctypes.c_int,  # return type
            ctypes.POINTER(self.nvmmhKernelConfiguration),  # kernel config
            ctypes.POINTER(self.nvmmhMatmulProblem),  # problem
        )

        c_callback = CALLBACK_TYPE(callback) if callback else None

        status = self.nvMatmulHeuristicsBackendSetCallbackProperty(
            backend,
            ctypes.c_int(callback_kind),
            c_callback
        )
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to set backend callback, status: {status}")

        # Store callback reference to prevent garbage collection
        if not hasattr(self, '_callbacks'):
            self._callbacks = {}
        self._callbacks[callback_kind] = c_callback

        return True

    def getBackendStringProperty(self, backend: nvmmhBackend,
                                 property: NvMatmulHeuristicsBackendProperty) -> str:
        """Helper method to get string properties.
        
        Args:
            _ backend: Backend object
            _ property: Property to get
            
        Returns:
            Property value as string
        """
        # First get required buffer size
        size = self.getBackendProperty(backend, property, None, 0)
        if size <= 0:
            return ""

        # Allocate buffer and get property
        buffer = ctypes.create_string_buffer(size)
        actual_size = self.getBackendProperty(backend, property, buffer, size)

        if actual_size <= 0:
            return ""

        return buffer.value.decode('utf-8')

    def getEx(self, problem: nvmmhMatmulProblem, count: int,
              backend, hardware_descriptor=None):
        """
        Get GEMM configurations using a problem object and custom backend.

        Args:
            - problem: Problem configuration
            - count: Number of configurations to retrieve
            - backend: Backend object (ctypes.POINTER(self.nvmmhBackend))
            - hardware_descriptor: Optional hardware descriptor
        """
        flags = ctypes.c_int(self.flags)
        output_type = self.nvmmhKernelConfiguration * count
        output = output_type()

        returned_count = self.nvMatmulHeuristicsGetGemmConfigEx(
            self.handle,
            self.precision.encode('ascii'),
            flags,
            backend,  # Already a pointer, no need for byref
            ctypes.byref(problem),
            output,
            count,
            hardware_descriptor if hardware_descriptor else self.nullptr
        )

        output_configs = list()
        for i in range(returned_count):
            kernelConfig = self.unpackGemmConfig(output[i])
            kernelConfig.layout = layoutToStr(problem.matmulLayout)
            try:
                estimatedRuntime = self.nvMatmulHeuristicsEstimateRuntime(
                    self.handle,
                    self.precision.encode('ascii'),
                    self.target,
                    ctypes.byref(problem),
                    ctypes.byref(output[i]),
                    hardware_descriptor if hardware_descriptor else self.nullptr
                )
            except Exception as e:
                print(f"Error estimating runtime: {e}")
                estimatedRuntime = 0.0
            output_configs.append({
                "kernel": kernelConfig,
                "problem": problem.asGemmProblem(),
                "nvmmhMatmulProblem": problem,
                "runtime": estimatedRuntime,
                "nvmmhKernelConfiguration": output[i]
            })
        return output_configs

    def createBackend(self, target: NvMatmulHeuristicsTarget):
        """Creates a backend object.
        
        Args:
            - target: Target backend type
            
        Returns:
            Backend object
        """
        backend = ctypes.POINTER(self.nvmmhBackend)()
        status = self.nvMatmulHeuristicsBackendCreate(ctypes.byref(backend), ctypes.c_int(target))
        if status != 1:  # NVMMH_STATUS_SUCCESS
            raise RuntimeError(f"Failed to create backend, status: {status}")
        return backend

    def destroyBackend(self, backend):
        """Destroys a backend object."""
        if backend:
            self.nvMatmulHeuristicsBackendDestroy(ctypes.byref(backend))


class NvMatmulHeuristicsInterfaceEx(NvMatmulHeuristicsInterface):
    """Extended version of NvMatmulHeuristicsInterface that manages discovery profiles internally
    and allows precision to be specified per-call rather than at construction time.
    """

    def __init__(self, backend: NvMatmulHeuristicsTarget = NvMatmulHeuristicsTarget.GENERIC,
                 path: str = None,
                 flags: NvMatmulHeuristicsFlags = NvMatmulHeuristicsFlags.NONE,
                 load_discovery_implicitly: bool = True,
                 gpu: NvMatmulHeuristicsNvidiaGpu = None):
        """Initialize the extended interface.

        Args:
            - backend: Target backend type
            - path: Path to nvMatmulHeuristics library
            - flags: Flags to use for operations
            - load_discovery_implicitly: Whether to automatically load discovery sets when needed
            - gpu: Optional GPU to use. If None, no GPU will be set.
        """
        # Initialize base class with a dummy precision that will be overridden
        super().__init__(backend=backend, precision='HSS', path=path, flags=flags)

        self.load_discovery_implicitly = load_discovery_implicitly
        # Dictionary to track loaded discovery sets: (target, precision, layout) -> bool
        self._loaded_discovery_sets = {}

        # Create and initialize hardware descriptor if GPU is specified
        self.hardware_descriptor = None
        if gpu is not None:
            self.hardware_descriptor = self.createHardwareDescriptor()
            self.setHardwarePredefinedGpu(self.hardware_descriptor, gpu)

    def __del__(self):
        """Clean up hardware descriptor when the object is destroyed."""
        if hasattr(self, 'hardware_descriptor') and self.hardware_descriptor is not None:
            self.destroyHardwareDescriptor(self.hardware_descriptor)
            self.hardware_descriptor = None

    def _get_discovery_key(self, target: NvMatmulHeuristicsTarget, precision: str,
                           layout: NvMatmulHeuristicsMatmulLayout) -> tuple:
        """Get the key for the discovery set cache.
        
        Args:
            - target: Target backend
            - precision: Precision string
            - layout: Matrix layout
            
        Returns:
            Tuple key for the discovery set cache
        """
        return (target, precision, layout)

    def _ensure_discovery_loaded(self, target: NvMatmulHeuristicsTarget, precision: str,
                                 layout: NvMatmulHeuristicsMatmulLayout) -> bool:
        """Ensure the discovery set is loaded for the given parameters.
        
        Args:
            - target: Target backend
            - precision: Precision string
            - layout: Matrix layout
            
        Returns:
            True if the discovery set is loaded, False otherwise
        """
        if not self.load_discovery_implicitly:
            return True

        key = self._get_discovery_key(target, precision, layout)
        if key in self._loaded_discovery_sets:
            return True

        # Try to load the discovery set
        success = self.loadInternalDiscoverySet(layout, precision)
        if success:
            self._loaded_discovery_sets[key] = True
        return success

    def loadInternalDiscoverySet(self, matmulLayout: NvMatmulHeuristicsMatmulLayout, precision: str = None) -> bool:
        """Override to track loaded discovery sets.
        
        Args:
            - matmulLayout: Matrix layout
            - hardware_descriptor: Hardware descriptor
            - precision: Optional precision override
            
        Returns:
            True if the discovery set was loaded successfully
        """
        if precision is None:
            precision = self.precision

        # Temporarily override precision for this call
        original_precision = self.precision
        self.precision = precision
        try:
            success = super().loadInternalDiscoverySet(matmulLayout, self.hardware_descriptor)
            if success:
                key = self._get_discovery_key(self.target, precision, matmulLayout)
                self._loaded_discovery_sets[key] = True
            return success
        finally:
            self.precision = original_precision

    def get(self, problem: NvMatmulHeuristicsInterface.nvmmhMatmulProblem, count: int,
            precision: str = None) -> list:
        """Get GEMM configurations with optional precision override.
        
        Args:
            - problem: Problem configuration
            - count: Number of configurations to retrieve
            - precision: Optional precision override
            
        Returns:
            List of kernel configurations
        """
        if precision is None:
            precision = self.precision

        self._ensure_discovery_loaded(self.target, precision, problem.matmulLayout)

        # Temporarily override precision for this call
        original_precision = self.precision
        self.precision = precision
        try:
            return super().get(problem, count, self.hardware_descriptor)
        finally:
            self.precision = original_precision

    def getEx(self, problem: NvMatmulHeuristicsInterface.nvmmhMatmulProblem, count: int,
              backend, precision: str = None) -> list:
        """Get GEMM configurations with custom backend and optional precision override.
        
        Args:
            - problem: Problem configuration
            - count: Number of configurations to retrieve
            - backend: Backend object
            - precision: Optional precision override
            
        Returns:
            List of kernel configurations
        """
        if precision is None:
            precision = self.precision

        self._ensure_discovery_loaded(self.target, precision, problem.matmulLayout)

        # Temporarily override precision for this call
        original_precision = self.precision
        self.precision = precision
        try:
            return super().getEx(problem, count, backend, self.hardware_descriptor)
        finally:
            self.precision = original_precision

    def estimateRuntime(self, problem: NvMatmulHeuristicsInterface.nvmmhMatmulProblem,
                        kernel_config: NvMatmulHeuristicsInterface.nvmmhKernelConfiguration,
                        precision: str = None) -> float:
        """Estimate runtime with optional precision override.
        
        Args:
            - problem: Problem configuration
            - kernel_config: Kernel configuration
            - precision: Optional precision override
            
        Returns:
            Estimated runtime in seconds
        """
        if precision is None:
            precision = self.precision

        self._ensure_discovery_loaded(self.target, precision, problem.matmulLayout)

        # Temporarily override precision for this call
        original_precision = self.precision
        self.precision = precision
        try:
            return super().estimateRuntime(problem, kernel_config, self.hardware_descriptor)
        finally:
            self.precision = original_precision

    def estimateSiliconMetric(self, problem: NvMatmulHeuristicsInterface.nvmmhMatmulProblem,
                              kernel_config: NvMatmulHeuristicsInterface.nvmmhKernelConfiguration,
                              metric: NvMatmulHeuristicsSiliconMetric,
                              precision: str = None) -> float:
        """Estimate silicon metric with optional precision override.
        
        Args:
            - problem: Problem configuration
            - kernel_config: Kernel configuration
            - metric: Metric to estimate
            - precision: Optional precision override
            
        Returns:
            Estimated metric value
        """
        if precision is None:
            precision = self.precision

        self._ensure_discovery_loaded(self.target, precision, problem.matmulLayout)

        # Temporarily override precision for this call
        original_precision = self.precision
        self.precision = precision
        try:
            return super().estimateSiliconMetric(problem, kernel_config, metric, self.hardware_descriptor)
        finally:
            self.precision = original_precision
