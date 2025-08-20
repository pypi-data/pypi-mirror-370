from ..classes.StiFileResult import StiFileResult
from .localizations.StiLocalizationResource import StiLocalizationResource
from .scripts.StiScriptResource import StiScriptResource


class StiResourcesHelper:

### Public
    
    def getResult(name: str) -> StiFileResult:
        if len(name or '') == 0:
            return StiFileResult.getError('Resource name not specified.')

        if (name.endswith('.xml')):
            return StiLocalizationResource.getResult(name)

        if (name.endswith('.js')):
            return StiScriptResource.getResult(name)
        
        return StiFileResult.getError('Unknown resource type.')
    