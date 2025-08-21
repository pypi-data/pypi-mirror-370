from .processor import Id02BaseProcessor

try:
    from id02.acquisition.saxs_preset import ID02DahuProcessingPreset
except ImportError:
    ID02DahuProcessingPreset = None


class Id02SaxsProcessor(Id02BaseProcessor):
    DEFAULT_QUEUE = "saxs"

    def _set_up_preset(self):
        if ID02DahuProcessingPreset is None:
            raise ImportError("id02_bliss could not be imported")

        return ID02DahuProcessingPreset()
