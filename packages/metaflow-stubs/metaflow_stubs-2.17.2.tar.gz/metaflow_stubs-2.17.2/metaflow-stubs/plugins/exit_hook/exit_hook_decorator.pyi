######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.2                                                                                 #
# Generated on 2025-08-19T21:01:04.551651                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

