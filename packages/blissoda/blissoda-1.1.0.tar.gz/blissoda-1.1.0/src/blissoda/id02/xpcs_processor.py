from .processor import Id02BaseProcessor

try:
    from id02.acquisition.xpcs_preset import ID02DynamixProcessingPreset
except ImportError:
    ID02DynamixProcessingPreset = None


class Id02XpcsProcessor(Id02BaseProcessor):
    DEFAULT_WORKER = "xpcs"

    def _set_up_preset(self):
        if ID02DynamixProcessingPreset is None:
            raise ImportError("id02_bliss could not be imported")

        return ID02DynamixProcessingPreset()
