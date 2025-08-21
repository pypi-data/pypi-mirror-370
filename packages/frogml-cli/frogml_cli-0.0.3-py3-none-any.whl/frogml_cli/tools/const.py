from frogml._proto.qwak.batch_job.v1.batch_job_resources_pb2 import GpuType

GPU_TYPES = list(set(GpuType.DESCRIPTOR.values_by_name) - {"INVALID_GPU"})
