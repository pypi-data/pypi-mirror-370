"""
    QApp Platform Project pennylane_circuit_export_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.data.async_task.circuit_export.backend_holder import BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from quapp_common.data.response.custom_header import CustomHeader

import requests

class PyquilCircuitExportTask(CircuitExportTask):

    def __init__(self, circuit_data_holder: CircuitDataHolder,
                 backend_data_holder: BackendDataHolder,
                 project_header: CustomHeader, workspace_header: CustomHeader):
        super().__init__(circuit_data_holder, backend_data_holder,
                         project_header, workspace_header)

    def _transpile_circuit(self):
        # no implementation needed for Pyquil
        pass
        
    def do(self):
        return

